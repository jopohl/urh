from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QPainterPath, QFont, QPen
import numpy as np

from urh import constants
from urh.SceneManager import SceneManager
from urh.signalprocessing.Signal import Signal
from urh.ui.ZoomableScene import ZoomableScene
from urh.cythonext import path_creator, util, signalFunctions


class SignalSceneManager(SceneManager):
    def __init__(self, signal: Signal, parent):
        super().__init__(parent)
        self.signal = signal
        self.noise_line_item = self.scene.addLine(0, 0, 0, 0, QPen(constants.NOISE_COLOR, Qt.FlatCap))
        self.path_item = self.scene.addPath(QPainterPath(), QPen(constants.LINECOLOR,  Qt.FlatCap))
        """:type: QGraphicsPathItem """
        self.text_item = self.scene.addText("Loading...", QFont("Helvetica", 72))
        self.scene_type = 0 # 0 = Analog Signal, 1 = QuadDemodView

    def show_scene_section(self, x1: float, x2: float):
        self.plot_data = self.signal.real_plot_data if self.scene_type == 0 else self.signal.qad
        super().show_scene_section(x1, x2)

    def init_scene(self):
        #self.text_item.setPlainText("")
        #num_samples = self.signal.num_samples


        stored_minimum, stored_maximum = self.minimum, self.maximum

        if self.scene_type == 0:
            # Ensure Real plot have same y Axis
            #minimum, maximum = util.minmax(self.signal.real_plot_data)
            self.plot_data = self.signal.real_plot_data
            self.noise_line_item.setLine(0, 0, 0, 0)
        else:
            noise_val = signalFunctions.get_noise_for_mod_type(self.scene_type - 1)
            # Bypass Min/Max calculation
            if noise_val == 0:
                # ASK
                self.minimum, self.maximum = 0, self.padding * np.max(self.signal.qad)
            else:
                self.minimum, self.maximum = 0, self.padding * noise_val
            self.plot_data = self.signal.qad
            self.noise_line_item.setLine(0, -noise_val, self.num_samples, -noise_val)

        super().init_scene()
        self.minimum, self.maximum = stored_minimum, stored_maximum

        self.line_item.setLine(0, 0, 0, 0) # Hide Axis

        if self.scene_type == 0:
            self.scene.draw_noise_area(self.signal.noise_min_plot, self.signal.noise_max_plot - self.signal.noise_min_plot)
        else:
            self.scene.draw_sep_area(-self.signal.qad_center)