#!/usr/bin/python3

# Daniel Weston
# psydw2@nottingham.ac.uk
# OPTIMlab

import numpy as np

import sfdi

from sfdi.services import CalibrationService

from app.blender import BlenderCameraCalibration, BlenderGammaCalibration, load_scene, render_with_gpu
from app.video import BlenderCamera, BlenderProjector
from app.args import handle_args

# Last camera calibration results:
def main():
    args = handle_args()
    if not load_scene(args['blend']): return

    render_with_gpu(args['use_gpu'])
    
    cali_serv = CalibrationService()

    # Calibrate the gamma for each camera
    proj = BlenderProjector()
    cameras = [BlenderCamera('Camera1', (1920, 1080), samples=16)]
    for cam in cameras:
        gamma_cali = BlenderGammaCalibration(cam, proj, delta=0.001, crop_size=0.25, order=4, intensity_count=32)
        cam_cali = BlenderCameraCalibration(cam, img_count=10, cb_size=(8, 6), cb_name='Checkerboard')
        
        gamma_cali.calibrate()
        cam_cali.calibrate()
        
        cali_serv.save_calibrations(gamma_cali, cam_cali)

if __name__ == "__main__":
    main()