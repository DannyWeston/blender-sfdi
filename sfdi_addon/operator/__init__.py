import bpy
from . import camera, projector, object

def register():
    camera.register()
    projector.register()
    object.register()
    
def unregister():
    camera.unregister()
    projector.unregister()
    object.unregister()
        