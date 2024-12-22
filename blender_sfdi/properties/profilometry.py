import bpy

import numpy as np

import opensfdi.phase as phase
import opensfdi.profilometry as prof

from abc import abstractmethod

# # # # # # # # # # # # # # # # # # # # # 
# Abstract classes

class PG_UIProperty(bpy.types.PropertyGroup):
    @abstractmethod
    def make_instance(self, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    def draw(self, layout):
        pass

# # # # # # # # # # # # # # # # # # # # # 
# Phase Shifting

class PG_PhaseShift(bpy.types.PropertyGroup):
    methods: bpy.props.EnumProperty(
        items=lambda self, context: self.get_items(context),
        name="Select Item",
        description="Choose an item from the collection",
        update=None
    )  # type: ignore

    METHODS: list[PG_UIProperty] = []

    def get_instance(self):
        for x in self.METHODS:
            if x == self.methods:
                return x.make_instance()
            
        return None

    def get_items(self, context):
        return [(v.__name__, v.__name__, "") for v in self.METHODS]

def register_shift(cls: PG_UIProperty):
    PG_PhaseShift.METHODS.append(cls)
    return cls

@register_shift
class PG_PhaseShiftNStep(PG_UIProperty):
    phase_count : bpy.props.IntProperty(name="Phase Count", default=3, min=3, max=32) # type: ignore

    def make_instance(self, **kwargs):
        return phase.NStepPhaseShift(phase_count=self.phase_count)
    
    def draw(self, layout):
        row = layout.row()
        row.prop(self, "phase_count")


# # # # # # # # # # # # # # # # # # # # #
# Phase Unwrapping

class PG_PhaseUnwrap(bpy.types.PropertyGroup):
    methods: bpy.props.EnumProperty(
        items=lambda self, context: self.get_items(context),
        name="Select Item",
        description="Choose an item from the collection",
        update=None
    )  # type: ignore

    METHODS: list[PG_UIProperty] = []

    def get_instance(self):
        for x in self.METHODS:
            if x == self.methods:
                return x.make_instance()
            
        return None
    
    def get_items(self, context):
        return [(v.__name__, v.__name__, "") for v in self.METHODS]
    
def register_unwrap(cls: PG_UIProperty):
    PG_PhaseUnwrap.METHODS.append(cls)
    return cls

@register_unwrap
class PG_PhaseUnwrapReliability(PG_UIProperty):
    wrap_around : bpy.props.BoolProperty(name="Wrap-around", default=False) # type: ignore

    def make_instance(self, **kwargs):
        return phase.ReliabilityPhaseUnwrap(wrap_around=self.wrap_around)
    
    def draw(self, layout):
        row = layout.row()
        row.prop(self, "wrap_around")


# # # # # # # # # # # # # # # # # # # # #
# Profilometry

class PG_Profilometry(bpy.types.PropertyGroup):
    methods: bpy.props.EnumProperty(
        items=lambda self, context: self.get_items(context),
        name="Select Item",
        description="Choose an item from the collection",
        update=None
    )  # type: ignore

    METHODS: list[PG_UIProperty] = []

    def get_instance(self):
        for x in self.METHODS:
            if x == self.methods:
                return x.make_instance()
            
        return None

    def get_items(self, context):
        return [(v.__name__, v.__name__, "") for v in self.METHODS]

def register_prof(cls: PG_UIProperty):
    PG_Profilometry.METHODS.append(cls)
    return cls

@register_prof
class PG_ClassicPhaseHeight(PG_UIProperty):
    sf : bpy.props.FloatProperty(name="Spatial Frequency", default=0.0, min=0.0) # type: ignore

    cam_proj_dist : bpy.props.FloatProperty(name="Camera-Projector Distance", default=1.0, min=0.0) # type: ignore

    cam_ref_dist : bpy.props.FloatProperty(name="Camera-Reference Distance", default=1.0, min=0.0) # type: ignore

    def make_instance(self, **kwargs):
        return prof.ClassicProf(data=np.array([self.sf, self.cam_proj_dist, self.cam_ref_dist]), **kwargs)
    
    def draw(self, layout):
        row = layout.row()
        row.prop(self, "sf")
        row.prop(self, "cam_ref_dist")
        row.prop(self, "cam_proj_dist")

@register_prof
class PG_LinearInvPhaseHeight(PG_UIProperty):
    def make_instance(self, **kwargs):
        return prof.LinearInverseProf(**kwargs)
    
    def draw(self, layout):
        pass

@register_prof
class PG_PolyPhaseHeight(PG_UIProperty):
    degree : bpy.props.IntProperty(name="Degree", description="Polynomial Degree", min=1, max=8, default=5) # type: ignore

    def make_instance(self, **kwargs):
        return prof.PolynomialProf(degree=self.degree, **kwargs)
    
    def draw(self, layout):
        row = layout.row()
        row.prop(self, "degree")


classes = [
    PG_PhaseShift,
    PG_PhaseShiftNStep,

    PG_PhaseUnwrap,
    PG_PhaseUnwrapReliability,

    PG_Profilometry,
    PG_ClassicPhaseHeight,
    PG_LinearInvPhaseHeight,
    PG_PolyPhaseHeight,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.PG_PhaseShiftNStep = bpy.props.PointerProperty(type=PG_PhaseShiftNStep)

    bpy.types.Scene.PG_PhaseUnwrapReliability = bpy.props.PointerProperty(type=PG_PhaseUnwrapReliability)

    bpy.types.Scene.PG_ClassicPhaseHeight = bpy.props.PointerProperty(type=PG_ClassicPhaseHeight)
    bpy.types.Scene.PG_LinearInvPhaseHeight = bpy.props.PointerProperty(type=PG_LinearInvPhaseHeight)
    bpy.types.Scene.PG_PolyPhaseHeight = bpy.props.PointerProperty(type=PG_PolyPhaseHeight)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.PG_PhaseShiftNStep

    del bpy.types.Scene.PG_PhaseUnwrapReliability

    del bpy.types.Scene.PG_ClassicPhaseHeight
    del bpy.types.Scene.PG_LinearInvPhaseHeight
    del bpy.types.Scene.PG_PolyPhaseHeight