import numpy as np
import cv2
import bpy

import os
import logging

from time import perf_counter

from sfdi.video import Projector, Camera
from sfdi.definitions import ROOT_DIR
from sfdi.io.std import stdout_redirected

class BlenderProjector(Projector):
    def __init__(self, imgs=[], obj_name="ImageProjector"):
        super().__init__(imgs=imgs)

        self.obj_name = obj_name
        
        self.obj = bpy.data.objects[obj_name]
        self.proj_obj = bpy.data.objects[f'{obj_name}_']
        
        self.img_node = None
        for obj in self.proj_obj.data.node_tree.nodes:
            if obj.label == "ProjectionImage":
                self.img_node = obj
                break
        else:
            raise Exception("Couldn't find ProjectionImage Light Node (to set the projection texture)")

    def display(self): # Blender needs images in RGB format
        img = super().display()
        
        if img is None: return None
        
        self.logger.info("Projecting image")
        
        # Set the projector image to img
        b_image = bpy.data.images.new("ProjectionImage", width=img.shape[0], height=img.shape[1])
        
        img = (img.astype(np.float16)) / 255.0 # Blender needs images as float16s between 0 and 1
        
        b_image.pixels = img.ravel()
        
        self.img_node.image = b_image
        
        return b_image

class BlenderCamera(Camera):
    def __init__(self, camera_name='', resolution=(1280, 720), use_gpu=True):
        super().__init__(resolution=resolution)
            
        self.camera_name = camera_name
        
        # Need to use cycles for Blender
        bpy.data.scenes[0].render.engine = "CYCLES"
        
        if use_gpu:
            # Set the device and feature set
            bpy.context.scene.cycles.device = "GPU"
            
            bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
            bpy.context.preferences.addons["cycles"].preferences.get_devices()
            
            for d in bpy.context.preferences.addons["cycles"].preferences.devices:
                d["use"] = 1 # Using all devices, include GPU and CPU

        # Set camera resolution
        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]

    def capture(self):
        temp_path = os.path.join(ROOT_DIR, 'temp.jpg')
        
        bpy.context.scene.render.filepath = temp_path
        
        self.logger.info("Rendering camera image")
        
        calc_time = perf_counter()
        with stdout_redirected(): # Hide spam output
            bpy.ops.render.render(write_still=True)

        self.logger.info(f"Rendered in {(perf_counter() - calc_time):.2f} seconds")
        
        img = cv2.imread(temp_path)

        try:
            os.remove(temp_path)
        except:
            self.logger.error("Could not delete temporary render image file")

        return img
    
    def set_resolution(self, width, height):
        # Set camera resolution
        bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = width, height
        
        return self