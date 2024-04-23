from sfdi_addon.video import BlenderCamera, BlenderProjector

from sfdi.experiment import Experiment

class BlenderExperiment:
    def __init__(self, cameras, projectors):
        self._cameras = [BlenderCamera(name=cam_name) for cam_name in cameras]
        self._projectors = [BlenderProjector(name=proj_name) for proj_name in projectors]
        
    def run_experiment(self):
        experiment = Experiment(self._cameras, self._projectors, 0.0)

        # n = number of images to render
        # Note will cycle through projector images according to n
        experiment.run(n=3)