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
    bl_idname = "op.add_camera"
    bl_label = "SFDI Camera"

    def execute(self, context):
        # Add the stuff
        
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

classes = [
    OP_RegisterCamera,
    OP_UnregisterCamera,
    OP_AddCamera,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(lambda self, context: self.layout.operator(OP_AddCamera.bl_idname))

def unregister():
    # TODO: Remove from VIEW3D
    
    for cls in classes:
        bpy.utils.unregister_class(cls)