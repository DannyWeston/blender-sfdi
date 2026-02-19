# Fringe Projection in Blender

## Overview

This repository consists of the source code for a Blender 5.0+ extension. 

This extension adds functionality in Blender to create different camera-projector configurations for fringe projection and gather large simulated datasets. It is possible to render results in real-time (~20fps tested on RTX2080Ti, 1080p, low-medium density scene), but it heavily dependent upon scene quality and the number of ray-samples chosen. Functionality for creating characterisation boards for the Zhang process are also included by default.

Currently managed by Daniel Weston, University of Nottingham, Optics and Photonics. For any questions please contact by email (psydw2@nottingham.ac.uk). 


## Setup

1. Download the latest release.

2. Navigate to "Edit > Preferences > Get Extensions" within your Blender installation.

3. At the top right, there is a small drop down arrow, click it and then click "Install from Disk..."

4. Close the preferences menu, press "N" on the keyboard, and the "SFDI" menu should be visible on the right side.


## Requirements

For the installation of this addon you will need a Windows or Linux-based operating system, and Blender version 5.0+. 

As this extension only works with the Cycles renderer, it is strongly recommend to use an nVidia RTX-capable GPU to speed up the render times. Note that it is possible to render on any CPU/GPU, but will be at a reduced speed. There are some settings in Blender which cause poor quality data to be generated if they are not changed. In the source code there is a "fringe_projection.blend" file which comes with all of these values correctly configured and an example system.

### Blender Settings Requirements
- Cycles rendering engine ONLY.
- Dithering disabled.
- Colour spaces set to raw linear (if not, you must complete gamma calibration!).
- Denoising disabled (it produces artifacts on rendered images).

### Blender Optional Settings
- World background colour disabled - a small amount of background light is present by default even when there are no lights present within the scene.
- Viewport samples ~64 - speed up the rendering of the viewport a little.
- If using RTX-capable card, the OptiX renderer should be enabled in "Edit > Preferences > System" to make use of the acceleration.
- Final render persistent data - use more GPU memory for faster renders. May require some experimentation.