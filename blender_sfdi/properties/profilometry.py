import bpy

import opensfdi.phase as phase
import opensfdi.profilometry as prof

class BasePropertyRelationGroup(bpy.types.PropertyGroup):
    clazz: object

    def make_clazz_inst(self, **kwargs):
        raise NotImplementedError
    
    def has_name(self, name) -> bool:
        return self.clazz.__name__ == name


# # # # # # # # # # # # # # # # # # # # # 
# Phase Shifting

class PG_PhaseShiftNStep(BasePropertyRelationGroup):
    clazz = phase.NStepPhaseShift
    
    phase_count : bpy.props.IntProperty(name="Phase Count", default=3, min=3, max=32) # type: ignore

    def make_clazz_inst(self, **kwargs):
        return self.clazz(steps=self.phase_count)
    
REGISTERED_PHASE_SHIFTS = [
    PG_PhaseShiftNStep,
]


# # # # # # # # # # # # # # # # # # # # #
# Phase Unwrapping

class PG_PhaseUnwrapReliability(BasePropertyRelationGroup):
    clazz = phase.ReliabilityPhaseUnwrap

    wrap_around : bpy.props.BoolProperty(name="Wrap-around", default=False) # type: ignore

    def make_clazz_inst(self, **kwargs):
        return self.clazz(wrap_around=self.wrap_around)

REGISTERED_PHASE_UNWRAPS = [
    PG_PhaseUnwrapReliability,
]


# # # # # # # # # # # # # # # # # # # # #
# Profilometry

class PG_ClassicPhaseHeight(BasePropertyRelationGroup):
    clazz = prof.ClassicProf

    sf : bpy.props.FloatProperty(name="Spatial Frequency", default=0.0, min=0.0) # type: ignore

    cam_proj_dist : bpy.props.FloatProperty(name="Camera-Projector Distance", default=1.0, min=0.0) # type: ignore

    cam_ref_dist : bpy.props.FloatProperty(name="Camera-Reference Distance", default=1.0, min=0.0) # type: ignore

    def make_clazz_inst(self, **kwargs):
        return self.clazz(data=np.array([self.sf, self.cam_proj_dist, self.cam_ref_dist]), **kwargs)

class PG_LinearInvPhaseHeight(BasePropertyRelationGroup):
    clazz = prof.LinearInverseProf

    def make_clazz_inst(self, **kwargs):
        return self.clazz(**kwargs)

class PG_PolyPhaseHeight(BasePropertyRelationGroup):
    clazz = prof.PolynomialProf
    
    degree : bpy.props.IntProperty(name="Degree", description="Polynomial Degree", min=1, max=8, default=5) # type: ignore

    def make_clazz_inst(self, **kwargs):
        return self.clazz(degree=self.degree, **kwargs)
    
REGISTERED_PROFS = [
    PG_ClassicPhaseHeight,
    PG_LinearInvPhaseHeight,
    PG_PolyPhaseHeight,
]




classes = [
    # Profilometry
    PG_ClassicPhaseHeight,
    PG_PolyPhaseHeight,
    PG_LinearInvPhaseHeight,

    # Phase Unwrapping
    PG_PhaseUnwrapReliability,

    # Phase Shifting
    PG_PhaseShiftNStep,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    prof.register()

    # Profilometry
    global REGISTERED_PROFS
    for prop in REGISTERED_PROFS:
        setattr(bpy.types.Object, prop.clazz.__name__, bpy.props.PointerProperty(type=prop))

    # Phase Unwrapping
    global REGISTERED_PHASE_UNWRAPS
    for prop in REGISTERED_PHASE_UNWRAPS:
        setattr(bpy.types.Object, prop.clazz.__name__, bpy.props.PointerProperty(type=prop))

    # Phase Shifting
    global REGISTERED_PHASE_SHIFTS
    for prop in REGISTERED_PHASE_SHIFTS:
        setattr(bpy.types.Object, prop.clazz.__name__, bpy.props.PointerProperty(type=prop))

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    prof.unregister()

    # Profilometry
    global REGISTERED_PROFS
    for prop in reversed(REGISTERED_PROFS):
        delattr(bpy.types.Object, prop.clazz.__name__)

    # Phase Unwrapping
    global REGISTERED_PHASE_UNWRAPS
    for prop in reversed(REGISTERED_PHASE_UNWRAPS):
        delattr(bpy.types.Object, prop.clazz.__name__)

    # Phase Shifting
    global REGISTERED_PHASE_SHIFTS
    for prop in reversed(REGISTERED_PHASE_SHIFTS):
        delattr(bpy.types.Object, prop.clazz.__name__)