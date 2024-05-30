import bpy
from bpy.types import Operator

class OP_RegisterObject(Operator):
    bl_idname = "op.register_object"
    bl_label = "TODO: Write label"
    
    @classmethod
    def poll(cls, context):
        objs = context.scene.ExProperties.objects

        return context.object and (objs.find(context.object.name) < 0)

    def execute(self, context):
        selected = context.object
        
        objs = context.scene.ExProperties.objects
        
        new_item = objs.add()
        new_item.name = selected.name
        new_item.obj = selected

        return {'FINISHED'}

class OP_UnregisterObject(Operator):
    bl_idname = "op.unregister_object"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        objs = context.scene.ExProperties.objects

        return context.object and (0 <= objs.find(context.object.name))
            
    def execute(self, context):
        objs = context.scene.ExProperties.objects
        selected = context.object

        selected_id = objs.find(selected.name)
        
        if selected_id is None: return {'FINISHED'}

        objs.remove(selected_id)
            
        return {'FINISHED'}

def hide_objects(value):
    objs = bpy.context.scene.ExProperties.objects
    
    for obj in objs:
        obj.obj.hide_render = value

classes = [
    OP_RegisterObject,
    OP_UnregisterObject,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)