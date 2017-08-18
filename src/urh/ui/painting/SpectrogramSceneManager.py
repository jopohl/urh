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

        self.lod = self.min_lod

    @property
    def num_samples(self):
        return len(self.spectrogram.samples)

    @property
    def min_lod(self):
        return 1

    @property
    def max_lod(self):
        return max(1, int(self.num_samples / (self.spectrogram.MAX_LINES_PER_VIEW * self.spectrogram.hop_size)))

    def __get_step_from_lod(self, lod):
        return max(self.min_lod, self.max_lod - lod + self.min_lod)

    def __get_sample_step(self, sample_start, sample_end):
        return max(1, int((sample_end - sample_start) / (self.spectrogram.MAX_LINES_PER_VIEW * self.spectrogram.hop_size)))

    def set_parameters(self, samples: np.ndarray, window_size, lod):
        redraw_needed = False
        if self.samples_need_update:
            self.spectrogram.samples = samples
            redraw_needed = True
            self.samples_need_update = False

        if window_size != self.spectrogram.window_size:
            self.spectrogram.window_size = window_size
            redraw_needed = True

        if lod != self.lod:
            self.lod = lod
            redraw_needed = True

        if redraw_needed:
            self.show_full_scene()

    def show_scene_section(self, x1: float, x2: float, subpath_ranges=None, colors=None):
        pass

    def show_full_scene(self):
        step = self.__get_step_from_lod(self.lod)
        self.scene.set_spectrogram_image(self.spectrogram.create_spectrogram_image(step=step))

    def init_scene(self, apply_padding=True):
        pass

    def eliminate(self):
        self.spectrogram.samples = None
        self.spectrogram = None
        super().eliminate()
