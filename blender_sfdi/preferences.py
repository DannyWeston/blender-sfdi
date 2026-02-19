import bpy
import addon_utils

from pathlib import Path
from bpy.types import AddonPreferences

def GetPreferences(context):
    return context.preferences.addons[__package__].preferences

def GetAddonPath():
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "BlenderSFDI":
            return Path(mod.__file__).parent
        
    return None

def GetStoragePath():
    path = Path(bpy.utils.extension_path_user(__package__, create=True))
    return path

def GetOutputPath():
    storage_path = GetStoragePath()

    path = storage_path / "output"

    path.mkdir(exist_ok=True)

    return path

class BlenderSFDIPreferences(AddonPreferences):
    bl_idname = __package__

    render_output: bpy.props.StringProperty(name="Render Output", subtype='DIR_PATH', default=str(GetOutputPath()), description="The directory to use for rendering")  # type: ignore

    def draw(self, context):
        self.layout.prop(self, "render_output")

ADDON_DIR = GetAddonPath()

ASSETS_DIR = ADDON_DIR / "assets"

def register():
    bpy.utils.register_class(BlenderSFDIPreferences)

def unregister():
    bpy.utils.unregister_class(BlenderSFDIPreferences)