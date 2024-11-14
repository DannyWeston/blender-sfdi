if "bpy" in locals():
    import importlib
    if "properties" in locals(): importlib.reload(properties)
    if "materials" in locals(): importlib.reload(materials)
    if "operators" in locals(): importlib.reload(operators)
    if "ui" in locals(): importlib.reload(ui)
else:
    import bpy
    from . import properties, operators, ui, materials

def register():
    properties.register()
    operators.register()
    ui.register()

def unregister():
    properties.unregister()
    operators.unregister()
    ui.unregister()