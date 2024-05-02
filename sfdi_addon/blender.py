import bpy
import logging

from sfdi.experiment import Experiment
from sfdi.calibration import CameraCalibration, GammaCalibration
from sfdi.io.std import stdout_redirected

from mathutils import Vector

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