import bpy
from bpy.app.handlers import persistent

import numpy as np
from .ui import on_cb_debug

class PG_Object(bpy.types.PropertyGroup):
    obj = bpy.props.PointerProperty(type=bpy.types.Object)

class PG_ProjSettings(bpy.types.PropertyGroup):    
    fringe_frequency : bpy.props.FloatProperty(name="Frequency", default=32.0, min=0.0) # type: ignore
    
    fringe_phase : bpy.props.FloatProperty(name="Phase", default=0.0, unit='ROTATION') # type: ignore
    
    fringe_rotation : bpy.props.FloatProperty(name="Rotation", default=0.0, unit='ROTATION') # type: ignore

    fringe_type : bpy.props.EnumProperty(
        name="Type",
        description="Type",
        items=[
            ("OP1", "Sinusoidal",   "TODO: Fill tooltip", 1),
    ]) # type: ignore

    throw_ratio : bpy.props.FloatProperty(name="Throw Ratio", default=1.0, min=1.0, subtype='FACTOR') # type: ignore

    aspect_ratio : bpy.props.FloatProperty(name="Aspect Ratio", default=16.0/9.0, min=1.0, subtype='FACTOR') # type: ignore
    
    resolution : bpy.props.IntVectorProperty(name="Resolution", size=2, default=(1024, 768), min=1) # type: ignore

class PG_CameraSettings(bpy.types.PropertyGroup):
    resolution : bpy.props.IntVectorProperty(name="Resolution", size=2, default=(1920, 1080)) # type: ignore

    # sensor_size : bpy.props.FloatVectorProperty(name="Sensor Size", size=2, default=(36.0, 24.0)) # type: ignore

    # focal_length : bpy.props.FloatProperty(name="Focal Length", default=50.0) # type: ignore

    # aspect_ratio : bpy.props.FloatProperty(name="Aspect Ratio", default=16.0/9.0, min=1.0, subtype='FACTOR') # type: ignore

class PG_CheckerboardSettings(bpy.types.PropertyGroup):
    size : bpy.props.IntVectorProperty(name="Size", size=2, default=(8, 6), min=1) # type: ignore

    seed : bpy.props.IntProperty(name="Seed", default=0, update=on_cb_debug) # type: ignore

    max_position : bpy.props.FloatVectorProperty(name="Max Position", size=3, default=(0.2, 0.2, 0.2), min=0, subtype='TRANSLATION', update=on_cb_debug) # type: ignore

    max_rotation : bpy.props.FloatVectorProperty(name="Max Rotation", size=3, default=(np.pi / 10.0, np.pi / 10.0, np.pi / 10.0), min=0, max=np.pi, subtype='EULER', update=on_cb_debug) # type: ignore

    show_debug : bpy.props.BoolProperty(name="Show Debug", default=False, update=on_cb_debug) # type: ignore

class PG_FPNStep(bpy.types.PropertyGroup):
    sf = bpy.props.FloatProperty(name="Spatial Frequency", default=0.0, min=0.0) # Stripe width

class PG_Experiment(bpy.types.PropertyGroup):
    objects = bpy.props.CollectionProperty(type=PG_Object)
    
    object_index = bpy.props.IntProperty(name="object_index")
    
    phase_count = bpy.props.IntProperty(name="Phase Count", default=3, min=3, max=32)
    
    runs = bpy.props.IntProperty(name="Runs", default=1, min=1)
    
    fp_n_step = bpy.props.PointerProperty(type=PG_FPNStep)

classes = [
    PG_Object,
    PG_FPNStep,
    PG_Experiment,

    PG_ProjSettings,
    PG_CheckerboardSettings,
    PG_CameraSettings
]

@persistent
def check_collections_update(scene, depsgraph):
    projectors = bpy.context.scene.ExProjectors
    cameras = bpy.context.scene.ExCameras
    objs = bpy.context.scene.ExProperties.objects
    
    if projectors:
        for proj in projectors:
            if proj.obj is None:
                # Remove from list
                temp_id = projectors.find(proj.name)
                projectors.remove(temp_id)
                return

            if scene.objects.get(proj.obj.name) is None:
                bpy.data.objects.remove(proj.obj)

    if cameras:
        for cam in cameras:
            if cam.obj is None:
                # Remove from list
                temp_id = cameras.find(cam.name)
                cameras.remove(temp_id)
                return
                
            if scene.objects.get(cam.obj.name) is None:
                bpy.data.objects.remove(cam.obj)

    if objs:            
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

    #bpy.app.handlers.depsgraph_update_post.append(check_collections_update)

    # SFDI Object Properties
    bpy.types.Object.proj_settings = bpy.props.PointerProperty(type=PG_ProjSettings)
    bpy.types.Object.camera_settings = bpy.props.PointerProperty(type=PG_CameraSettings)
    bpy.types.Object.cb_settings = bpy.props.PointerProperty(type=PG_CheckerboardSettings)

    # Experiment settings
    bpy.types.Scene.ExProperties = bpy.props.PointerProperty(type=PG_Experiment)

    bpy.types.Scene.ExProjectors = bpy.props.CollectionProperty(type=PG_Object)
    bpy.types.Scene.ExProjectorsIndex = bpy.props.IntProperty(name="ExProjectorsIndex")
    
    bpy.types.Scene.ExCameras = bpy.props.CollectionProperty(type=PG_Object)
    bpy.types.Scene.ExCamerasIndex = bpy.props.IntProperty(name="ExCamerasIndex")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Object.proj_settings
    del bpy.types.Object.camera_settings
    del bpy.types.Object.cb_settings

    del bpy.types.Scene.ExProperties
    
    del bpy.types.Scene.ExProjectors
    del bpy.types.Scene.ExProjectorsIndex
    
    del bpy.types.Scene.ExCameras
    del bpy.types.Scene.ExCamerasIndex