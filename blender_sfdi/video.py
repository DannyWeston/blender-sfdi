import numpy as np
import cv2
import bpy

import os

from time import perf_counter

from opensfdi.video import FringeProjector, Camera
from opensfdi.definitions import ROOT_DIR
from opensfdi.io.std import stdout_redirected

class BL_FringeProjector(FringeProjector):
    def __init__(self, name, frequency, orientation, resolution, phases=[]):
        super().__init__(name, frequency, orientation, resolution, phases)
        
        self.light_obj = bpy.data.objects[name]

    def display(self):
        # Don't actually need to do anything because the Blender Renderer handles the image projection for us
        # When changing the phase
        self.logger.debug("Projecting image")
        
        # Set the projector image to img
        # b_image = bpy.data.images.new("ProjectionImage", width=img.shape[0], height=img.shape[1])
        
        # img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA) # Blender needs alpha channel
        # img = img.astype(np.float16) # Blender needs images as float16s between 0 and 1
        
        # b_image.pixels = img.ravel()
        
        # self.img_node.image = b_image
        
    def next(self):
        super().next()

        # Update the phase in Blender
        self.light_obj.data["Phase"] = self.get_phase()
        
        print(self.light_obj.data["Phase"])
            
    def get_pos(self):
        return self.light_obj.matrix_world.to_translation()

    @staticmethod
    def from_proj_obj(proj_obj):
        data = proj_obj.data
        return BL_FringeProjector(name=proj_obj.name,
                                    frequency=data["Spatial Frequency"], 
                                    orientation=data["Rotation"],
                                    resolution=tuple(data["Resolution"]))

class BL_Camera(Camera):
    def __init__(self, name='Camera1', resolution=(1920, 1080), cam_mat=None, dist_mat=None, optimal_mat=None, samples=16):
        super().__init__(resolution=resolution, name='Camera1', cam_mat=cam_mat, dist_mat=dist_mat, optimal_mat=optimal_mat)

        self.camera = bpy.data.objects[name]
        
        self.samples = samples
        
        # Set the number of samples for the active scene
        bpy.data.scenes[0].cycles.samples = samples

    def capture(self):
        scene = bpy.context.scene
        
        # Need to set this camera as the renderer to be safe
        scene.camera = self.camera

        # Set scene render resolution to this camera's resolution
        scene.render.resolution_x = self.resolution[0]
        scene.render.resolution_y = self.resolution[1]

        # Render scene to temporary file
        old_filetype = scene.render.image_settings.file_format
        old_quality = scene.render.image_settings.quality
        
        # JPEG with max quality (no compression)
        scene.render.image_settings.file_format = 'JPEG'
        scene.render.image_settings.quality = 100
        
        # TODO: Change to addon_dir
        temp_path = os.path.join(ROOT_DIR, f'{self.name}_temp.jpg')
        #temp_path = os.path.join('C:\\Users\\danie\\Desktop', f'{self.name}_temp.jpg')
        scene.render.filepath = temp_path
        
        self.logger.debug("Rendering camera image")
        
        calc_time = perf_counter()
        with stdout_redirected():
            bpy.ops.render.render(write_still=True)
        
        # Reset old parameters
        scene.render.image_settings.file_format = old_filetype
        scene.render.image_settings.quality = old_quality

        self.logger.debug(f"Rendered in {(perf_counter() - calc_time):.2f} seconds")
        
        # Load rendered image from disk and convert to correct range (delete old image)
        img = cv2.imread(temp_path)
        img = img.astype(np.float32) / 255.0

        # try:
        #     os.remove(temp_path)
        # except:
        #     self.logger.error("Could not delete temporary render image file")

        return img
    
    def get_pos(self):
        return self.camera.matrix_world.to_translation()

    def set_resolution(self, width, height):
        self.resolution = width, height

        return self
 
class CameraFactory:
    @staticmethod
    def DefaultCamera():
        return None