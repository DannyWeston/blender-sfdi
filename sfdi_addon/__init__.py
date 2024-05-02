import bpy
import sfdi

import os

from sfdi_addon import operators, ui, properties

bl_info = {
    "name": "Fringe Projection",
    "description": "TODO: Description goes here",
    "author": "Daniel Weston",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "category": "Development",
}

if "bpy" in locals():
    import importlib
    
    if "operators" in locals(): importlib.reload(operators)
    if "ui" in locals(): importlib.reload(ui)
    if "properties" in locals(): importlib.reload(properties)
    if "video" in locals(): importlib.reload(video)
    if "experiment" in locals(): importlib.reload(experiment)
    if "blender" in locals(): importlib.reload(blender)
    if "sfdi" in locals(): importlib.reload(sfdi)

def get_addon_dir():
    import addon_utils
    for mod in addon_utils.modules():
        if mod.bl_info.get("name") == "Fringe Projection":
            return os.path.dirname(mod.__file__)

    return None

def register():
    addon_dir = get_addon_dir()
    if addon_dir: sfdi.definitions.ROOT_DIR = addon_dir
    
    print(f"SFDI ROOT_DIR set as {sfdi.definitions.ROOT_DIR}")
        
    properties.register()
    operators.register()
    ui.register()

def unregister():
    properties.unregister()
    operators.unregister()
    ui.unregister()
    
if __name__ == "__main__":
    register()