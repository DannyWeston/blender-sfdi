if "bpy" in locals():
    import importlib
    if "properties" in locals(): importlib.reload(properties)
    if "devices" in locals(): importlib.reload(devices)
    if "assets" in locals(): importlib.reload(assets)
    if "operators" in locals(): importlib.reload(operators)
    if "ui" in locals(): importlib.reload(ui)
    if "preferences" in locals(): importlib.reload(preferences)
else:
    import bpy
    from . import properties, operators, ui, preferences, assets, devices

def register():
    properties.register()
    operators.register()
    ui.register()
    preferences.register()
    assets.register()
    devices.register()

def unregister():
    preferences.unregister()
    properties.unregister()
    operators.unregister()
    ui.unregister()
    assets.unregister()
    devices.unregister()