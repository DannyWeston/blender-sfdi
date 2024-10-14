import bpy

import numpy as np

from .ui import on_cb_debug
from .blender import BL_Camera, BL_FringeProjector


class PG_Object(bpy.types.PropertyGroup):
    obj : bpy.props.PointerProperty(type=bpy.types.Object) # type: ignore

# # # # # # # # # # # # # # # # # # # # # 
# Projector

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


# # # # # # # # # # # # # # # # # # # # # 
# Camera

class PG_CameraSettings(bpy.types.PropertyGroup):
    resolution : bpy.props.IntVectorProperty(name="Resolution", size=2, default=(1920, 1080)) # type: ignore

    # sensor_size : bpy.props.FloatVectorProperty(name="Sensor Size", size=2, default=(36.0, 24.0)) # type: ignore

    # focal_length : bpy.props.FloatProperty(name="Focal Length", default=50.0)

    # aspect_ratio : bpy.props.FloatProperty(name="Aspect Ratio", default=16.0/9.0, min=1.0, subtype='FACTOR') # type: ignore


# # # # # # # # # # # # # # # # # # # # # 
# Calibration

class PG_CheckerboardSettings(bpy.types.PropertyGroup):
    size : bpy.props.IntVectorProperty(name="Size", size=2, default=(8, 6), min=1) # type: ignore

    seed : bpy.props.IntProperty(name="Seed", default=0, update=on_cb_debug) # type: ignore

    max_position : bpy.props.FloatVectorProperty(name="Max Position", size=3, default=(0.2, 0.2, 0.2), min=0, subtype='TRANSLATION', update=on_cb_debug) # type: ignore

    max_rotation : bpy.props.FloatVectorProperty(name="Max Rotation", size=3, default=(np.pi / 10.0, np.pi / 10.0, np.pi / 10.0), min=0, max=np.pi, subtype='EULER', update=on_cb_debug) # type: ignore

    show_debug : bpy.props.BoolProperty(name="Show Debug", default=False, update=on_cb_debug) # type: ignore


# # # # # # # # # # # # # # # # # # # # # 
# Experiment

class PG_Experiment(bpy.types.PropertyGroup):
    runs : bpy.props.IntProperty(name="Runs", default=1, min=1) # type: ignore

    output_dir : bpy.props.StringProperty(name="Output Directory", description="Choose a directory:", subtype='DIR_PATH') # type: ignore

    bl_objs : bpy.props.CollectionProperty(type=PG_Object)  # type: ignore
    bl_obj_index : bpy.props.IntProperty(name="object_index") # type: ignore

class PG_NStepClassic(bpy.types.PropertyGroup):
    camera : bpy.props.PointerProperty(type=bpy.types.Object, poll=lambda _, o: BL_Camera.is_camera(o)) # type: ignore

    projector : bpy.props.PointerProperty(type=bpy.types.Object, poll=lambda _, o: BL_FringeProjector.is_fringe_proj(o)) #type: ignore

    phases : bpy.props.IntProperty(name="Phase Count", default=3, min=3, max=32) # type: ignore
    
    sf : bpy.props.FloatProperty(name="Spatial Frequency", default=0.0, min=0.0) # type: ignore

    calibrate : bpy.props.IntProperty(name="Calibration", default=0, min=0) # type: ignore

def check_stale_objs(scene):
    bl_obj_ptrs = scene.ex_settings.bl_objs

    if bl_obj_ptrs:
        for ptr in bl_obj_ptrs:
            if scene.objects.get(ptr.name) is None:
                # Remove from list
                temp_id = bl_obj_ptrs.find(ptr.name)
                bl_obj_ptrs.remove(temp_id)

classes = [
    PG_Object,

    PG_ProjSettings,
    PG_CheckerboardSettings,
    PG_CameraSettings,

    # Experiment
    PG_Experiment,
    PG_NStepClassic,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.handlers.depsgraph_update_post.append(check_stale_objs)

    # SFDI Object Properties
    bpy.types.Object.proj_settings = bpy.props.PointerProperty(type=PG_ProjSettings)
    bpy.types.Object.camera_settings = bpy.props.PointerProperty(type=PG_CameraSettings)
    bpy.types.Object.cb_settings = bpy.props.PointerProperty(type=PG_CheckerboardSettings)

    # Experiment settings
    bpy.types.Scene.ex_settings = bpy.props.PointerProperty(type=PG_Experiment)
    bpy.types.Scene.ex_nstepclassic = bpy.props.PointerProperty(type=PG_NStepClassic)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.depsgraph_update_post.remove(check_stale_objs)
    
    del bpy.types.Object.proj_settings
    del bpy.types.Object.camera_settings
    del bpy.types.Object.cb_settings

    del bpy.types.Scene.ex_settings
    del bpy.types.Scene.ex_nstepclassic