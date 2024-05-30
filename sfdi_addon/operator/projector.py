import bpy
from bpy.types import Operator

from sfdi_addon.video import ProjectorFactory

class OP_RegisterProj(Operator):
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

class OP_UnregisterProj(Operator):
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

class OP_AddProj(Operator):
    bl_idname = "menu.add_proj"
    bl_label = "Fringe Projector"

    bl_options = {'REGISTER', 'UNDO'}
    
    location: bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH')
    rotation: bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION')
    
    # Projector resolution
    width: bpy.props.IntProperty(name="Width", default=1024, min=1)
    height: bpy.props.IntProperty(name="Height", default=768, min=1)
    
    fringe_type: bpy.props.EnumProperty(
        name="Type",
        description="TODO: Some description",
        items=[
            ("OP1", "Sinusoidal",   "TODO: Fill tooltip", 1),
            ("OP2", "Binary",       "TODO: Fill tooltip", 2),
        ]
    )
    
    fringe_frequency: bpy.props.FloatProperty(name="Fringe Frequency", default=32.0, min=0.0)
    
    fringe_phase: bpy.props.FloatProperty(name="Fringe Phase", default=0.0, unit='ROTATION')
    
    fringe_rotation: bpy.props.FloatProperty(name="Fringe Rotation", default=0.0, unit='ROTATION')

    # TODO: Implement custom draw function to make menu look a bit nicer

    def execute(self, context):
        # Make a projector using factory
        projector = ProjectorFactory.MakeDefault(self.location, self.rotation)

        proj_settings = projector.ProjectorSettings

        proj_settings.frequency = self.fringe_frequency
        proj_settings.phase = self.fringe_phase
        proj_settings.rotation = self.fringe_rotation
        proj_settings.fringe_type = self.fringe_type
        
        proj_settings.width = self.width
        proj_settings.height = self.height

        return {'FINISHED'}

classes = [
    OP_RegisterProj,
    OP_UnregisterProj,
    OP_AddProj
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_add.append(lambda self, context: self.layout.operator(OP_AddProj.bl_idname))

def unregister():
    # TODO: Remove from VIEW3D
    
    for cls in classes:
        bpy.utils.unregister_class(cls)