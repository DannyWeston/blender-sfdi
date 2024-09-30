import bpy
from bpy.types import Panel, UIList, Menu

from . import operators

# # # # # # # # # # # # # # # # # # # # # 
# Add Object Menu

class VIEW3D_MT_SFDIMenu(Menu):
    bl_idname = "VIEW3D_MT_SFDIMenu"
    bl_label = "SFDI"

    ops = [
        operators.calibration.OP_AddCheckerboard,
        operators.camera.OP_AddCamera,
        operators.projector.OP_AddProj,
    ]

    def draw(self, context):
        for op in VIEW3D_MT_SFDIMenu.ops:
            self.layout.operator(op.bl_idname)


# # # # # # # # # # # # # # # # # # # # # 
# Projector


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
    bl_category = "SFDI"
    bl_label = 'Projector'

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        selected = context.object

        return selected and ("IsProjector" in context.object.data)

    def draw(self, context):
        selected = context.object

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


# # # # # # # # # # # # # # # # # # # # # 
# Camera

class UL_RegisteredCameras(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item and item.obj:
                row.prop(item.obj, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class CAMERA_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = 'Camera'

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        selected = context.object

        return selected and (selected.type == "CAMERA")

    def draw(self, context):
        selected = context.object

        # TODO: Check object type for camera, ignore for now

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Suggest to use Cycles
        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = layout.box()
            box.label(text='SFDI Cameras can only be used with Blender Cycles', icon='ERROR')
            return

        camera_settings = selected.camera_settings
        
        layout.label(text='Camera Settings:')
        box = layout.box()

        box.prop(camera_settings, 'resolution')
        # box.prop(camera_settings, 'aspect_ratio')

# # # # # # # # # # # # # # # # # # # # # 
# Calibration

class CHECKERBOARD_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = "Checkerboard"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        selected = context.object

        return selected and ("IsCheckerboard" in context.object.data)

    def draw(self, context):
        selected = context.object
        settings = selected.cb_settings

        self.layout.label(text='Tile Grid Settings:')
        box = self.layout.box()
        box.prop(settings, "size")

        self.layout.label(text='Position Settings:')
        box = self.layout.box()
        box.prop(settings, "seed")
        box.prop(settings, "max_position")
        box.prop(settings, "max_rotation")


classes = [
    VIEW3D_MT_SFDIMenu,

    UL_RegisteredProjectors,
    UL_RegisteredCameras,

    PROJECTOR_PT_Settings,
    CAMERA_PT_Settings,
    CHECKERBOARD_PT_Settings,
]

def sfdi_menu(self, context):
    self.layout.menu(VIEW3D_MT_SFDIMenu.bl_idname)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_add.append(sfdi_menu)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_add.remove(sfdi_menu)