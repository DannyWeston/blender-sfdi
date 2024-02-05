#!/usr/bin/python3

# Daniel Weston
# psydw2@nottingham.ac.uk
# OPTIMlab

import logging
import os

logging.basicConfig(
    level = logging.INFO, 
    format = "[%(levelname)s] %(message)s"
)

# Use this application folder as the program's root
from sfdi.definitions import update_root, ROOT_DIR
update_root(os.path.dirname(os.path.abspath(__file__)))

from sfdi.experiment import Experiment
from app.video import BlenderProjector, BlenderCamera

from app.blender import load_scene

def after_ref():
    import bpy
    
    target_obj = bpy.data.objects["Sphere"]
    target_obj.hide_render = False

if __name__ == "__main__":
    from app.args import handle_args
    args = handle_args()
    
    if not load_scene(): 
        quit() # Exit if can't load specified scene file

    p = Experiment( camera=BlenderCamera(),
                    projector=BlenderProjector(),
                    debug=args["debug"]
    )
    
    p.ref_cbs.append(after_ref)

    # Run the experiment with some parameters
    p.run(  args["refr_index"],
            args["mu_a"],
            args["mu_sp"],
            args["runs"],
    )