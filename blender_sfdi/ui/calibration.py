import bpy
from bpy.types import Panel, UIList

class PT_CheckerboardMenu(Panel):
    bl_idname = "pt.checkerboard_menu"
    bl_label = "Checkerboard Properties"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object.data and context.object.data.name in bpy.data.lights

    def draw(self, context):
        settings = context.object.CheckerboardSettings
        
        box = self.layout.box()

        grid = box.grid_flow(columns=2, align=True)
        grid.prop(proj_settings, "width")
        grid.prop(proj_settings, "height")
        

classes = [
    PT_ProjMenu,
    UL_RegisteredProjectors
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)