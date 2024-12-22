import bpy
import numpy as np

from opensfdi.services import ExperimentService, FileExperimentRepo, FileImageRepo

from . import profilometry as prof
from ..definitions import get_storage_path
from ..blender import BL_Camera, BL_FringeProjector, BL_Checkerboard, BL_MotorStage

# Special class for relating a bl_prop to a class,
# and being able to instantiate said class


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

def on_cb_debug(self, context):
    cb = BL_Checkerboard(context.object)
    
    if cb.settings.show_debug:
        s = cb.settings
        cb.random_transform(s.max_position, s.max_rotation, s.seed)
        return

    cb.restore_transform()


class PG_CheckerboardSettings(bpy.types.PropertyGroup):
    size : bpy.props.IntVectorProperty(name="Size", size=2, default=(8, 6), min=1) # type: ignore

    seed : bpy.props.IntProperty(name="Seed", default=0, update=on_cb_debug) # type: ignore

    max_position : bpy.props.FloatVectorProperty(name="Max Position", size=3, default=(0.2, 0.2, 0.2), min=0, subtype='TRANSLATION', update=on_cb_debug) # type: ignore

    max_rotation : bpy.props.FloatVectorProperty(name="Max Rotation", size=3, default=(np.pi / 10.0, np.pi / 10.0, np.pi / 10.0), min=0, max=np.pi, subtype='EULER', update=on_cb_debug) # type: ignore

    show_debug : bpy.props.BoolProperty(name="Show Debug", default=False, update=on_cb_debug) # type: ignore


# # # # # # # # # # # # # # # # # # # # # 
# Experiment

def get_experiment_items(self, context):
    prof_repo = FileExperimentRepo(get_storage_path())
    img_repo = FileImageRepo(get_storage_path())

    service = ExperimentService(prof_repo, img_repo)

    return service.get_exp_list()

class PG_Experiment(bpy.types.PropertyGroup):
    bl_objs : bpy.props.CollectionProperty(type=PG_Object)  # type: ignore

    bl_obj_index : bpy.props.IntProperty(name="object_index") # type: ignore

    camera : bpy.props.PointerProperty(type=bpy.types.Object, poll=lambda _, o: BL_Camera.is_camera(o)) # type: ignore

    projector : bpy.props.PointerProperty(type=bpy.types.Object, poll=lambda _, o: BL_FringeProjector.is_fringe_proj(o)) # type: ignore

    phase_shift : bpy.props.PointerProperty(type=prof.PG_PhaseShift, name="phase_shift", description="Phase Shifting Method") # type: ignore

    phase_unwrap : bpy.props.PointerProperty(type=prof.PG_PhaseUnwrap, name="phase_unwrap", description="Phase Unwrapping Method") # type: ignore

    profilometry : bpy.props.PointerProperty(type=prof.PG_Profilometry, name="profilometry", description="Profilometry Method") # type: ignore


    # Calibration

    output_name : bpy.props.StringProperty(name="Calibration Name", description="Choose an output filename:") # type: ignore

    motor_stage : bpy.props.PointerProperty(type=bpy.types.Object, poll=lambda _, o: BL_MotorStage.is_motorstage(o)) # type: ignore


    # Experiment

    only_images : bpy.props.BoolProperty(name="Only Generate Images", description="Should only images be generated (no heightmap / calibration etc)", default=False) # type: ignore

    calibration_files : bpy.props.EnumProperty(name="Calibration", description="Calibration file to use for height reconstruction",
        items=get_experiment_items,
        default=None,
        get=None,
        set=None
    )  # type: ignore

# # # # # # # # # # # # # # # # # # # # # 
# Calibration

def update_ms_min(self, context):
    if self.min_height >= self.max_height:
        self.min_height = self.max_height

def update_ms_max(self, context):
    if self.max_height < self.min_height:
        self.max_height = self.min_height

class PG_MotorStageSettings(bpy.types.PropertyGroup):
    min_height : bpy.props.FloatProperty(name="Motor Stage Minimum Height", description="Min Motor Stage Height", min=0.0, update=update_ms_min, default=0.0) # type: ignore
    
    max_height : bpy.props.FloatProperty(name="Motor Stage Maximum Height", description="Max Motor Stage Height", min=0.0, update=update_ms_max, default=0.2) # type: ignore
    
    steps : bpy.props.IntProperty(name="Motor Stage Range Steps", description="Motor Stage Height Steps", min=2, default=2) # type: ignore


classes = [
    PG_Object,

    PG_ProjSettings,
    PG_CheckerboardSettings,
    PG_CameraSettings,

    # Experiment
    PG_Experiment,

    # Calibration,
    PG_MotorStageSettings,
]

def register():
    prof.register()

    for cls in classes:
        bpy.utils.register_class(cls)

    # SFDI Object Properties
    bpy.types.Object.proj_settings = bpy.props.PointerProperty(type=PG_ProjSettings)
    bpy.types.Object.camera_settings = bpy.props.PointerProperty(type=PG_CameraSettings)
    bpy.types.Object.cb_settings = bpy.props.PointerProperty(type=PG_CheckerboardSettings)

    bpy.types.Object.ms_settings = bpy.props.PointerProperty(type=PG_MotorStageSettings)

    # Experiment settings
    bpy.types.Scene.ex_settings = bpy.props.PointerProperty(type=PG_Experiment)

def unregister():
    prof.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Object.proj_settings
    del bpy.types.Object.camera_settings
    del bpy.types.Object.cb_settings

    del bpy.types.Object.ms_settings
    

    # Experiment settings
    del bpy.types.Scene.ex_settings