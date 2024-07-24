import bpy
import sfdi
import os

from . import operator, ui, properties, blender, video, materials

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
    if "sfdi" in locals(): importlib.reload(sfdi)
    
    if "operator" in locals(): importlib.reload(operator)
    if "ui" in locals(): importlib.reload(ui)
    
    if "blender" in locals(): importlib.reload(blender)
    if "properties" in locals(): importlib.reload(properties)
    if "video" in locals(): importlib.reload(video)
    if "materials" in locals(): importlib.reload(materials)

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
    operator.register()
    ui.register()

def unregister():
    properties.unregister()
    operator.unregister()
    ui.unregister()

if __name__ == "__main__":
    register()