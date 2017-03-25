from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QGraphicsView


class LegendGraphicView(QGraphicsView):
    resized = pyqtSignal()

    def __init__(self, parent=None):
        self.ysep = 0
        self.y_scene = -1
        self.scene_height = 2
        super().__init__(parent)

    def eliminate(self):
        if self.scene() is not None:
            self.scene().clear()
            self.scene().setParent(None)

        self.setParent(None)
        self.destroy()
        self.deleteLater()

    def resizeEvent(self, event):
        self.resized.emit()

    def refresh(self):
        if self.scene() is not None:
            self.resetTransform()
            self.scene().setSceneRect(0, self.y_scene, self.width(), self.scene_height)
            self.scene().draw_one_zero_arrows(self.ysep)
            self.fitInView(self.sceneRect())
            self.show()

    def wheelEvent(self, event: QWheelEvent):
        return
