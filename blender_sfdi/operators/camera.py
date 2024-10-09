import bpy
from bpy.types import Operator

from ..blender import BL_Camera

class OP_RegisterCamera(Operator):
    bl_idname = "op.register_camera"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        cameras = context.scene.ExCameras

        bl_obj = context.object

        return BL_Camera.is_camera(bl_obj) and (cameras.find(bl_obj.name) < 0)

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
    bl_label = "Basic Camera"
    bl_options = {'REGISTER', 'UNDO'}

    location : bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation : bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        # Create a default camera
        BL_Camera.create_bl_obj(self.location, self.rotation)

        return {'FINISHED'}

class OP_AddPiCameraV1(Operator):
    bl_idname = "menu.add_picamerav1"
    bl_label = "Pi v1.0 Camera"
    bl_options = {'REGISTER', 'UNDO'}

    location : bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore
    rotation : bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        # Create a default camera
        camera = BL_Camera.create_bl_obj(self.location, self.rotation)
        
        camera.resolution = (2592, 1944)

        return {'FINISHED'}

classes = [
    OP_RegisterCamera,
    OP_UnregisterCamera,

    OP_AddCamera,
    OP_AddPiCameraV1,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)