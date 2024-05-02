import bpy

from math import pi

class PG_Object(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.Object)

class PG_Projector(bpy.types.PropertyGroup):
    frequency: bpy.props.FloatProperty(name="Frequency", default=32.0, min=0.0)
    
    phase: bpy.props.FloatProperty(name="Phase", default=0.0, min=0.0, unit='ROTATION')
    
    rotation: bpy.props.FloatProperty(name="Rotation", default=0.0, unit='ROTATION')
    
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

class PG_Experiment(bpy.types.PropertyGroup):
    objects: bpy.props.CollectionProperty(type=PG_Object)
    object_index: bpy.props.IntProperty(name="object_index")
    
    phase_count: bpy.props.IntProperty(name="Phase Count", default=3, min=3, max=32)
    
    runs: bpy.props.IntProperty(name="Runs", default=1, min=1)

classes = [
    PG_Object,
    PG_Projector,
    PG_Experiment,
]

def check_collections_update(scene):
    projectors = bpy.context.scene.ExProjectors
    cameras = bpy.context.scene.ExCameras
    objs = bpy.context.scene.ExProperties.objects
    
    for proj in projectors:
        if proj.obj is None:
            # Remove from list
            temp_id = projectors.find(proj.name)
            projectors.remove(temp_id)
            return

        if scene.objects.get(proj.obj.name) is None:
            bpy.data.objects.remove(proj.obj)

    for cam in cameras:
        if cam.obj is None:
            # Remove from list
            temp_id = cameras.find(cam.name)
            cameras.remove(temp_id)
            return
            
        if scene.objects.get(cam.obj.name) is None:
            bpy.data.objects.remove(cam.obj)
            
    for obj in objs:
        if obj.obj is None:
            # Remove from list
            temp_id = objs.find(obj.name)
            objs.remove(temp_id)
            return
            
        if scene.objects.get(obj.obj.name) is None:
            bpy.data.objects.remove(obj.obj)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.app.handlers.depsgraph_update_post.append(check_collections_update)
    
    bpy.types.Scene.ExProperties = bpy.props.PointerProperty(type=PG_Experiment)
        
    bpy.types.Scene.ExProjectors = bpy.props.CollectionProperty(type=PG_Object)
    bpy.types.Scene.ExProjectorsIndex = bpy.props.IntProperty(name="ExProjectorsIndex")
    
    bpy.types.Scene.ExCameras = bpy.props.CollectionProperty(type=PG_Object)
    bpy.types.Scene.ExCamerasIndex = bpy.props.IntProperty(name="ExCamerasIndex")
    
    bpy.types.Object.ProjectorSettings = bpy.props.PointerProperty(type=PG_Projector)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    bpy.app.handlers.depsgraph_update_post.remove(check_collections_update)
    
    del bpy.types.Scene.ExProperties
    
    del bpy.types.Scene.ExProjectors
    del bpy.types.Scene.ExProjectorsIndex
    
    del bpy.types.Scene.ExCameras
    del bpy.types.Scene.ExCamerasIndex
    
    del bpy.types.Object.ProjectorSettings