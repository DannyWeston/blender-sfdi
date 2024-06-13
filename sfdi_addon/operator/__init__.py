import bpy
from . import camera, projector, object, calibration, fringe_proj

def register():
    camera.register()
    projector.register()
    object.register()
    calibration.register()
    fringe_proj.register()

def unregister():
    camera.unregister()
    projector.unregister()
    object.unregister()
    calibration.unregister()
    fringe_proj.unregister()