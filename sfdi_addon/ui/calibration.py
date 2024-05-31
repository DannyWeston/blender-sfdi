import bpy
from bpy.types import Operator

class OP_AddCheckerboard(Operator):
    bl_idname = "op.add_checkerboard"
    bl_label = "Checkerboard"

    def execute(self, context):
        # Add the stuff
        
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
