from . import devices, fringe_projection

def register():
    fringe_projection.register()
    devices.register()

def unregister():
    fringe_projection.unregister()
    devices.unregister()