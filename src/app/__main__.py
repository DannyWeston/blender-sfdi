#!/usr/bin/python3

# Daniel Weston
# psydw2@nottingham.ac.uk
# OPTIMlab

import logging
import bpy
import numpy as np

logging.basicConfig(
    level = logging.INFO, 
    format = "[%(levelname)s] %(message)s"
)

from tkinter import filedialog as fd

from sfdi.fringes import Fringes
from sfdi.experiment import Experiment
from sfdi.io.repositories import ResultRepository, ImageRepository
from sfdi.io.std import stdout_redirected

from sfdi import rgb2grey, display_image, centre_crop_img
from sfdi.profilometry import ClassicPhaseHeight, PolyPhaseHeight

from app.video import BlenderProjector, BlenderCamera

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
        cameras = [BlenderCamera(f'camera', use_gpu=False)]
        
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
        path = f'C:\\git\\sfdi\\src\\sfdi\\data\\results\\20240213_145944'
        img_repo = ImageRepository(path)
        ref_imgs = [img_repo.load(f'cam0_refimg{i}.jpg') for i in range(3)]
        imgs = [img_repo.load(f'cam0_img{i}.jpg') for i in range(3)]
    
    # Show images
    if args["debug"]:
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
    if args["debug"]:
        for img in ref_imgs: display_image(img, grey=True, title='Reference Images')
        for img in imgs: display_image(img, grey=True, title='Measured Images')

    # Calculate heightmap using converted to greyscale images
    spatial_freq = 0.032        # Pairs per mm (32 pairs / m = 32 p / 1000mm = 32 pairs per mm)
    ref_dist = 1000.0           # mm
    cam_plane_dist = 200.0      # mm

    #c_heightmap = ClassicPhaseHeight(spatial_freq, ref_dist, cam_plane_dist).heightmap(ref_imgs, imgs)
    #h_min, h_max = np.min(c_heightmap), np.max(c_heightmap)
    #display_image(c_heightmap, grey=True, title='Heightmap', vmin=h_min, vmax=h_max)

    poly_heightmap = PolyPhaseHeight()

    calibrate = True
    if calibrate:
        # Load heightmap
        img_repo = ImageRepository('C:\\Users\\psydw2\\Desktop\\')
        heightmap = img_repo.load(f'heightmap.jpg')

        # Drop GB channels if present (assume they are all equal)
        if heightmap.shape[2] == 3: heightmap = heightmap[:,:,0]

        # Crop to same size as images
        heightmap = centre_crop_img(heightmap, img_roi[0], img_roi[1]) 

        poly_heightmap = PolyPhaseHeight()
        best = []
        best_score = float('inf')

        for i in range(2, 10):
            coeffs, score = poly_heightmap.calibrate(heightmap, ref_imgs, imgs, deg=i)
            if score < best_score:
                best_score = score
                best = coeffs

        print(best)
        print(best_score)
    else:
        coeffs = [28.3603171, -5.37344553, 0.232223233, -0.00228115047]
        polyheight = PolyPhaseHeight(coeffs)
        poly_heightmap = polyheight.heightmap(ref_imgs, imgs)
        poly_heightmap[poly_heightmap < 0] = 0

        poly_min, poly_max = np.min(poly_heightmap), np.max(poly_heightmap)
        print(poly_min, poly_max)

        display_image(poly_heightmap, grey=True, title='PolyPhaseHeight Result', vmin=poly_min, vmax=poly_max)