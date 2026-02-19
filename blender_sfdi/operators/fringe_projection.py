import bpy
import json

from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

from .. import devices

# TODO: Add support for selecting filetype
# TODO: Add support for measurements being automatically added to Blender

# Calibration

class OP_CreateAnimation(Operator):
    bl_idname = "op.fp_createanimation"
    bl_label = "Characterise"

    def _set_interp(self, animatable, data_path, mode, index=-1):
        action = animatable.animation_data.action   

        fcurve = action.fcurve_ensure_for_datablock(datablock=animatable, data_path=data_path, index=index)
        for i in range(len(fcurve.keyframe_points)):
            fcurve.keyframe_points[i].interpolation = mode

    def _generate_animation(self, camera, projector, stripe_counts, phases, rotations, frame_start=0):
        frame_id = frame_start

        channel = projector.settings.channels_list[0]

        for rotation in rotations: # Set projector rotation
            channel.rotation = rotation
            projector.bl_obj.data.keyframe_insert(data_path="sfdi.channels_list[0].rotation", frame=frame_id)

            for stripe_count in stripe_counts: # Set projector stripe count
                channel.stripe_count = stripe_count
                projector.bl_obj.data.keyframe_insert(data_path=f"sfdi.channels_list[0].stripe_count", frame=frame_id)

                for phase in phases: # Set projector phase
                    channel.phase = phase
                    projector.bl_obj.data.keyframe_insert(data_path="sfdi.channels_list[0].phase", frame=frame_id)

                    frame_id += 1

        # Disable any interpolation
        self._set_interp(projector.bl_obj.data, data_path="sfdi.channels_list[0].stripe_count", mode='CONSTANT')
        self._set_interp(projector.bl_obj.data, data_path="sfdi.channels_list[0].rotation", mode='CONSTANT')
        self._set_interp(projector.bl_obj.data, data_path="sfdi.channels_list[0].phase", mode='CONSTANT')

        return frame_id

    def execute(self, context):
        scene = context.scene
        settings = scene.fp_stereo

        fringes_manager = settings.fringes_manager
        
        # Check correct devices were passed
        if not devices.BL_Camera.is_camera(settings.camera): return {"FINISHED"}
        if not devices.BL_Projector.is_projector(settings.projector): return {"FINISHED"}
            
        # Create devices and clear animation data
        camera = devices.BL_Camera.from_bl_obj(settings.camera)
        camera.bl_obj.animation_data_clear()
        
        projector = devices.BL_Projector.from_bl_obj(settings.projector)
        projector.bl_obj.animation_data_clear()
        
        # Check if characterising
        char_board = None
        if devices.BL_CharBoard.is_char_board(settings.char_board): # Error
            char_board = devices.BL_CharBoard.from_bl_obj(settings.char_board)
            char_board.bl_obj.animation_data_clear()

        # Get fringe manager values
        stripe_counts = [prop.value for prop in fringes_manager.stripe_counts]
        phases = [prop.value for prop in fringes_manager.phases]
        rotations = [prop.value for prop in fringes_manager.rotations]

        # Set scene start value
        scene.frame_start = 0
        scene.frame_step = 1

        if char_board is not None:
            frame_track = 0

            # Create animation for each board pose
            for pose in char_board.bl_obj.sfdi.poses:
                char_board.bl_obj.delta_location = pose.translation
                char_board.bl_obj.delta_rotation_quaternion = pose.rotation

                # Generateo characterisation board positions first
                char_board.bl_obj.keyframe_insert(data_path='delta_location', frame=frame_track)
                char_board.bl_obj.keyframe_insert(data_path='delta_rotation_quaternion', frame=frame_track)

                frame_track = self._generate_animation(camera, projector, stripe_counts, phases, rotations, frame_start=frame_track)

            # Disable any interp
            for i in range(3):
                self._set_interp(char_board.bl_obj, data_path="delta_location", mode='CONSTANT', index=i)

            for i in range(4):
                self._set_interp(char_board.bl_obj, data_path="delta_rotation_quaternion", mode='CONSTANT', index=i)
            
        else: frame_track = self._generate_animation(camera, projector, stripe_counts, phases, rotations)
            
        scene.frame_end = frame_track - 1

        return {"FINISHED"}


# Fringes Manager

class OP_AddStripeCount(Operator):
    bl_idname = "menu.op_add_stripe_count"
    bl_label = "Add Stripe Count"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager

        # Limit to 30 stripe counts
        return len(settings.stripe_counts) <= 29

    def execute(self, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager

        new_item = settings.stripe_counts.add()
            
        return {'FINISHED'}

class OP_AddPhase(Operator):
    bl_idname = "menu.op_add_phase"
    bl_label = "Add Phase"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager
        
        # Limit to 32 phase counts
        return len(settings.phases) <= 29

    def execute(self, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager

        new_item = settings.phases.add()
            
        return {'FINISHED'}
    
class OP_AddRotation(Operator):
    bl_idname = "menu.op_add_rotation"
    bl_label = "Add Rotation"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager

        # Limit to 30 rotations
        return len(settings.rotations) <= 29

    def execute(self, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager

        new_item = settings.rotations.add()
            
        return {'FINISHED'}
    
class OP_RemoveStripeCount(Operator):
    bl_idname = "menu.op_remove_stripe_count"
    bl_label = "Remove Stripe Count"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager
        
        return 1 < len(settings.stripe_counts)

    def execute(self, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager

        stripe_counts = settings.stripe_counts

        stripe_counts.remove(len(stripe_counts) - 1)
            
        return {'FINISHED'}
 
class OP_RemovePhase(Operator):
    bl_idname = "menu.op_remove_phase"
    bl_label = "Remove Phase"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager
        
        return 1 < len(settings.phases)

    def execute(self, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager

        phases = settings.phases

        phases.remove(len(phases) - 1)
            
        return {'FINISHED'}
 
class OP_RemoveRotation(Operator):
    bl_idname = "menu.op_remove_rotation"
    bl_label = "Remove Rotation"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager
        
        return 1 < len(settings.rotations)

    def execute(self, context):
        scene = context.scene
        settings = scene.fp_stereo.fringes_manager

        rotations = settings.rotations

        rotations.remove(len(rotations) - 1)
            
        return {'FINISHED'}

class OP_SaveMetadata(bpy.types.Operator, ImportHelper):
    bl_idname = "op.save_metadata"
    bl_label = "Save Metadata"
    
    filepath: bpy.props.StringProperty(
        name="File path",
        description="Filepath for saving",
        maxlen=1024,
        subtype='FILE_PATH'
    ) # type: ignore 
    
    filename: bpy.props.StringProperty(
        name="Filename",
        description="Name of the file",
        default="metadata.json",
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

    def _camera_metadata(self, camera: devices.BL_Camera):
        translation = camera.world_matrix.to_translation()
        rotation = camera.world_matrix.to_quaternion()

        return {
            "name" : camera.bl_obj.name,
            "translation" : {
                "x" : translation.x,
                "y" : translation.y,
                "z" : translation.z,
            },
            "rotation" : {
                "w" : rotation.w,
                "x" : rotation.x,
                "y" : rotation.y,
                "z" : rotation.z,
            },
            "resolution" : {
                "width" : camera.resolution[0],
                "height" : camera.resolution[1],
            },
            "channels": camera.channels,
            "refresh_rate": camera.refresh_rate,
            "render_samples": camera.render_samples,
        }

    def _projector_metadata(self, projector: devices.BL_Projector):
        translation = projector.world_matrix.to_translation()
        rotation = projector.world_matrix.to_quaternion()

        return {
            "name" : projector.bl_obj.name,
            # "resolution" : {
            #     "width" : {projector.resolution[0]},
            #     "height" : {projector.resolution[1]},
            # },
            "translation" : {
                "x" : translation.x,
                "y" : translation.y,
                "z" : translation.z,
            },
            "rotation" : {
                "w" : rotation.w,
                "x" : rotation.x,
                "y" : rotation.y,
                "z" : rotation.z,
            },
            "channels": [{
                    "fringes_type" : projector.settings.channels_list[i].fringes_type,
                    "intensity" : projector.settings.channels_list[i].intensity,
                    "noise" : projector.settings.channels_list[i].noise,
            } for i in range(projector.channels)],

            "refresh_rate" : projector.refresh_rate,
            "throw_ratio" : projector.throw_ratio,
            "aspect_ratio" : projector.aspect_ratio,
            "light_falloff" : projector.settings.light_falloff,
        }

    def _char_board_metadata(self, char_board: devices.BL_CharBoard):
        return {
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

    def _generate_metadata(self, scene):
        fp_stereo = scene.fp_stereo
        fringes_manager = fp_stereo.fringes_manager


        # Add Fringe Manager data first
        metadata = {
            "stripe_counts" : [prop.value for prop in fringes_manager.stripe_counts],
            "phases" : [prop.value for prop in fringes_manager.phases],
            "rotations" : [prop.value for prop in fringes_manager.rotations],
            "multiplexing" : fringes_manager.multiplexing,
        }

        # Add camera data if present
        if devices.BL_Camera.is_camera(fp_stereo.camera):
            camera = devices.BL_Camera.from_bl_obj(fp_stereo.camera)
            metadata["camera"] = self._camera_metadata(camera)
        
        # Add projector data if present
        if devices.BL_Projector.is_projector(fp_stereo.projector):
            projector = devices.BL_Projector.from_bl_obj(fp_stereo.projector)
            metadata["projector"] = self._projector_metadata(projector)

        # Add projector data if present
        if devices.BL_CharBoard.is_char_board(fp_stereo.char_board):
            char_board = devices.BL_CharBoard.from_bl_obj(fp_stereo.char_board)
            metadata["char_board"] = self._char_board_metadata(char_board)

        return metadata
    
    def execute(self, context):
        """Called when user confirms file selection"""
        filepath = self.filepath

        if not filepath.endswith(".json"):
            filepath += ".json"

        scene = context.scene

        metadata = self._generate_metadata(scene)

        with open(filepath, 'w') as json_file:
            json.dump(metadata, json_file, indent=2)
        
        self.report({'INFO'}, f"Saved to {filepath}")

        return {'FINISHED'}
    
    def invoke(self, context, event):
        """Called when operator is invoked"""
        # Open file browser
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

classes = [
    # Calibration,
    OP_AddStripeCount,
    OP_AddPhase,
    OP_AddRotation,

    OP_RemoveStripeCount,
    OP_RemovePhase,
    OP_RemoveRotation,

    OP_SaveMetadata,
    OP_CreateAnimation,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)