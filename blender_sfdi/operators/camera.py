import bpy
from bpy.types import Operator

class OP_RegisterCamera(Operator):
    bl_idname = "op.register_camera"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        cameras = context.scene.ExCameras

        return context.object and (context.object.type == "CAMERA") and (cameras.find(context.object.name) < 0)

    def execute(self, context):
        selected = context.object

        cameras = context.scene.ExCameras

        new_item = cameras.add()
        new_item.name = selected.name
        new_item.obj = selected

        return {'FINISHED'}

class OP_UnregisterCamera(Operator):
    bl_idname = "op.unregister_camera"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        cameras = context.scene.ExCameras

        return context.object and (0 <= cameras.find(context.object.name))

    def execute(self, context):
        cameras = context.scene.ExCameras
        selected = context.object

        selected_id = cameras.find(selected.name)

        if selected_id is None: return {'FINISHED'}

        cameras.remove(selected_id)

        return {'FINISHED'}

class OP_AddCamera(Operator):
    bl_idname = "menu.add_camera"
    bl_label = "SFDI Camera"
    bl_options = {'REGISTER', 'UNDO'}

    location : bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation : bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        # Create a default camera
        scene = context.scene

        bl_camera_obj = BL_CameraFactory.MakeDefaultCamera(self.location, self.rotation)

        scene.collection.objects.link(bl_camera_obj)

        return {'FINISHED'}

class BL_CameraFactory:
    @staticmethod
    def MakeDefaultCamera(location, rotation):
        # Create the object
        bl_camera = bpy.data.cameras.new("Camera")

        bl_camera_obj = bpy.data.objects.new("Camera", bl_camera)

        bl_camera_obj.location = location
        bl_camera_obj.rotation_euler = rotation

        return bl_camera_obj

    @staticmethod
    def MakePiCameraV1(location, rotation):
        # See: https://www.raspberrypi.com/documentation/accessories/camera.html
        bl_camera_obj = BL_CameraFactory.MakeDefaultCamera(location, rotation)

        settings = bl_camera_obj.camera_settings
        settings.resolution = (2592, 1944)

        # TODO: Find a way to limit the minimum and maximum values for non-default instances

        return bl_camera_obj

classes = [
    OP_RegisterCamera,
    OP_UnregisterCamera,
    OP_AddCamera,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)