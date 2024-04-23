import bpy

class PG_FringeProj(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.Object)
    
    
class PG_FPCollection(bpy.types.PropertyGroup):
    id: bpy.props.IntProperty()
    items: bpy.props.CollectionProperty(type=PG_FringeProj)
    
    
class PG_Fringes(bpy.types.PropertyGroup):
    phases: bpy.props.IntProperty(name="Phases", default=3, min=3, max=16)
    
    rotation: bpy.props.FloatProperty(name="Rotation", default=90, min=0, max=180)
    
    fringes_type: bpy.props.EnumProperty(
        name="Type",
        description="TODO: Some description",
        items=[
            ("OP1", "Sinusoidal",   "TODO: Fill tooltip"),
            ("OP2", "Binary",       "TODO: Fill tooltip"),
        ]
    )
    
    
classes = [
    PG_Fringes,
    
    PG_FringeProj,
    PG_FPCollection,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.FringeProjectors = bpy.props.PointerProperty(type=PG_FPCollection)
    
    bpy.types.Scene.FringesProps = bpy.props.PointerProperty(type=PG_Fringes)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.FringeProjectors
    del bpy.types.Scene.FringesProps