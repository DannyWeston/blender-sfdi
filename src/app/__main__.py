#!/usr/bin/python3

# Daniel Weston
# psydw2@nottingham.ac.uk
# OPTIMlab

import numpy as np

import sfdi

from sfdi.fringes import Fringes
from sfdi.io.repositories import ResultRepository, ImageRepository
from sfdi.calibration.geometric import camera_calibration
from sfdi.profilometry import PolyPhaseHeight, ClassicPhaseHeight
from sfdi.definitions import CALIBRATION_DIR

from app.blender import BlenderExperiment
from app.video import BlenderProjector, BlenderCamera
from app.args import handle_args

# Last camera calibration results:
# Camera matrix:      [[1.23885305e+03,   0.00000000e+00,     6.16820237e+02],
#                     [0.00000000e+00,    1.23411087e+03,     3.62838367e+02],
#                     [0.00000000e+00,    0.00000000e+00,     1.00000000e+00]]

# Dist matrix:        [[-0.0140819,       0.12176221,         -0.00068668,         -0.00381937,       -0.32111301]]

# Optimal matrix:     [[1.23257834e+03,   0.00000000e+00,     6.11851257e+02],
#                     [0.00000000e+00,    1.22242477e+03,     3.62396200e+02],
#                     [0.00000000e+00,    0.00000000e+00,     1.00000000e+00]]

def main():
    args = handle_args()
    
    # Calibrate the camera
    
    # ir = ImageRepository(CALIBRATION_DIR)
    
    # cb_imgs = []
    # for i in range(16):
    #     img = ir.load(f'checkerboard_{i}.jpg')
    #     if img is not None: cb_imgs.append(img)
    
    # camera_calibration(cb_imgs)
    
    # Calibrate the projector

    render = True
    
    if render:
        # Try to load a blender scene which the user picks
        if not BlenderExperiment.load_scene(args['blend']):
            return
        
        n = 3 # 3 Measurements per experiment
        fringes = Fringes.from_generator(1024, 1024, 32, 0, n=n) # 32 fringes (1024 / 32)
        
        projector = BlenderProjector(fringes)
        cameras = [BlenderCamera('Camera1')]
        
        exp = BlenderExperiment(
            cameras=cameras,
            projector=projector,
            target_names=["Sphere"],
            use_gpu=args["use_gpu"]
        )

        # Run the experiment and save the results
        expresult = exp.run(n)
        
        # Save the results
        repo = ResultRepository()
        repo.save(expresult)
        
        imgs = expresult.imgs
        ref_imgs = expresult.ref_imgs
    else:
        # Load the images from file
        path = f'D:\\git\\sfdi\\src\\sfdi\\data\\results\\20240220_220551'
        img_repo = ImageRepository(path)

        camera_count = 2    # Number of cameras
        img_count = 3       # Number of phases

        imgs = []
        ref_imgs = []

        for i in range(img_count):
            imgs.append([img_repo.load(f'cam{cam_i}_img{i}.jpg') for cam_i in range(camera_count)])
            ref_imgs.append([img_repo.load(f'cam{cam_i}_refimg{i}.jpg') for cam_i in range(camera_count)])

    # Convert to greyscale
    # Crop to region of interest
    img_roi = (100, 320)

    for phase in ref_imgs:
        for cam in range(len(phase)):
            phase[cam] = sfdi.rgb2grey(phase[cam])
            phase[cam] = sfdi.centre_crop_img(phase[cam], img_roi[0], img_roi[1])

    for phase in imgs:
        for cam in range(len(phase)):
            phase[cam] = sfdi.rgb2grey(phase[cam])
            phase[cam] = sfdi.centre_crop_img(phase[cam], img_roi[0], img_roi[1])
                

    # Calculate heightmap using ClassPhaseHeight technique
    sf = 32                     # Roughly 32 pairs per meter
    ref_dist = 1                # m
    sensor_dist = 0.2           # m

    ph = ClassicPhaseHeight(ref_dist, sensor_dist, sf)

    heightmap = ph.heightmap(ref_imgs[0], imgs[0])

    sfdi.display_image(heightmap, True,'Classic Phase-to-Heightmap Result',
                       np.min(heightmap), np.max(heightmap))
    
    return

    # TODO: Fix polynomial calibration

    #c_heightmap = ClassicPhaseHeight(spatial_freq, ref_dist, cam_plane_dist).heightmap(ref_imgs, imgs)
    #h_min, h_max = np.min(c_heightmap), np.max(c_heightmap)
    #display_image(c_heightmap, grey=True, title='Heightmap', vmin=h_min, vmax=h_max)
    

    poly_heightmap = PolyPhaseHeight()
    
    calibrate = True
    if calibrate:
        # Load heightmap
        img_repo = ImageRepository('C:\\Users\\psydw2\\Desktop\\')
        heightmaps = [img_repo.load(f'heightmap.jpg')]

        # Drop GB channels if present (assume they are all equal)
        if heightmaps[0].shape[2] == 3: heightmaps[0] = heightmaps[0][:,:,0]

        # Crop to same size as images
        heightmaps[0] = centre_crop_img(heightmaps[0], img_roi[0], img_roi[1]) 

        poly_heightmap = PolyPhaseHeight()
        best = []
        best_score = float('inf')

        for i in range(2, 10):
            coeffs, score = poly_heightmap.calibrate(heightmaps[0], ref_imgs[0], imgs[0], deg=i)
            if score < best_score:
                best_score = score
                best = coeffs

        print(best)
        print(f'SSR: {best_score}')
    else:
        coeffs = [28.3603171, -5.37344553, 0.232223233, -0.00228115047]
        polyheight = PolyPhaseHeight(coeffs)
        poly_heightmap = polyheight.heightmap(ref_imgs[0], imgs[0])
        poly_heightmap[poly_heightmap < 0] = 0

        poly_min, poly_max = np.min(poly_heightmap), np.max(poly_heightmap)
        print(poly_min, poly_max)

        display_image(poly_heightmap, grey=True, title='PolyPhaseHeight Result', vmin=poly_min, vmax=poly_max)

if __name__ == "__main__":
    main()