import bpy

from sfdi_addon.operators import OP_RegisterProj, OP_UnregisterProj

class UL_RegisteredProjectors(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                if active_propname == "id":
                    row.prop(item.obj, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
            layout.label(text=data.name, translate=False, icon_value=icon)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

     
class UL_RegisteredCameras(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        slot = item
        
        row = layout.row()
        
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if slot:
                if active_propname == "id":
                    row.prop(slot.obj, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
            layout.label(text=data.name, translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

      
class PT_SFDIMenu(bpy.types.Panel):
    bl_category = "SFDI"
    bl_label = "SFDI Menu"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        fps = context.scene.FringeProjectors

        row = self.layout.row(align=True)
        
        self.layout.label(text="Experiment Projectors")
        
        self.layout.template_list("UL_RegisteredProjectors", "", fps, "items", fps, "id")
        
        self.layout.operator(OP_RegisterProj.bl_idname, text="Add")
        self.layout.operator(OP_UnregisterProj.bl_idname, text="Remove")


class PT_ProjMenu(bpy.types.Panel):
    bl_idname = "pt.proj_menu"
    bl_label = "Fringe Properties"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return context.object.name in bpy.data.lights

    def draw(self, context):
        fringes_props = context.scene.FringesProps
        
        self.layout.row(align=True)
        self.layout.prop(fringes_props, "fringes_type")
        self.layout.prop(fringes_props, "phases")
        self.layout.prop(fringes_props, "rotation")


classes = [
    UL_RegisteredProjectors,
    UL_RegisteredCameras,
    
    PT_SFDIMenu,
    PT_ProjMenu
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)