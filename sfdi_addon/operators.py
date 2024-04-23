import bpy

from sfdi_addon.video import CameraFactory, ProjectorFactory

from sfdi_addon.experiment import BlenderExperiment

class OP_RegisterProj(bpy.types.Operator):
    bl_idname = "op.register_proj"
    bl_label = "TODO: Write label"
    
    @classmethod
    def poll(cls, context):
        fps = context.scene.FringeProjectors

        return (context.object.type == "LIGHT") and (fps.get_id_by_name(context.object.name) is None)

    def execute(self, context):
        selected = context.object
        
        fps = context.scene.FringeProjectors
        
        new_item = fps.items.add()
        new_item.name = selected.name
        new_item.obj = selected
        
        if fps.id < len(fps.items) - 1:
            fps.id = len(fps.items) - 1
            
        return {'FINISHED'}

class OP_UnregisterProj(bpy.types.Operator):
    bl_idname = "op.unregister_proj"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        fps = context.scene.FringeProjectors

        if len(fps.items) < 1: return False 

        return not (fps.get_id_by_name(context.object.name) is None)
            
    def execute(self, context):
        fps = context.scene.FringeProjectors
        selected = context.object

        fps.id = fps.get_id_by_name(selected.name)
        if fps.id is None: return {'FINISHED'}

        fps.items.remove(fps.id)
        
        if len(fps.items) < 1: return {'FINISHED'}

        if len(fps.items) <= fps.id: fps.id = len(fps.items) - 1
            
        return {'FINISHED'}

class OP_AddProj(bpy.types.Operator):
    bl_idname = "menu.add_proj"
    bl_label = "Projector"

    def execute(self, context):
        self.report({'INFO'}, f"Adding a projector")
        
        # TODO: add logic to add a projector
        # Show a modal popup with some configurables (to match a specific projector?)
        
        return {'FINISHED'}

class OP_AddCamera(bpy.types.Operator):
    bl_idname = "menu.add_camera"
    bl_label = "SFDI Camera"

    def execute(self, context):
        self.report({'INFO'}, f"Adding a camera")
        
        # TODO: Add a camera
        # Show a modal popup with some configurables (such as selecting certain camera etc)
        
        return {'FINISHED'}

# class OP_RegisterCamera(bpy.types.Operator):
#     bl_idname = "op.register_proj"
#     bl_label = "TODO: Write label"
    
#     @classmethod
#     def poll(cls, context):
#         registered = context.scene.FringeProjectors.items
        
#         return (context.object.name in bpy.data.lights) and (context.object.name not in registered)
            
#     def execute(self, context):
#         selected = context.object
        
#         fps = context.scene.FringeProjectors
        
#         new_item = fps.items.add()
#         new_item.name = selected.name
#         new_item.obj = selected
        
#         if fps.id < len(fps.items) - 1:
#             fps.id = len(fps.items) - 1
            
#         return {'FINISHED'}

# class OP_UnregisterCamera(bpy.types.Operator):
#     bl_idname = "op.unregister_proj"
#     bl_label = "TODO: Write label"
    
#     @classmethod
#     def poll(cls, context):
#         return context.object.name in context.scene.FringeProjectors.items
            
#     def execute(self, context):
#         selected = context.object
        
#         fps = context.scene.FringeProjectors
        
#         fps.id = [i for i, item in enumerate(fps.items) if item.name == selected.name][0]
#         fps.items.remove(fps.id)

#         if len(fps.items) < 1: return {'FINISHED'}
        
#         if fps.id >= len(fps.items):
#             fps.id = len(fps.items) - 1
            
#         return {'FINISHED'}


class OP_RunExperiment(bpy.types.Operator):
    bl_idname = "op.run_experiment"
    bl_label = "TODO"

    def execute(self, context):
        # TODO: Gather all the experiment settings, create correct objects, and run the experiment
        
        # TODO: Need to gather the results and present them in a pretty way
        
        return {'FINISHED'}


classes = [
    OP_RegisterProj,
    OP_UnregisterProj,
    OP_AddProj,
    OP_AddCamera,
    
    # OP_RegisterCamera,
    # OP_UnregisterCamera
    
    OP_RunExperiment,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(lambda self, context: self.layout.operator(OP_AddProj.bl_idname))
    bpy.types.VIEW3D_MT_add.append(lambda self, context: self.layout.operator(OP_AddCamera.bl_idname))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)