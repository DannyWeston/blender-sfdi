import bpy
import logging

from sfdi.experiment import Experiment
from sfdi.calibration import CameraCalibration, GammaCalibration
from sfdi.io.std import stdout_redirected

def load_scene(blend_path):
    logger = logging.getLogger("sfdi")

    if blend_path is None or blend_path == '':
        return False
            
    try:
        with stdout_redirected():
            bpy.ops.wm.open_mainfile(filepath=blend_path)

    except Exception as e:
        logger.error(e)
        return False
    
    logger.info("Successfully loaded blender file")
    
    # Need to use cycles for Blender
    bpy.data.scenes[0].render.engine = "CYCLES"
    
    return True

def render_with_gpu(value):
    logger = logging.getLogger("sfdi")
    
    if value:
        # Set the device and feature set
        bpy.context.scene.cycles.device = "GPU"
        
        bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
        bpy.context.preferences.addons["cycles"].preferences.get_devices()
        
        logger.info("Using GPU to render images with Blender")
        
        # for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        #     d["use"] = 1 # Using all devices, include GPU and CPU

class BlenderGammaCalibration(GammaCalibration):
    def __init__(self, camera, projector, delta, crop_size=0.25, order=5, intensity_count=32):
        super().__init__(camera, projector, delta, crop_size, order, intensity_count)
    
    def calibrate(self):
        self.projector.enabled(True)
        result = super().calibrate()
        self.projector.enabled(False)
        
        return result

class BlenderCameraCalibration(CameraCalibration):
    def __init__(self, camera, img_count=10, cb_size=(8, 6), cb_name='Checkerboard'):
        super().__init__(camera, img_count, cb_size)
        
        self._cb_name = cb_name
        
        self._cb_obj = bpy.data.objects[cb_name]
        
        self._set_cb_orientation(0)
        
    def calibrate(self):
        self._cb_obj.hide_render = False
        result = super().calibrate()
        self._cb_obj.hide_render = True
        
        return result

    def on_checkerboard_change(self, i):
        self._set_cb_orientation(i + 1)

    def _set_cb_orientation(self, seed):
        self.logger.debug("Generating new checkerboard orientation")
        self._cb_obj.modifiers["GeometryNodes"]["Input_5"] = seed
        self._cb_obj.data.update()

class BlenderExperiment(Experiment):
    def __init__(self, cameras, projector, target_names):
        super().__init__(cameras, projector, 0.0)

        # Set objects to hide for reference measurements
        self.target_names = target_names

        self.show_objects(False) # Hide objects ready for reference images

    def show_objects(self, value):
        for name in self.target_names:
            bpy.data.objects[name].hide_render = (not value)

    def run(self, n=3):
        self.show_objects(False)
        self.projector.enabled(True)
        
        result = super().run(n)
        
        self.show_objects(False)
        self.projector.enabled(False)
        
        return result

    def on_ref_finish(self):
        self.show_objects(True)