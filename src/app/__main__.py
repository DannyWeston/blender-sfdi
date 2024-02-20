#!/usr/bin/python3

# Daniel Weston
# psydw2@nottingham.ac.uk
# OPTIMlab

import numpy as np

from sfdi.fringes import Fringes
from sfdi.io.repositories import ResultRepository, ImageRepository

from sfdi import rgb2grey, display_image, centre_crop_img
from sfdi.profilometry import ClassicPhaseHeight, PolyPhaseHeight

from app.blender import BlenderExperiment, load_scene
from app.video import BlenderProjector, BlenderCamera

def show_images(imgs, title, grey=False):
    for img in imgs: display_image(img, title=title, grey=grey)

def main():
    from app.args import handle_args
    args = handle_args()
    
    # Try to load a blender scene which the user picks
    if not load_scene(): return
    
    render = True
    
    if render:
        n = 3 # 3 Measurements per experiment
        fringes = Fringes.from_generator(1024, 1024, 32, n=n) # 32 fringes (1024 / 32)
        
        projector = BlenderProjector(fringes)
        cameras = [BlenderCamera('Camera1'), BlenderCamera('Camera2')]
        
        exp = BlenderExperiment(
            cameras=cameras,
            projector=projector,
            target_names=["Sphere"],
            use_gpu=True,
            debug=args["debug"]
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
        path = f'C:\\git\\sfdi\\src\\sfdi\\data\\results\\20240220_154928'
        img_repo = ImageRepository(path)

        camera_count = 2    # Number of cameras
        img_count = 3       # Number of phases

        imgs = []
        ref_imgs = []

        for cam_i in range(camera_count):
            imgs.append([img_repo.load(f'cam{cam_i}_refimg{i}.jpg') for i in range(img_count)])
            ref_imgs.append([img_repo.load(f'cam{cam_i}_img{i}.jpg') for i in range(img_count)])

    # Show images
    if args["debug"]:
        for i, cam in enumerate(imgs): show_images(cam, f'Camera {i} - Measurement Image')
        for i, cam in enumerate(ref_imgs): show_images(cam, f'Camera {i} - Reference Image')
        
    # Convert to greyscale
    # Crop to region of interest
    img_roi = (100, 320)

    for cam_imgs in ref_imgs:
        for img_i in range(len(cam_imgs)):
            cam_imgs[img_i] = rgb2grey(cam_imgs[img_i])
            cam_imgs[img_i] = centre_crop_img(cam_imgs[img_i], img_roi[0], img_roi[1])

    for cam_imgs in imgs:
        for img_i in range(len(cam_imgs)):
            cam_imgs[img_i] = rgb2grey(cam_imgs[img_i])
            cam_imgs[img_i] = centre_crop_img(cam_imgs[img_i], img_roi[0], img_roi[1])
    
    # Show images
    if args["debug"]:
        for i, cam in enumerate(imgs): show_images(cam, f'Camera {i} - Images', True)
        for i, cam in enumerate(ref_imgs): show_images(cam, f'Camera {i} - Reference Images', True)

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