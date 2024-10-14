from . import camera, projector, calibration, experiment

def register():
    camera.register()
    projector.register()
    calibration.register()
    experiment.register()

def unregister():
    camera.unregister()
    projector.unregister()
    calibration.unregister()
    experiment.unregister()