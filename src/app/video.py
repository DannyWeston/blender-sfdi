import numpy as np
import cv2
import bpy

import os
import logging

from sfdi.video import Projector, Camera
from sfdi.definitions import ROOT_DIR
from app.blender import stdout_redirected

class BlenderProjector(Projector):
    def __init__(self, obj_name="ImageProjector"):    
        self.obj_name = obj_name
        
        self.obj = bpy.data.objects[obj_name]
        self.proj_obj = bpy.data.objects[f'{obj_name}_']

    def display(self, img): # Blender needs images in RGB format
        img_node = None
        for obj in self.proj_obj.data.node_tree.nodes:
            if obj.label == "ProjectionImage":
                img_node = obj
                break
        else:
            raise Exception("Couldn't find ProjectionImage Light Node (to set the projection texture)")
        
        # Put image in correct format for Blender
        #resized_img = cv2.resize(img, dsize=(self.width, self.height), interpolation=cv2.INTER_CUBIC)
        
        #cv2.imshow('Test', resized_img)
        #cv2.waitKey(0)
        
        # Set the projector image to img
        b_image = bpy.data.images.new("ProjectionImage", width=img.shape[0], height=img.shape[1])
        
        img = (img.astype(np.float16)) / 255.0 # Blender needs images as float16s between 0 and 1
        
        b_image.pixels = img.ravel()
        
        img_node.image = b_image

class BlenderCamera(Camera):
    def __init__(self, resolution=(1280, 720), use_gpu=True):
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
        
        with stdout_redirected():
            bpy.ops.render.render(write_still=True)
        
        img = cv2.imread(temp_path)

        try: 
            os.remove(temp_path)
        except: 
            print("Could not delete temporary render image file")

        return cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    
    def set_resolution(self, width, height):
        # Set camera resolution
        bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = width, height
        
        return self