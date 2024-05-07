import bpy

from sfdi_addon.operators import OP_RegisterProj, OP_UnregisterProj, OP_RegisterCamera, OP_UnregisterCamera, OP_RegisterObject, OP_UnregisterObject, OP_FPNStep

class UL_RegisteredProjectors(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item and item.obj:
                row.prop(item.obj, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class UL_RegisteredCameras(bpy.types.UIList):
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

class UL_RegisteredObjects(bpy.types.UIList):
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

class PT_ProjMenu(bpy.types.Panel):
    bl_idname = "pt.proj_menu"
    bl_label = "Fringe Properties"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object.data and context.object.data.name in bpy.data.lights

    def draw(self, context):
        proj_settings = context.object.ProjectorSettings
        
        box = self.layout.box()
        
        box.row(align=True)
        box.prop(proj_settings, "fringe_type")
        box.prop(proj_settings, "frequency")
        box.prop(proj_settings, "phase")
        box.prop(proj_settings, "rotation")

        grid = box.grid_flow(columns=2, align=True)
        grid.prop(proj_settings, "width")
        grid.prop(proj_settings, "height")

class PT_SFDI_Selection(bpy.types.Panel):
    bl_category = "SFDI"
    bl_label = "Selected"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        # Projector Section
        box = self.layout.box()
        box.label(text="Projectors")
        box.template_list("UL_RegisteredProjectors", "", context.scene, "ExProjectors", context.scene, "ExProjectorsIndex")
        
        grid = box.grid_flow(columns=2, align=True)
        grid.operator(OP_RegisterProj.bl_idname, text="Add Projector")
        grid.operator(OP_UnregisterProj.bl_idname, text="Remove Projector")
        
        # Camera section
        box = self.layout.box()
        box.label(text="Cameras")
        box.template_list("UL_RegisteredCameras", "", context.scene, "ExCameras", context.scene, "ExCamerasIndex")
        
        grid = box.grid_flow(columns=2, align=True)
        grid.operator(OP_RegisterCamera.bl_idname, text="Add Camera")
        grid.operator(OP_UnregisterCamera.bl_idname, text="Remove Camera")
        
        # Objects section
        ex = context.scene.ExProperties
        box = self.layout.box()
        box.label(text="Objects")
        box.template_list("UL_RegisteredObjects", "", ex, "objects", ex, "object_index")

        grid = box.grid_flow(columns=2, align=True)
        grid.operator(OP_RegisterObject.bl_idname, text="Add Object")
        grid.operator(OP_UnregisterObject.bl_idname, text="Remove Object")

class PT_SFDI_NStepFP(bpy.types.Panel):
    bl_category = "SFDI"
    bl_label = "Fringe Projection: N-Step"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    bl_options = {"DEFAULT_CLOSED"}
    
    
    def draw(self, context):
        ex = context.scene.ExProperties
        
        box = self.layout.box()
        grid = box.grid_flow(columns=2, align=True)
        grid.prop(ex, "phase_count")
        grid.prop(ex, "runs")
        
        # Fringe Projection: N-step
        n_step = ex.fp_n_step
        if n_step:
            grid = box.grid_flow(columns=2, align=True)
            grid.prop(n_step, "sf")
        
            box.operator(OP_FPNStep.bl_idname, text="Run")

classes = [
    UL_RegisteredProjectors,
    UL_RegisteredCameras,
    UL_RegisteredObjects,
    
    PT_SFDI_Selection,
    PT_SFDI_NStepFP,
    PT_ProjMenu
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)