import bpy

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

def register():
    properties.register()
    operators.register()
    ui.register()

def unregister():
    properties.unregister()
    operators.unregister()
    ui.unregister()
    
if __name__ == "__main__":
    register()