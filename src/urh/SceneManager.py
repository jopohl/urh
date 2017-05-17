import math

import numpy as np
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QFont, QPen, QColor
from PyQt5.QtWidgets import QGraphicsPathItem

from urh import constants
from urh.cythonext import path_creator, util
from urh.ui.ZoomableScene import ZoomableScene
from urh.util.Logger import logger


class SceneManager(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.scene = ZoomableScene()
        self.__plot_data = None  # type: np.ndarray
        self.line_item = self.scene.addLine(0, 0, 0, 0, QPen(constants.AXISCOLOR, Qt.FlatCap))
        self.minimum = float("nan")  # NaN = AutoDetect
        self.maximum = float("nan")  # NaN = AutoDetect

        self.padding = 1.25

    @property
    def plot_data(self):
        return self.__plot_data

    @plot_data.setter
    def plot_data(self, value):
        self.__plot_data = value

    @property
    def num_samples(self):
        return len(self.plot_data)

    def show_scene_section(self, x1: float, x2: float, subpath_ranges=None, colors=None):
        """

        :param x1: start of section to show
        :param x2: end of section to show
        :param subpath_ranges: for coloring subpaths
        :type subpath_ranges: list of tuple
        :param colors: for coloring the subpaths
        :type color: list of QColor
        :return:
        """
        paths = path_creator.create_path(self.plot_data, start=self.__limit_value(x1),
                                         end=self.__limit_value(x2),
                                         subpath_ranges=subpath_ranges)
        self.set_path(paths, colors=colors)

    def set_path(self, paths: list, colors=None):
        self.clear_path()
        colors = [constants.LINECOLOR] * len(paths) if colors is None else colors
        assert len(paths) == len(colors)
        for path, color in zip(paths, colors):
            self.scene.addPath(path, QPen(color if color else constants.LINECOLOR, Qt.FlatCap))

    def __limit_value(self, val: float) -> int:
        return 0 if val < 0 else self.num_samples if val > self.num_samples else int(val)

    def show_full_scene(self):
        self.show_scene_section(0, self.num_samples)

    def init_scene(self, apply_padding=True):
        if self.num_samples == 0:
            return

        if math.isnan(self.minimum) or math.isnan(self.maximum):
            minimum, maximum = util.minmax(self.plot_data)
        else:
            minimum, maximum = self.minimum, self.maximum

        padding = self.padding if apply_padding else 1

        if abs(minimum) > abs(maximum):
            minimum = -padding * abs(minimum)
            maximum = -padding * minimum
        else:
            maximum = padding * abs(maximum)
            minimum = -padding * maximum

        self.scene.setSceneRect(0, minimum, self.num_samples, maximum - minimum)
        self.scene.setBackgroundBrush(constants.BGCOLOR)

        if self.line_item is not None:
            self.line_item.setLine(0, 0, self.num_samples, 0)

    def clear_path(self):
        for item in self.scene.items():
            if isinstance(item, QGraphicsPathItem):
                self.scene.removeItem(item)
                item.setParentItem(None)
                del item

    def eliminate(self):
        self.plot_data = None
        self.line_item = None
        self.scene.clear()
        self.scene.setParent(None)

    @staticmethod
    def create_rectangle(proto_bits, pulse_len=100):
        """
        :type proto_bits: list of str
        """
        ones = np.ones(pulse_len, dtype=np.float32) * 1
        zeros = np.ones(pulse_len, dtype=np.float32) * -1
        n = 0
        y = []
        for msg in proto_bits:
            for bit in msg:
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
