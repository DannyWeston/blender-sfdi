import bpy
import opensfdi

from . import properties, operators, ui

if "bpy" in locals():
    import importlib
    if "opensfdi" in locals(): importlib.reload(opensfdi)

    if "properties" in locals(): importlib.reload(properties)
    if "operator" in locals(): importlib.reload(operators)
    if "ui" in locals(): importlib.reload(ui)

def get_storage_dir():
    # Create an addon directory if it doesn't exist
    return bpy.utils.extension_path_user(__package__, create=True)

def register():
    # Set SFDI root directory to correct place (create folder structure also)
    opensfdi.definitions.update_root(get_storage_dir(), True)

    properties.register()
    operators.register()
    ui.register()

def unregister():
    properties.unregister()
    operators.unregister()
    ui.unregister()