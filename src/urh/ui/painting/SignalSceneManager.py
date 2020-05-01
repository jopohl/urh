import math

from urh.signalprocessing.Signal import Signal
from urh.ui.painting.SceneManager import SceneManager


class SignalSceneManager(SceneManager):
    def __init__(self, signal: Signal, parent):
        super().__init__(parent)
        self.signal = signal
        self.scene_type = 0  # 0 = Analog Signal, 1 = QuadDemodView
        self.mod_type = "ASK"

    def show_scene_section(self, x1: float, x2: float, subpath_ranges=None, colors=None):
        self.plot_data = self.signal.real_plot_data if self.scene_type == 0 else self.signal.qad
        super().show_scene_section(x1, x2, subpath_ranges=subpath_ranges, colors=colors)

    def init_scene(self):
        if self.scene_type == 0:
            # Ensure real plot has same y Axis
            self.plot_data = self.signal.real_plot_data
        else:
            self.plot_data = self.signal.qad

        super().init_scene()
        if self.scene_type == 1 and (self.mod_type == "FSK" or self.mod_type == "PSK"):
            self.scene.setSceneRect(0, -4, self.num_samples, 8)

        self.line_item.setLine(0, 0, 0, 0)  # Hide Axis

        if self.scene_type == 0:
            self.scene.draw_noise_area(self.signal.noise_min_plot, self.signal.noise_max_plot - self.signal.noise_min_plot)
        else:
            self.scene.draw_sep_area(-self.signal.center_thresholds)

    def eliminate(self):
        super().eliminate()
        # do not eliminate the signal here, as it would cause data loss in tree models!
        # if hasattr(self.signal, "eliminate"):
        #    self.signal.eliminate()
        self.signal = None
