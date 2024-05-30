
import bpy
from bpy.types import Panel

from sfdi_addon.operator.fringe_proj import OP_FPNStep
from sfdi_addon.operator.projector import OP_RegisterProj, OP_UnregisterProj
from sfdi_addon.operator.camera import OP_RegisterCamera, OP_UnregisterCamera
from sfdi_addon.operator.object import OP_RegisterObject, OP_UnregisterObject

class PT_SFDI_NStepFP(Panel):
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

class PT_SFDI_Selection(Panel):
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

classes = [
    PT_SFDI_NStepFP,
    PT_SFDI_Selection
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)