import numpy as np
import cv2
import bpy

import os

from time import perf_counter

from sfdi.video import Projector, Camera
from sfdi.definitions import ROOT_DIR
from sfdi.io.std import stdout_redirected

class BlenderProjector(Projector):
    def __init__(self, imgs=[], name='Projector1'):
        super().__init__(imgs=imgs, name='Projector1')
    
        self.obj = bpy.data.objects[name]
        self.model_obj = bpy.data.objects[f'{name}_']
        
        self.img_node = None
        for obj in self.obj.data.node_tree.nodes:
            if obj.label == "ProjectionImage":
                self.img_node = obj
                break
        else:
            raise Exception("Couldn't find ProjectionImage Light Node (to set the projection texture)")

    def display(self): # Blender needs images in RGB format
        img = super().display()
        
        if img is None: return None
        
        self.logger.debug("Projecting image")
        
        # Set the projector image to img
        b_image = bpy.data.images.new("ProjectionImage", width=img.shape[0], height=img.shape[1])
        
        img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA) # Blender needs alpha channel
        img = img.astype(np.float16) # Blender needs images as float16s between 0 and 1
        
        b_image.pixels = img.ravel()
        
        self.img_node.image = b_image
        
        return b_image

    def enabled(self, value):
        self.obj.hide_render = not value
        
    def get_pos(self):
        return self.obj.matrix_world.to_translation()

class BlenderCamera(Camera):
    def __init__(self, name='Camera1', resolution=(1920, 1080), cam_mat=None, dist_mat=None, optimal_mat=None, samples=16):
        super().__init__(resolution=resolution, name='Camera1', cam_mat=cam_mat, dist_mat=dist_mat, optimal_mat=optimal_mat)

        self.obj = bpy.data.objects[name]
        self.camera_obj = bpy.data.objects[f'{name}_']
        
        self.samples = samples
        
        # Set the number of samples
        bpy.data.scenes[0].cycles.samples = samples

    def capture(self):
        # Need to set this camera as the renderer to be safe
        bpy.context.scene.camera = self.camera_obj

        # Set scene render resolution to this camera's resolution
        bpy.context.scene.render.resolution_x = self.resolution[0]
        bpy.context.scene.render.resolution_y = self.resolution[1]

        # Render scene to temporary file

        temp_path = os.path.join(ROOT_DIR, f'{self.name}_temp.jpg')
        
        bpy.context.scene.render.filepath = temp_path
        
        self.logger.debug("Rendering camera image")
        
        calc_time = perf_counter()
        with stdout_redirected(): # Hide spam output
            bpy.ops.render.render(write_still=True)

        self.logger.debug(f"Rendered in {(perf_counter() - calc_time):.2f} seconds")
        
        img = cv2.imread(temp_path) # Reload image from disk
        img = img.astype(np.float32) / 255.0 # Convert to float32 0.0 <= img <= 1.0

        try:
            os.remove(temp_path)
        except:
            self.logger.error("Could not delete temporary render image file")

        return img
    
    def get_pos(self):
        return self.camera_obj.matrix_world.to_translation()

    def set_resolution(self, width, height):
        self.resolution = width, height

        return self
    

class CameraFactory:
    @staticmethod
    def DefaultCamera():
        return None