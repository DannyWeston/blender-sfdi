import bpy

class PG_Object(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.Object)

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
    PG_Object,
    PG_Fringes,
]

def check_collections_update(scene):
    projectors = bpy.context.scene.ExProjectors
    cameras = bpy.context.scene.ExCameras
    
    for proj in projectors:
        if not proj.obj:
            temp_id = projectors.find(proj.name)
            projectors.remove(temp_id)

    for cam in cameras:
        if not cam.obj:
            temp_id = cameras.find(cam.name)
            cameras.remove(temp_id)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.app.handlers.depsgraph_update_post.append(check_collections_update)
        
    bpy.types.Scene.ExProjectors = bpy.props.CollectionProperty(type=PG_Object)
    bpy.types.Scene.ExProjectorsIndex = bpy.props.IntProperty(name="ExProjectorsIndex2")
    
    bpy.types.Scene.ExCameras = bpy.props.CollectionProperty(type=PG_Object)
    bpy.types.Scene.ExCamerasIndex = bpy.props.IntProperty(name="ExCamerasIndex2")
    
    bpy.types.Scene.FringesProps = bpy.props.PointerProperty(type=PG_Fringes)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    bpy.app.handlers.depsgraph_update_post.remove(check_collections_update)
    
    del bpy.types.Scene.ExProjectors
    del bpy.types.Scene.ExProjectorsIndex
    del bpy.types.Scene.ExCameras
    del bpy.types.Scene.ExCamerasIndex
    del bpy.types.Scene.FringesProps