#!/usr/bin/python3

# Daniel Weston
# psydw2@nottingham.ac.uk
# OPTIMlab

import logging
import bpy

logging.basicConfig(
    level = logging.INFO, 
    format = "[%(levelname)s] %(message)s"
)

from tkinter import filedialog as fd

from sfdi.generation.fringes import Fringes
from sfdi.experiment import Experiment
from sfdi.io.repositories import ResultRepository, ImageRepository
from sfdi.io.std import stdout_redirected

from sfdi import rgb2grey, display_image, centre_crop_img
from sfdi.profilometry import ClassicPhaseHeight

from app.video import BlenderProjector, BlenderCamera

import cv2

def on_ref_finish(): bpy.data.objects[target_name].hide_render = False
def on_meas_finish(): bpy.data.objects[target_name].hide_render = True

if __name__ == "__main__":
    from app.args import handle_args
    args = handle_args()
    
    # Exit if can't load specified scene file
    logger = logging.getLogger('sfdi')
    
    render = False
    
    if render:
        try:
            filepath = fd.askopenfilename()
            
            with stdout_redirected():
                bpy.ops.wm.open_mainfile(filepath=filepath)

        except Exception as e:
            logger.error("Could not load blender file")
            quit()
        
        logger.info("Blender file successfully loaded")

        n = 3 # 3 Measurements per experiment
        fringes = Fringes.from_generator(2048, 2048, 32, n=n)
        
        target_name = "Sphere"
        
        projector = BlenderProjector(fringes)
        cameras = [BlenderCamera(f'camera')]
        
        exp = Experiment(
            cameras=cameras, 
            projector=projector, 
            ref_cbs=[on_ref_finish],
            meas_cbs=[on_meas_finish]
        )
        # Run the experiment and save the results
        expresult = exp.run(n)
        
        # Save the results
        repo = ResultRepository()
        repo.save(expresult)
        
        imgs = [img[0] for img in expresult.imgs]
        ref_imgs = [img[0] for img in expresult.ref_imgs]
    else:
        # Load the images from file
        img_repo = ImageRepository("D:\\git\\sfdi\\src\\sfdi\\data\\results\\20240208_233021")
        ref_imgs = [img_repo.load(f'cam0_refimg{i}.jpg') for i in range(3)]
        imgs = [img_repo.load(f'cam0_img{i}.jpg') for i in range(3)]
    
    import numpy as np
    print(np.min(imgs[0]), np.max(imgs[0]))
    
    # Show images
    for img in ref_imgs: display_image(img, title='Reference Images')
    for img in imgs: display_image(img, title='Measured Images')
    
    # Convert to greyscale
    ref_imgs = [rgb2grey(img) for img in ref_imgs]
    imgs = [rgb2grey(img) for img in imgs]
    
    # Crop to region of interest
    img_roi = (100, 320)    
    ref_imgs = [centre_crop_img(img, img_roi[0], img_roi[1]) for img in ref_imgs]
    imgs = [centre_crop_img(img, img_roi[0], img_roi[1]) for img in imgs]
    
    # Show processed images
    for img in ref_imgs: display_image(img, grey=True, title='Reference Images')
    for img in imgs: display_image(img, grey=True, title='Measured Images')

    # Calculate heightmap using converted to greyscale images
    spatial_freq = 0.032        # Pairs per mm (32 pairs / m = 32 p / 1000mm = 32 pairs per mm)
    ref_dist = 1000.0           # mm
    cam_plane_dist = 200.0      # mm

    heightmap = ClassicPhaseHeight(spatial_freq, ref_dist, cam_plane_dist).heightmap(ref_imgs, imgs)
    
    display_image(heightmap, grey=True, title='Heightmap')