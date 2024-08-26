import addon_utils

from pathlib import Path

def get_addon_path():
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "blender_sfdi":
            return Path(mod.__file__).parent
        
    return None

ADDON_DIR = get_addon_path()

ASSETS_DIR = ADDON_DIR / "assets"

MODELS_DIR = ASSETS_DIR / "models"