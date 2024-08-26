import bpy
from bpy.types import Panel, UIList

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

class PROJECTOR_PT_Settings(Panel):
    bl_category = "Projector"
    bl_label = 'Projector'

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        selected = context.object

        if not (selected and ("IsProjector" in context.object.data)):
            return

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Suggest to use Cycles
        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = layout.box()
            box.label(text='Fringe projectors can only be used with Blender Cycles', icon='ERROR')
            return

        proj_settings = selected.proj_settings
        
        layout.label(text='Projector Settings:')
        box = layout.box()
        box.prop(proj_settings, 'resolution')
        box.prop(proj_settings, 'aspect_ratio')
        box.prop(proj_settings, 'throw_ratio')

        layout.label(text='Fringe Settings:')
        box = layout.box()
        box.prop(proj_settings, 'fringe_frequency')
        box.prop(proj_settings, 'fringe_phase')
        box.prop(proj_settings, 'fringe_rotation')
        box.prop(proj_settings, 'fringe_type')

classes = [
    #PT_ProjMenu,
    UL_RegisteredProjectors,
    PROJECTOR_PT_Settings
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)