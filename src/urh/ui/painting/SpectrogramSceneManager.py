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

        # If dynamic, the scene is updated on each zoom/scroll
        # If not, then spectrogram is calculated completely once (may take some time) and then stored
        self.dynamic = False

    @property
    def num_samples(self):
        return len(self.spectrogram.samples)

    @property
    def total_length_x(self):
        return len(self.spectrogram.samples) / self.spectrogram.hop_size

    @property
    def zoom_factor(self):
        return self.total_length_x / self.spectrogram.time_bins

    def __get_sample_step(self, sample_start, sample_end):
        return max(1, int((sample_end - sample_start) / (self.spectrogram.MAX_LINES_PER_VIEW * self.spectrogram.hop_size)))

    def set_samples(self, samples: np.ndarray, window_size):
        redraw_needed = False
        if self.samples_need_update:
            self.spectrogram.samples = samples
            redraw_needed = True
            self.samples_need_update = False

        if window_size != self.spectrogram.window_size:
            self.spectrogram.window_size = window_size
            redraw_needed = True

        if redraw_needed:
            self.show_full_scene()


    def show_scene_section(self, x1: float, x2: float, subpath_ranges=None, colors=None):
        if not self.dynamic:
            return

        sample_start = max(0, int(self.zoom_factor * x1 * self.spectrogram.hop_size))
        sample_end = max(0, int(self.zoom_factor * x2 * self.spectrogram.hop_size))

        if sample_start > sample_start:
            sample_start, sample_end = sample_end, sample_start

        step = self.__get_sample_step(sample_start, sample_end)

        print(sample_start, sample_end, step)

        self.scene.set_spectrogram_image(self.spectrogram.create_spectrogram_image(sample_start, sample_end, step))

    def show_full_scene(self):
        if self.dynamic:
            step = self.__get_sample_step(0, self.num_samples)
        else:
            step = 1
        self.scene.set_spectrogram_image(self.spectrogram.create_spectrogram_image(step=step))

    def init_scene(self, apply_padding=True):
        pass

    def eliminate(self):
        self.spectrogram.samples = None
        self.spectrogram = None
        super().eliminate()
