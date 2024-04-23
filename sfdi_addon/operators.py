import bpy

class OP_RegisterProj(bpy.types.Operator):
    bl_idname = "op.register_proj"
    bl_label = "TODO: Write label"
    
    @classmethod
    def poll(cls, context):
        return context.object.type == "LIGHT"
            
    def execute(self, context):
        selected = context.object
        
        fps = context.scene.FringeProjectors
        
        if selected.name in fps.items:
            return {'FINISHED'}
        
        new_item = fps.items.add()
        new_item.name = selected.name
        new_item.obj = selected
        
        if fps.id < len(fps.items) - 1:
            fps.id = len(fps.items) - 1
            
        return {'FINISHED'}

class OP_UnregisterProj(bpy.types.Operator):
    bl_idname = "op.unregister_proj"
    bl_label = "TODO: Write label"
            
    def execute(self, context):
        fps = context.scene.FringeProjectors

        if len(fps.items) < 1: return {'FINISHED'}
        
        fps.items.remove(fps.id)
        
        if len(fps.items) <= fps.id: fps.id = len(fps.items) - 1
            
        return {'FINISHED'}

class OP_AddProj(bpy.types.Operator):
    bl_idname = "menu.add_proj"
    bl_label = "Projector"

    def execute(self, context):
        self.report({'INFO'}, f"Adding a projector")
        
        # TODO: add logic to add a projector
        
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
    
    # OP_RegisterCamera,
    # OP_UnregisterCamera
    
    OP_RunExperiment,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(lambda s, ctx: s.layout.operator(OP_AddProjector.bl_idname))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)