import bpy
import addon_utils

from pathlib import Path

def get_addon_path():
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "blender_sfdi":
            return Path(mod.__file__).parent
        
    return None

def get_storage_path():
    path = Path(bpy.utils.extension_path_user(__package__, create=True))
    return path

ADDON_DIR = get_addon_path()

ASSETS_DIR = ADDON_DIR / "assets"

MODELS_DIR = ASSETS_DIR / "models"