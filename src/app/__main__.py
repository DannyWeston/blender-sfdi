#!/usr/bin/python3

# Daniel Weston
# psydw2@nottingham.ac.uk
# OPTIMlab

import numpy as np
import cv2

from sfdi.fringes import Fringes
from sfdi.profilometry import PolyPhaseHeight, ClassicPhaseHeight
from sfdi.calibration import apply_correction
from sfdi.services import ResultService, CalibrationService
from sfdi import show_surface

from app.blender import BlenderExperiment, load_scene, render_with_gpu
from app.video import BlenderProjector, BlenderCamera
from app.args import handle_args

import matplotlib.pyplot as plt

def main():
    args = handle_args()
    if not load_scene(args['blend']): return
    render_with_gpu(args['use_gpu'])
    
    render = True
    if render:
        # Load calibration values
        cali_service = CalibrationService()
        
        camera_name = 'Camera1'
        projector_name = 'Projector1'

        gamma_calib, lens_calib, proj_calib = cali_service.load_calibrations(camera_name, projector_name)

        cam_mat = np.array(lens_calib["cam_mat"])
        dist_mat = np.array(lens_calib["dist_mat"])
        optimal_mat = np.array(lens_calib["optimal_mat"])
        camera = BlenderCamera(camera_name, (3840, 2160), cam_mat, dist_mat, optimal_mat)
        
        gamma_coeffs = np.array(gamma_calib["coeffs"])
        gamma_visible = np.array(gamma_calib["visible_intensities"])

        phases = 3
        period = 16 # Pixels per period
        width = 2048

        fringes = Fringes.from_generator(width, width, period, 0, n=phases)
        #fringes = [apply_correction(img, gamma_coeffs, np.min(gamma_visible), np.max(gamma_visible)) for img in fringes]
        fringes = Fringes(fringes)
        projector = BlenderProjector(fringes, projector_name)

        cameras = [camera]
        exp = BlenderExperiment(
            cameras=cameras,
            projector=projector,
            target_names=["Sphere"]
        )

        # Run the experiment and save the results
        ref_imgs, imgs = exp.run(phases)
        
        res_service = ResultService.default()
        res_data = {}
        res_data["cameras"] = { camera.name: {"resolution": camera.resolution, "samples": camera.samples } for camera in cameras }
        res_data["projectors"] = { projector.name: {} }
        res_data["phases"] = phases
        res_data["cam_count"] = len(cameras)
        res_data["period"] = period
        res_data["width"] = width
        
        res_service.save_data(res_data, fringes, imgs, ref_imgs)
    else:
        res_service = ResultService.default('phase3_period16')
        ref_imgs, imgs, data = res_service.load_data()
        
        phases = data["phases"]
        period = data["period"]
        width = data["width"]
        
        cameras = [BlenderCamera(name, resolution=v["resolution"], samples=v["samples"]) for name, v in data["cameras"].items()]
        projectors = [BlenderProjector(name) for name, v in data["projectors"].items()]
        
        # TODO: FIX
        projector = projectors[0]
        camera = cameras[0]

    # Calculate heightmap using ClassicPhaseHeight technique
    l = 0.95076 * 1000 # mm
    d = abs((camera.get_pos() - projector.get_pos()).length) * 1000.0 # mm
    sf = 1.0 / ((0.950317 * 1000.0) / ((width / period) - 1.0)) #mm^-1

    ph = ClassicPhaseHeight(sf, d, l)

    heightmaps = []
    for cam_i in range(len(imgs)):
        heightmap = ph.heightmap(ref_imgs[cam_i], imgs[cam_i], grey=True, crop=(0.33, 0.33, 0.33, 0.25))
        heightmap = cv2.medianBlur(heightmap, 5) # Apply median filter to smooth out peaks
        show_surface(heightmap)
        heightmaps.append(heightmap)

if __name__ == "__main__":
    main()