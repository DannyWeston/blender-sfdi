import bpy
from . import projector, camera, fringe_proj, object

def register():
    projector.register()
    camera.register()
    fringe_proj.register()
    object.register()

def unregister():
    projector.unregister()
    camera.unregister()
    fringe_proj.unregister()
    object.unregister()