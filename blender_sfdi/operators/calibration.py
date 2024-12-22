import bpy
from bpy.types import Operator

from ..blender import BL_Checkerboard

class OP_AddCheckerboard(Operator):
    bl_idname = "menu.add_checkerboard"
    bl_label = "Checkerboard"

    bl_options = {'REGISTER', 'UNDO'}
    
    # TODO: Investigate subtype vs units
    location: bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore

    rotation: bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        BL_Checkerboard.create_bl_obj(self.location, self.rotation)
        return {'FINISHED'}

class OP_AddMotorStage(Operator):
    bl_idname = "menu.add_motorstage"
    bl_label = "Motor Stage"

    bl_options = {'REGISTER', 'UNDO'}

    location: bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), unit='LENGTH') # type: ignore

    rotation: bpy.props.FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), unit='ROTATION') # type: ignore

    def execute(self, context):
        bpy.ops.mesh.primitive_plane_add(size=1, align='WORLD', scale=(1, 1, 1))
        bl_obj = bpy.context.active_object
        bl_obj.name = "Motor Stage"

        # Transform created object if any supplied
        bl_obj.rotation_euler[0] = self.rotation[0]
        bl_obj.rotation_euler[1] = self.rotation[1]
        bl_obj.rotation_euler[2] = self.rotation[2]

        bl_obj.location[0] = self.location[0]
        bl_obj.location[1] = self.location[1]
        bl_obj.location[2] = self.location[2]

        bl_obj.data["IsMotorStage"] = True

        return {'FINISHED'}

classes = [
    OP_AddCheckerboard,
    OP_AddMotorStage,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)