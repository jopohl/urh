import math

import numpy as np
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsPathItem
from urh.signalprocessing.IQArray import IQArray

from urh import settings
from urh.cythonext import path_creator, util
from urh.ui.painting.ZoomableScene import ZoomableScene


class SceneManager(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.scene = ZoomableScene()
        self.__plot_data = None  # type: np.ndarray
        self.line_item = self.scene.addLine(0, 0, 0, 0, QPen(settings.AXISCOLOR, 0))

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
        start, end = self.__limit_value(x1), self.__limit_value(x2)

        if end > start:
            paths = path_creator.create_path(self.plot_data, start=start, end=end,
                                             subpath_ranges=subpath_ranges)
            self.set_path(paths, colors=colors)

    def set_path(self, paths: list, colors=None):
        self.clear_path()
        colors = [settings.LINECOLOR] * len(paths) if colors is None else colors
        assert len(paths) == len(colors)
        for path, color in zip(paths, colors):
            path_object = self.scene.addPath(path, QPen(color if color else settings.LINECOLOR, 0))
            if color:
                path_object.setZValue(1)

    def __limit_value(self, val: float) -> int:
        return 0 if val < 0 else self.num_samples if val > self.num_samples else int(val)

    def show_full_scene(self):
        self.show_scene_section(0, self.num_samples)

    def init_scene(self):
        if self.num_samples == 0:
            return

        minimum, maximum = IQArray.min_max_for_dtype(self.plot_data.dtype)
        self.scene.setSceneRect(0, minimum, self.num_samples, maximum - minimum)
        self.scene.setBackgroundBrush(settings.BGCOLOR)

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
        scene.setBackgroundBrush(settings.BGCOLOR)
        scene.addLine(0, 0, n, 0, QPen(settings.AXISCOLOR, 0))
        if len(y) > 0:
            y = np.array(y)
        else:
            y = np.array(y).astype(np.float32)
        path = path_creator.array_to_QPath(x, y)
        scene.addPath(path, QPen(settings.LINECOLOR, 0))
        return scene, n
