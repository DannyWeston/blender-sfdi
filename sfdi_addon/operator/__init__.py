import bpy
from . import camera, projector, object, calibration

def register():
    camera.register()
    projector.register()
    object.register()
    calibration.register()

def unregister():
    camera.unregister()
    projector.unregister()
    object.unregister()
    calibration.unregister()