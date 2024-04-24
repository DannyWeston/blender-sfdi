import bpy

from sfdi_addon.video import CameraFactory, ProjectorFactory

from sfdi_addon.experiment import BlenderExperiment

class OP_RegisterProj(bpy.types.Operator):
    bl_idname = "op.register_proj"
    bl_label = "TODO: Write label"
    
    @classmethod
    def poll(cls, context):
        projs = context.scene.ExProjectors

        return context.object and (context.object.type == "LIGHT") and (projs.find(context.object.name) < 0)

    def execute(self, context):
        selected = context.object
        
        projs = context.scene.ExProjectors
        
        new_item = projs.add()
        new_item.name = selected.name
        new_item.obj = selected

        return {'FINISHED'}

class OP_UnregisterProj(bpy.types.Operator):
    bl_idname = "op.unregister_proj"
    bl_label = "TODO: Write label"

    @classmethod
    def poll(cls, context):
        projs = context.scene.ExProjectors

        return context.object and (0 <= projs.find(context.object.name))
            
    def execute(self, context):        
        projs = context.scene.ExProjectors
        selected = context.object

        selected_id = projs.find(selected.name)
        
        if selected_id is None: return {'FINISHED'}

        projs.remove(selected_id)
            
        return {'FINISHED'}

class OP_RegisterCamera(bpy.types.Operator):
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

class OP_UnregisterCamera(bpy.types.Operator):
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
    
    OP_RegisterCamera,
    OP_UnregisterCamera,
    OP_AddCamera,
    
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