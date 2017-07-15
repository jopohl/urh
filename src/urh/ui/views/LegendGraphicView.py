from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QGraphicsView


class LegendGraphicView(QGraphicsView):
    resized = pyqtSignal()

    def __init__(self, parent=None):
        self.y_sep = 0
        self.y_scene = -1
        self.scene_height = 2
        super().__init__(parent)

    def eliminate(self):
        if self.scene() is not None:
            self.scene().clear()
            self.scene().setParent(None)

    def resizeEvent(self, event):
        self.resized.emit()

    def refresh(self):
        if self.scene() is not None:
            self.resetTransform()
            self.scene().setSceneRect(0, self.y_scene, self.width(), self.scene_height)
            self.scene().draw_one_zero_arrows(self.y_sep)
            self.fitInView(self.sceneRect())
            self.show()

    def wheelEvent(self, event: QWheelEvent):
        return
