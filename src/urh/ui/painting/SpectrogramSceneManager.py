import numpy as np

from urh.signalprocessing.Spectrogram import Spectrogram
from urh.ui.painting.SceneManager import SceneManager
from urh.ui.painting.SpectrogramScene import SpectrogramScene


class SpectrogramSceneManager(SceneManager):
    def __init__(self, samples, parent):
        super().__init__(parent)

        self.samples_need_update = True

        self.scene.clear()
        self.spectrogram = Spectrogram(samples)
        self.scene = SpectrogramScene()

    @property
    def num_samples(self):
        return len(self.spectrogram.samples)

    def set_parameters(self, samples: np.ndarray, window_size, force_redraw=False):
        redraw_needed = False
        if self.samples_need_update:
            self.spectrogram.samples = samples
            redraw_needed = True
            self.samples_need_update = False

        if window_size != self.spectrogram.window_size:
            self.spectrogram.window_size = window_size
            redraw_needed = True

        if redraw_needed or force_redraw:
            self.show_full_scene()

    def show_scene_section(self, x1: float, x2: float, subpath_ranges=None, colors=None):
        pass

    def show_full_scene(self):
        self.scene.set_spectrogram_image(self.spectrogram.create_spectrogram_image(step=1))

    def init_scene(self, apply_padding=True):
        pass

    def eliminate(self):
        self.spectrogram.samples = None
        self.spectrogram = None
        super().eliminate()
