import bpy
from bpy.types import Panel

class CHECKERBOARD_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = "Checkerboard"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    # @classmethod
    # def poll(cls, context):
    #     return context.object.data and context.object.data.name in bpy.data.lights

    def draw(self, context):
        selected = context.object

        if not (selected and ("IsCheckerboard" in context.object.data)):
            return

        settings = selected.cb_settings

        self.layout.label(text='Checkerboard Settings:')
        box = self.layout.box()
        box.prop(settings, "size")

classes = [
    CHECKERBOARD_PT_Settings
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)