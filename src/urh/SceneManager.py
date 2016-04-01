from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QPainterPath, QFont, QPen
import math
import numpy as np

from urh import constants
from urh.ui.ZoomableScene import ZoomableScene
from urh.cythonext import path_creator
from urh.cythonext import util


class SceneManager(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.scene = ZoomableScene()
        self.plot_data = np.array([0] * 100)
        self.line_item = self.scene.addLine(0, 0, 0, 0, QPen(constants.AXISCOLOR,  Qt.FlatCap))
        self.text_item = self.scene.addText("",  QFont("Helvetica", 20))
        self.minimum = float("nan")  # NaN = AutoDetect
        self.maximum = float("nan")  # NaN = AutoDetect
        self.path_item = self.scene.addPath(QPainterPath(), QPen(constants.LINECOLOR,  Qt.FlatCap))
        """:type: QGraphicsPathItem """

        self.padding = 1.25

    @property
    def num_samples(self):
        return len(self.plot_data)

    def show_scene_section(self, x1: float, x2: float):
        path = path_creator.create_path(self.plot_data, self.__limit_value(x1), self.__limit_value(x2))
        self.path_item.setPath(path)

    def __limit_value(self, val):
        if val < 0:
            return 0
        elif val > self.num_samples:
            return self.num_samples
        return int(val)

    def show_full_scene(self):
        self.show_scene_section(0, self.num_samples)

    def init_scene(self):
        self.set_text("")

        if self.num_samples == 0:
            return

        if math.isnan(self.minimum) or math.isnan(self.maximum):
            minimum, maximum = util.minmax(self.plot_data)
        else:
            minimum, maximum = self.minimum, self.maximum

        if abs(minimum) > abs(maximum):
            minimum = -self.padding*abs(minimum)
            maximum = -self.padding*minimum
        else:
            maximum = abs(maximum)
            minimum = -maximum

        # self.scene.setSceneRect(0, -1, num_samples, 2)
        self.scene.setSceneRect(0, minimum, self.num_samples, maximum - minimum)
        self.scene.setBackgroundBrush(constants.BGCOLOR)
        self.line_item.setLine(0, 0, self.num_samples, 0)

    def clear_path(self):
        self.path_item.setPath(QPainterPath())

    def set_text(self, text):
        self.text_item.setPlainText(text)

    @staticmethod
    def create_rectangle(proto_bits, pulse_len=100):
        """
        :type proto_bits: list of str
        """
        ones = np.ones(pulse_len, dtype=np.float32) * 1
        zeros = np.ones(pulse_len, dtype=np.float32) * -1
        n = 0
        y = []
        for block in proto_bits:
            for bit in block:
                n += pulse_len
                if bit == "0":
                    y.extend(zeros)
                else:
                    y.extend(ones)
        x = np.arange(0, n).astype(np.int64)
        scene = ZoomableScene()
        scene.setSceneRect(0, -1, n, 2)
        scene.setBackgroundBrush(constants.BGCOLOR)
        scene.addLine(0, 0, n, 0, QPen(constants.AXISCOLOR, Qt.FlatCap))
        if len(y) > 0:
            y = np.array(y)
        else:
            y = np.array(y).astype(np.float32)
        path = path_creator.array_to_QPath(x, y)
        scene.addPath(path, QPen(constants.LINECOLOR, Qt.FlatCap))
        return scene, n
