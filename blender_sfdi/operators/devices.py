import bpy
import json

from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from .. import devices, assets, preferences

# Characterisation Board

class OP_AddCheckerBoard(Operator):
    bl_idname = "menu.op_addcheckerboard"
    bl_label = "TODO: Write label"
    
    location    : bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation    : bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        bl_objs = set(context.selected_objects)

        assets.meshes.load_obj(preferences.ASSETS_DIR / "checker_board.obj")

        matched_bl_objs = [obj for obj in context.selected_objects if obj not in bl_objs]

        if matched_bl_objs == 0:
            # TODO: Give warning
            return None 
        
        bl_obj = matched_bl_objs[0]
        bl_obj.data[devices.BL_CharBoard.IS_BOARD_STR] = True

        # Set checkerboard pattern material
        devices.BL_CharBoard._checkerboard_shader(bl_obj.material_slots[1].material)
        
        return {'FINISHED'}

class OP_AddCircleBoard(Operator):
    bl_idname = "menu.op_addcircleboard"
    bl_label = "TODO: Write label"
    
    location    : bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation    : bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        bl_objs = set(context.selected_objects)

        assets.meshes.load_obj(preferences.ASSETS_DIR / "circle_board.obj")

        matched_bl_objs = [obj for obj in context.selected_objects if obj not in bl_objs]

        if matched_bl_objs == 0:
            # TODO: Give warning
            return None
        
        bl_obj = matched_bl_objs[0]
        bl_obj.data[devices.BL_CharBoard.IS_BOARD_STR] = True

        # Set checkerboard pattern material
        devices.BL_CharBoard._circleboard_shader(bl_obj.material_slots[1].material)
        
        return {'FINISHED'}

class OP_AddImageBoard(Operator):
    bl_idname = "menu.op_addimageboard"
    bl_label = "TODO: Write label"
    
    location    : bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation    : bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        bl_objs = set(context.selected_objects)

        assets.meshes.load_obj(preferences.ASSETS_DIR / "image_board.obj")

        matched_bl_objs = [obj for obj in context.selected_objects if obj not in bl_objs]

        if matched_bl_objs == 0:
            # TODO: Give warning
            return None
        
        bl_obj = matched_bl_objs[0]
        bl_obj.data[devices.BL_CharBoard.IS_BOARD_STR] = True

        # Set checkerboard pattern material
        devices.BL_CharBoard._imageboard_shader(bl_obj.material_slots[1].material)
        
        return {'FINISHED'}

class OP_LoadBoardPoses(bpy.types.Operator):
    bl_idname = "menu.op_loadchar_board_poses"
    bl_label = "Load Poses"

    filepath: bpy.props.StringProperty(
        name="File path",
        description="Filepath for loading",
        maxlen=1024,
        subtype='FILE_PATH'
    ) # type: ignore 
    
    filename: bpy.props.StringProperty(
        name="Filename",
        description="Name of the file",
        default="board_poses.json",
        maxlen=1024,
        subtype='FILE_NAME'
    ) # type: ignore
    
    directory: bpy.props.StringProperty(
        name="Directory",
        description="Directory for loading",
        maxlen=1024,
        subtype='DIR_PATH'
    ) # type: ignore
    
    filter_glob: bpy.props.StringProperty(
        default="*.json;",
        options={'HIDDEN'}
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        try:
            char_board = devices.BL_CharBoard.from_bl_obj(context.object)
        except ValueError:
            return False
        
        return True

    def execute(self, context):
        with open(self.filepath, "r+") as jsonfile:
            raw_json = json.load(jsonfile)

        if ("char_board" not in raw_json) or ("poses" not in raw_json["char_board"]):
            return {"CANCELLED"}
        
        char_board = devices.BL_CharBoard.from_bl_obj(context.object)
        settings = char_board.settings
        
        # Get rid of the existing transforms to load the new ones
        settings.poses.clear()

        # Add to the transforms list
        for pose in raw_json["char_board"]["poses"]:
            new_item = settings.poses.add()

            translation = pose["translation"]
            rotation = pose["rotation"]

            new_item.translation = [translation["x"], translation["y"], translation["z"]]
            new_item.rotation = [rotation["w"], rotation["x"], rotation["y"], rotation["z"]]
            
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class OP_SaveBoardPoses(bpy.types.Operator, ImportHelper):
    bl_idname = "op.save_board_poses"
    bl_label = "Save Board Poses"
    
    filepath: bpy.props.StringProperty(
        name="File path",
        description="Filepath for saving",
        maxlen=1024,
        subtype='FILE_PATH'
    ) # type: ignore 
    
    filename: bpy.props.StringProperty(
        name="Filename",
        description="Name of the file",
        default="board_poses.json",
        maxlen=1024,
        subtype='FILE_NAME'
    ) # type: ignore
    
    directory: bpy.props.StringProperty(
        name="Directory",
        description="Directory for saving",
        maxlen=1024,
        subtype='DIR_PATH'
    ) # type: ignore
    
    filter_glob: bpy.props.StringProperty(
        default="*.json;",
        options={'HIDDEN'}
    ) # type: ignore
    
    @classmethod
    def poll(cls, context):
        try:
            char_board = devices.BL_CharBoard.from_bl_obj(context.object)
        except Exception:
            return False

        return 0 < len(char_board.settings.poses)

    def execute(self, context):
        """Called when user confirms file selection"""
        filepath = self.filepath

        if not filepath.endswith(".json"):
            filepath += ".json"
        
        # Gather up the data and store in json object
        char_board = devices.BL_CharBoard.from_bl_obj(context.object)

        data = {"char_board" : {
                "poses" : [
                    {
                        "translation" : {
                            "x" : pose.translation[0],
                            "y" : pose.translation[1],
                            "z" : pose.translation[2]
                        },
                        "rotation" : {
                            "w" : pose.rotation[0],
                            "x" : pose.rotation[1],
                            "y" : pose.rotation[2],
                            "z" : pose.rotation[3],
                        }
                    } 
                    for pose in char_board.settings.poses
                ]
            }
        }

        with open(filepath, 'w') as json_file:
            json.dump(data, json_file, indent=2)
        
        self.report({'INFO'}, f"Saved to {filepath}")

        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class OP_RemoveCharBoardPose(bpy.types.Operator):
    bl_idname = "menu.op_remove_char_board_pose"
    bl_label = "Remove Pose"
    
    pose_id : bpy.props.IntProperty(name="Remove Pose ID") # type: ignore

    @classmethod
    def poll(cls, context):
        try:
            char_board = devices.BL_CharBoard.from_bl_obj(context.object)
        except ValueError:
            return False
        
        return 0 < len(char_board.settings.poses)

    def execute(self, context):
        char_board = devices.BL_CharBoard.from_bl_obj(context.object)

        poses = char_board.settings.poses

        poses.remove(self.pose_id)
            
        return {'FINISHED'}

class OP_AddCharBoardPose(bpy.types.Operator):
    bl_idname = "menu.op_add_char_board_pose"
    bl_label = "Add Pose"

    @classmethod
    def poll(cls, context):
        try:
            char_board = devices.BL_CharBoard.from_bl_obj(context.object)
        except ValueError:
            return False
        
        return True

    def execute(self, context):
        char_board = devices.BL_CharBoard.from_bl_obj(context.object)

        poses = char_board.settings.poses
        
        new_item = poses.add()
        new_item.translation = char_board.bl_obj.delta_location
        new_item.rotation = char_board.bl_obj.delta_rotation_quaternion

        return {'FINISHED'}

class OP_ViewCBTransform(bpy.types.Operator):
    bl_idname = "menu.op_viewcbtransform"
    bl_label = "View Transform"

    transform_id : bpy.props.IntProperty(name="Transform ID", default=-1) # type: ignore

    @classmethod
    def poll(cls, context):
        try:
            board = devices.BL_CharBoard.from_bl_obj(context.object)
        except ValueError:
            return False
        
        return True

    def execute(self, context):
        board = devices.BL_CharBoard(context.object)

        pose = board.settings.cb_transforms[self.transform_id]
        
        board.bl_obj.delta_location = pose.translation
        board.bl_obj.delta_rotation_quaternion = pose.rotation

        return {'FINISHED'}


# Projector

class OP_AddFringeProjector(Operator):
    bl_idname = "menu.add_fringeprojector"
    bl_label = "Fringe Projector"
    bl_options = {'REGISTER', 'UNDO'}

    name        : bpy.props.StringProperty(name="Name", default="FringeProjector") # type: ignore
    location    : bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation    : bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        # Create the blender object for the projector
        # *The actual projector object will be constructed ad-hoc when it is needed
        bl_obj = devices.BL_Projector.create_bl_obj(self.location, self.rotation, name=self.name)
        
        return {'FINISHED'}


# Camera

class OP_AddCamera(Operator):
    bl_idname = "menu.add_camera"
    bl_label = "Basic Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    name : bpy.props.StringProperty(name="Name", default="Camera") # type: ignore

    location : bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation : bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        # Create the Blender Object for the camera
        # *The actual camera object will be constructed ad-hoc when it is needed

        camera = devices.BL_Camera.create_bl_obj(self.location, self.rotation, name=self.name)

        # TODO: Set blender object properties

        return {'FINISHED'}

class OP_CameraSetScene(Operator):
    bl_idname = "op.camera_set_scene"
    bl_label = "Update"

    @classmethod
    def poll(cls, context):
        bl_obj = context.object

        return devices.BL_Camera.is_camera(bl_obj)

    def execute(self, context):
        scene = context.scene

        camera = devices.BL_Camera.from_bl_obj(context.object)

        # Camera settings
        scene.render.fps = camera.refresh_rate
        scene.render.resolution_x = camera.resolution[0]
        scene.render.resolution_y = camera.resolution[1]
        scene.render.image_settings.color_mode = "RGB" if camera.channels == 3 else "BW"

        # Blender settings
        # Cycles engine 
        scene.render.engine = "CYCLES" 

        # Pixel bit depth
        scene.render.image_settings.color_depth = camera.settings.bit_depth   

         # Use .tif
        scene.render.image_settings.file_format = camera.settings.file_format
        if camera.settings.file_format == "TIFF": scene.render.image_settings.tiff_codec = 'NONE'
            
        # Number of viewport samples
        scene.cycles.samples = camera.settings.render_samples # Set scene sample rate

        return {'FINISHED'}

# Blender register

classes = [
    # Camera
    OP_AddCamera,
    OP_CameraSetScene,

    # Projector
    OP_AddFringeProjector,

    # Char
    OP_AddCheckerBoard,
    OP_AddCircleBoard,
    OP_AddImageBoard,

    OP_AddCharBoardPose,
    OP_RemoveCharBoardPose,
    OP_ViewCBTransform,

    OP_SaveBoardPoses,
    OP_LoadBoardPoses,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)