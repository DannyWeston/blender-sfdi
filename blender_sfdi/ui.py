import bpy
from bpy.types import Panel, Menu

from . import operators, devices

# Stereo Fringe Projection

class UI_FPStereo(Panel):
    bl_label = "Stereo Fringe Projection"
    bl_idname = "SCENE_PT_FPStereo"

    bl_category = "SFDI"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    bl_options = {'DEFAULT_CLOSED'}

    def _draw_fringes_manager(self, settings, layout):
        fringes_manager = settings.fringes_manager

        header, panel = layout.panel("FPStereoFringesManager", default_closed=True)
        header.label(text="Fringes Settings")
        if panel:
            if devices.BL_Projector.is_projector(settings.projector):
                projector = devices.BL_Projector.from_bl_obj(settings.projector)
                row = panel.row()
                row.enabled = 1 < projector.channels
                row.prop(fringes_manager, "multiplexing")

            # Stripe Counts
            box = panel.box()
            row = box.row()
            row.label(text="Stripe Counts")
            row.operator(operators.fringe_projection.OP_RemoveStripeCount.bl_idname, text="-")
            row.operator(operators.fringe_projection.OP_AddStripeCount.bl_idname, text="+")
            
            cc = 0
            for i, item in enumerate(fringes_manager.stripe_counts.values()):
                if i == 0: row = box.row()
                col = row.column()
                col.prop(item, "value", text="")
                cc += 1
                
                if cc == 3 and i < len(fringes_manager.stripe_counts.values()) - 1:
                    row = box.row()
                    cc = 0

            # Phase Counts
            box = panel.box()
            row = box.row()
            row.label(text="Phases")
            row.operator(operators.fringe_projection.OP_RemovePhase.bl_idname, text="-")
            row.operator(operators.fringe_projection.OP_AddPhase.bl_idname, text="+")
            cc = 0
            for i, item in enumerate(fringes_manager.phases.values()):
                if i == 0: row = box.row()
                col = row.column()
                col.prop(item, "value", text="")
                cc += 1
                
                if cc == 3 and i < len(fringes_manager.phases.values()) - 1:
                    row = box.row()
                    cc = 0


            # Rotations
            box = panel.box()
            row = box.row()
            row.label(text="Rotations")
            row.operator(operators.fringe_projection.OP_RemoveRotation.bl_idname, text="-")
            row.operator(operators.fringe_projection.OP_AddRotation.bl_idname, text="+")
            cc = 0
            for i, item in enumerate(fringes_manager.rotations.values()):
                if i == 0: row = box.row()
                col = row.column()
                col.prop(item, "value", text="")
                cc += 1
                
                if cc == 3 and i < len(fringes_manager.rotations.values()) - 1:
                    row = box.row()
                    cc = 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.fp_stereo

        # Camera & characterisation board
        layout.prop(settings, "camera", text="Camera")
        layout.prop(settings, "char_board", text="Characterisation Board")
        layout.prop(settings, "projector", text="Projector")

        # Animate / save metadata operators
        row = layout.row()
        row.operator(operators.fringe_projection.OP_CreateAnimation.bl_idname, text="Animate")
        row.operator(operators.fringe_projection.OP_SaveMetadata.bl_idname, text="Save Metadata")

        # Fringe manager
        self._draw_fringes_manager(settings, layout)


# Add SFDI Objects Menu

class MENU_MT_Camera(Menu):
    bl_idname = "MENU_MT_Camera"
    bl_label = "Camera"

    def draw(self, context):
        for t in devices.TEMPLATE_CAMERAS:
            name = t[0]

            op = self.layout.operator(operators.devices.OP_AddCamera.bl_idname, text=name)
            op.name = name

            # TODO: Add ability to set camera properties

class MENU_MT_Projector(Menu):
    bl_idname = "MENU_MT_Projector"
    bl_label = "Projector"

    def draw(self, context):
        self.layout.operator(operators.devices.OP_AddFringeProjector.bl_idname, text="Fringe Projector")

class MENU_MT_CharBoard(Menu):
    bl_idname = "MENU_MT_CharBoard"
    bl_label = "Board"

    def draw(self, context):
        self.layout.operator(operators.devices.OP_AddCheckerBoard.bl_idname, text="Checker Board")
        self.layout.operator(operators.devices.OP_AddCircleBoard.bl_idname, text="Circle Board")
        self.layout.operator(operators.devices.OP_AddImageBoard.bl_idname, text="Image Board")

class VIEW3D_MT_SFDIMenu(Menu):
    bl_idname = "VIEW3D_MT_SFDIMenu"
    bl_label = "SFDI"

    def draw(self, context):
        self.layout.menu(MENU_MT_Camera.bl_idname)
        self.layout.menu(MENU_MT_Projector.bl_idname)
        self.layout.menu(MENU_MT_CharBoard.bl_idname)


# Projector

class PROJECTOR_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = 'Projector'

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return devices.BL_Projector.is_projector(context.object)

    def draw(self, context):
        projector = devices.BL_Projector.from_bl_obj(context.object)

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Suggest to use Cycles
        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = layout.box()
            box.label(text='Fringe projectors can only be used with Blender Cycles', icon='ERROR')
            return

        # Main settings        
        header, panel = layout.panel("Projector Settings", default_closed=False)
        header.label(text='Main Settings')
        if panel:
            # TODO: Resolution
            # row = box.row(align=True)
            # row.prop(projector.settings, "resolution", index=0, text="Resolution")
            # row.prop(projector.settings, "resolution", index=1, text="")

            panel.prop(projector.settings, 'aspect_ratio')
            panel.prop(projector.settings, 'throw_ratio')
            panel.prop(projector.settings, 'light_falloff')

        # Channel-specific settings
        header, panel = layout.panel("Channels", default_closed=True)
        header.label(text=f"Channel Properties")
        if panel:
            panel.prop(projector.settings, 'channels')

            for i in range(projector.channels):
                ch_prop = projector.settings.channels_list[i]

                # Create channel-specific sub-panel for holding values
                temp_header, temp_panel = panel.panel(f"Channel{i+1}", default_closed=False)
                temp_header.label(text=f"Channel {i+1}")

                if temp_panel:
                    panel.prop(ch_prop, "intensity")
                    panel.prop(ch_prop, "fringes_type")
                    panel.prop(ch_prop, "stripe_count")
                    panel.prop(ch_prop, "phase")
                    panel.prop(ch_prop, "rotation")
                    panel.prop(ch_prop, "noise")


            # TODO: Add way to add/remove channels
            # panel.operator(operators.devices.OP..., text="Add Delta Transform")


# Camera

class CAMERA_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = 'Camera'

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return devices.BL_Camera.is_camera(context.object)

    def draw(self, context):
        camera = devices.BL_Camera.from_bl_obj(context.object)

        # TODO: Check object type for camera, ignore for now

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # Suggest to use Cycles
        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = layout.box()
            box.label(text='SFDI cameras can only be used with the Cycles renderer', icon='ERROR')
            return
        
        # Main settings        
        header, panel = layout.panel("Camera Settings", default_closed=False)
        header.label(text='Main Settings')
        if panel:
            box = panel.box()

            # Pixel Resolution
            row = box.row(align=True)
            row.prop(camera.settings, "resolution", index=0, text="Resolution")
            row.prop(camera.settings, "resolution", index=1, text="")

            box.prop(camera.settings, 'refresh_rate')
            box.prop(camera.settings, 'channels')
        
            box.operator(operators.devices.OP_CameraSetScene.bl_idname, text="Update Scene")

        # Blender settings        
        header, panel = layout.panel("Camera Blender Settings", default_closed=False)
        header.label(text='Blender Settings')
        if panel:
            box = layout.box()
            box.prop(camera.settings, 'render_samples')
            box.prop(camera.settings, 'bit_depth')
            box.prop(camera.settings, 'file_format')


# Characterisation Board

class CHARACTERISATION_PT_Settings(Panel):
    bl_category = "SFDI"
    bl_label = "Characterisation Board"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return devices.BL_CharBoard.is_char_board(context.object)

    def draw(self, context):
        board = devices.BL_CharBoard.from_bl_obj(context.object)

        layout = self.layout
        settings = board.settings

        # Save / Load Operators
        row = layout.row()
        row.label(text="Poses:")
        row.operator(operators.devices.OP_LoadBoardPoses.bl_idname, text="Load")
        row.operator(operators.devices.OP_SaveBoardPoses.bl_idname, text="Save")

        # Board Poses
        header, panel = layout.panel("CharacterisationPoses", default_closed=True)
        header.label(text=f"Characterisation Poses ({len(settings.poses)})")
        if panel:
            # Print all transforms
            for i, ff in enumerate(settings.poses):
                row = panel.row()
                row.prop(ff, "translation", text="")
                row.prop(ff, "rotation", text="")

                # TODO: Add support for viewing a transform
                # op = row.operator(operators.board.OP_ViewCBTransform.bl_idname, text="V")
                # op.transform_id = i

                op = row.operator(operators.devices.OP_RemoveCharBoardPose.bl_idname, text="-")
                op.pose_id = i

            # Add a new pose (use delta)
            panel.operator(operators.devices.OP_AddCharBoardPose.bl_idname, text="Add Pose")


# Blender register

classes = [
    MENU_MT_Camera,
    CAMERA_PT_Settings,

    MENU_MT_Projector,
    PROJECTOR_PT_Settings,

    MENU_MT_CharBoard,
    CHARACTERISATION_PT_Settings,

    VIEW3D_MT_SFDIMenu,

    UI_FPStereo,
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