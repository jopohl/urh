import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainterPath, QFont, QPen

from urh import constants
from urh.SceneManager import SceneManager
from urh.cythonext import path_creator
from urh.ui.GridScene import GridScene


class FFTSceneManager(SceneManager):
    def __init__(self, parent, graphic_view=None):
        self.peak = []

        super().__init__(parent)
        self.scene = GridScene(parent=graphic_view)
        self.scene.setBackgroundBrush(constants.BGCOLOR)

        self.init_scene(draw_grid=False)
        self.path_item = self.scene.addPath(QPainterPath(), QPen(constants.LINECOLOR,  Qt.FlatCap))
        """:type: QGraphicsPathItem """

        self.peak_item = self.scene.addPath(QPainterPath(), QPen(constants.PEAK_COLOR, Qt.FlatCap))
        """:type: QGraphicsPathItem """

        font = QFont("Helvetica", 20)
        font.setStyleHint(QFont.SansSerif, QFont.OpenGLCompatible)
        self.text_item = self.scene.addText("", font)

    def show_scene_section(self, x1: float, x2: float):
        start = int(x1) if x1 > 0 else 0
        end = int(x2) if x2 < self.num_samples else self.num_samples
        path = path_creator.create_path(np.log10(self.plot_data), start, end)
        self.path_item.setPath(path)

        try:
            peak_path = path_creator.create_path(np.log10(self.peak), start, end)
            self.peak_item.setPath(peak_path)
        except RuntimeWarning:
            pass

    def init_scene(self, draw_grid=True):
        self.scene.draw_grid = draw_grid
        minimum = -4.5
        maximum = 2
        # minimum = -np.log10(np.max(self.y)))

        self.peak = self.plot_data if len(self.peak) < self.num_samples else np.maximum(self.peak, self.plot_data)
        self.scene.setSceneRect(0, minimum, self.num_samples, maximum - minimum)

    def clear_path(self):
        super().clear_path()
        self.peak = []
        self.peak_item.setPath(QPainterPath())

    def set_text(self, text):
        self.scene.draw_grid = False
        super().set_text(text)
