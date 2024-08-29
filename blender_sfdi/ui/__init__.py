from . import projector, camera, fringe_proj, object, calibration

def register():
    projector.register()
    camera.register()
    calibration.register()

    fringe_proj.register()
    object.register()

def unregister():
    projector.unregister()
    camera.unregister()
    calibration.unregister()

    fringe_proj.unregister()
    object.unregister()