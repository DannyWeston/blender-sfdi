from abc import ABC, abstractmethod
import bpy
from bpy.types import Panel, UIList, Menu

from .blender import BL_FringeProjector, BL_Camera, BL_Checkerboard, BL_MotorStage
from . import operators

# # # # # # # # # # # # # # # # # # # # # 
# Abstract classes

class IPanelPropSection(ABC):
    @abstractmethod
    def draw(self, settings: bpy.types.PropertyGroup, layout):
        pass


# # # # # # # # # # # # # # # # # # # # #
# Experiment

class UI_UL_RegisteredObjects(UIList):
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

class UI_ExperimentPanel(Panel):
    bl_label = "Experiment"
    bl_idname = "SCENE_PT_Experiment"

    bl_category = "SFDI"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.ex_settings

        box = layout.box()
        box.template_list("UI_UL_RegisteredObjects", "UI_ExperimentPanel_Objects", settings, "bl_objs", settings, "bl_obj_index")

        row = box.row()
        row.operator(operators.experiment.OP_RegisterObject.bl_idname, text="Add Object")
        row.operator(operators.experiment.OP_UnregisterObject.bl_idname, text="Remove Object")

        row.prop(settings, "only_images", text="Only Generate Images")

        # Selected camera / projector
        row = box.row()
        row.prop(settings, "camera", text="Camera")
        row.prop(settings, "projector", text="Projector")

        # Phase Shift
        box = layout.box()
        box.prop(settings.phase_shift, "methods", text="Phase Shift")
        active = getattr(scene, settings.phase_shift.methods)
        active.draw(box)

        # Phase Unwrap
        box = layout.box()
        box.prop(settings.phase_unwrap, "methods", text="Phase Unwrap")
        active = getattr(scene, settings.phase_unwrap.methods)
        active.draw(box)

        # Profilometry
        box = layout.box()
        box.prop(settings.profilometry, "methods", text="Profilometry")
        active = getattr(scene, settings.profilometry.methods)
        active.draw(box)

        # Calibration Operator
        box = layout.box()

        row = box.row() # Motor Stage
        row.prop(settings, "motor_stage", text="Motor Stage")

        row = box.row() # Output Name / Run Button
        sub = row.row()
        sub.scale_x = 2.0
        sub.prop(settings, "output_name", text="Name")
        row.operator(operators.experiment.OP_CalibrateProf.bl_idname, text="Calibrate")

        # Experiment Operator
        box = layout.box()
        row = box.row()
        sub = row.row()
        sub.scale_x = 2.0
        sub.prop(settings, "calibration_files", text="Calibration")
        row.operator(operators.experiment.OP_Experiment.bl_idname, text="Run")

# # # # # # # # # # # # # # # # # # # # # 
# Add Object Menu

class VIEW3D_MT_SFDIMenu(Menu):
    bl_idname = "VIEW3D_MT_SFDIMenu"
    bl_label = "SFDI"

    ops = [
        operators.calibration.OP_AddCheckerboard,
        operators.calibration.OP_AddMotorStage,

        operators.projector.OP_AddProj,

        operators.camera.OP_AddCamera,
        operators.camera.OP_AddPiCameraV1
    ]

    def draw(self, context):
        for op in VIEW3D_MT_SFDIMenu.ops:
            self.layout.operator(op.bl_idname)


# # # # # # # # # # # # # # # # # # # # # 
# Projector

class PROJECTOR_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = 'Projector'

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return BL_FringeProjector.is_fringe_proj(context.object)

    def draw(self, context):
        fringe_proj = BL_FringeProjector(context.object)

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Suggest to use Cycles
        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = layout.box()
            box.label(text='Fringe projectors can only be used with Blender Cycles', icon='ERROR')
            return
        
        layout.label(text='Projector Settings:')
        box = layout.box()
        box.prop(fringe_proj.settings, 'resolution')
        box.prop(fringe_proj.settings, 'aspect_ratio')
        box.prop(fringe_proj.settings, 'throw_ratio')

        layout.label(text='Fringe Settings:')
        box = layout.box()
        box.prop(fringe_proj.settings, 'fringe_frequency')
        box.prop(fringe_proj.settings, 'fringe_phase')
        box.prop(fringe_proj.settings, 'fringe_rotation')
        box.prop(fringe_proj.settings, 'fringe_type')


# # # # # # # # # # # # # # # # # # # # # 
# Camera

class CAMERA_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = 'Camera'

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return BL_Camera.is_camera(context.object)

    def draw(self, context):
        camera = BL_Camera(context.object)

        # TODO: Check object type for camera, ignore for now

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Suggest to use Cycles
        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = layout.box()
            box.label(text='SFDI Cameras can only be used with Blender Cycles', icon='ERROR')
            return

        layout.label(text='Camera Settings:')
        box = layout.box()

        box.prop(camera.settings, 'resolution')
        # box.prop(camera_settings, 'aspect_ratio')


class CHECKERBOARD_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = "Checkerboard"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return BL_Checkerboard.is_checkerboard(context.object)

    def draw(self, context):
        cb = BL_Checkerboard(context.object)

        self.layout.label(text='Tile Grid Settings:')
        box = self.layout.box()
        box.prop(cb.settings, "size")

        self.layout.label(text='Position Settings:')
        box = self.layout.box()
        box.prop(cb.settings, "seed")
        box.prop(cb.settings, "max_position")
        box.prop(cb.settings, "max_rotation")
        box.prop(cb.settings, "show_debug")



# # # # # # # # # # # # # # # # # # # # # 
# Motor Stage

class MOTORSTAGE_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = 'Motor Stage'

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return BL_MotorStage.is_motorstage(context.object)

    def draw(self, context):
        motor_stage = BL_MotorStage(context.object)

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        box = layout.box()
        row = box.row() # Min / max height
        row.prop(motor_stage.settings, 'min_height')
        row.prop(motor_stage.settings, 'max_height')

        box.prop(motor_stage.settings, 'steps')

# # # # # # # # # # # # # # # # # # # # #
# Entry Point

classes = [
    VIEW3D_MT_SFDIMenu,

    # Experiments
    UI_ExperimentPanel,
    UI_UL_RegisteredObjects,

    # Custom Object Types
    PROJECTOR_PT_Settings,
    CAMERA_PT_Settings,
    CHECKERBOARD_PT_Settings,
    MOTORSTAGE_PT_Settings,
]

def check_stale_objs(scene):
    bl_obj_ptrs = scene.ex_settings.bl_objs

    if bl_obj_ptrs:
        for ptr in bl_obj_ptrs:
            if scene.objects.get(ptr.name) is None:
                # Remove from list
                temp_id = bl_obj_ptrs.find(ptr.name)
                bl_obj_ptrs.remove(temp_id)

def sfdi_menu(self, context):
    self.layout.menu(VIEW3D_MT_SFDIMenu.bl_idname)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_add.append(sfdi_menu)

    bpy.app.handlers.depsgraph_update_post.append(check_stale_objs)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_add.remove(sfdi_menu)

    bpy.app.handlers.depsgraph_update_post.remove(check_stale_objs)