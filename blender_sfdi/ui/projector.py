import bpy
from bpy.types import Panel, UIList

""" class PT_ProjMenu(Panel):
    bl_idname = "pt.proj_menu"
    bl_label = "Fringe Properties"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object.data and ("IsProjector" in context.object.data) and context.object.data.name in bpy.data.lights

    def draw(self, context):
        temp = context.object.data
        
        box = self.layout.box()
        
        box.row(align=True)
        box.prop(temp["Fringe Type"], "fringe_type")
        box.prop(proj_settings, "frequency")
        box.prop(proj_settings, "phase")
        box.prop(proj_settings, "rotation")

        grid = box.grid_flow(columns=2, align=True)
        grid.prop(proj_settings, "width")
        grid.prop(proj_settings, "height") """

class UL_RegisteredProjectors(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        
        if item is None: return
        
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item and item.obj:
                row.prop(item.obj, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

classes = [
    #PT_ProjMenu,
    UL_RegisteredProjectors
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)