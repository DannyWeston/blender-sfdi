import bpy
import logging

from tkinter import filedialog as fd

from sfdi.experiment import Experiment
from sfdi.io.std import stdout_redirected

def load_scene():
    logger = logging.getLogger("sfdi")
            
    try:
        filepath = fd.askopenfilename()
        with stdout_redirected():
            bpy.ops.wm.open_mainfile(filepath=filepath)

    except Exception as e:
        logger.error(e)
        return False
    
    logger.info("Successfully loaded blender file")
    
    return True

class BlenderExperiment(Experiment):
    def __init__(self, cameras, projector, target_names, use_gpu=False):
        super().__init__(cameras, projector, 0.0)

        # Set objects to hide for reference measurements
        self.target_names = target_names

        # Need to use cycles for Blender
        bpy.data.scenes[0].render.engine = "CYCLES"

        self.use_gpu(use_gpu) # Set GPU rendering or not

        self.show_objects(False) # Hide objects ready for reference images

    def show_objects(self, value):
        for name in self.target_names:
            bpy.data.objects[name].hide_render = (not value)

    def use_gpu(self, value):
        if value:
            # Set the device and feature set
            bpy.context.scene.cycles.device = "GPU"
            
            bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
            bpy.context.preferences.addons["cycles"].preferences.get_devices()
            
            # for d in bpy.context.preferences.addons["cycles"].preferences.devices:
            #     d["use"] = 1 # Using all devices, include GPU and CPU

    def on_ref_finish(self):
        self.logger.debug('Attempting to show target objects')
        self.show_objects(True)

    def on_measurement_finish(self):
        self.logger.debug('Attempting to hide target objects')
        self.show_objects(False)