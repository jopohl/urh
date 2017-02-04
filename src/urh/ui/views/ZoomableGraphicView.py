from PyQt5.QtCore import pyqtSignal, QRectF
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QGraphicsScene

from urh.SceneManager import SceneManager
from urh.ui.views.SelectableGraphicView import SelectableGraphicView


class ZoomableGraphicView(SelectableGraphicView):
    zoomed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.margin = 0.25
        self.min_width = 100
        self.max_width = "auto"

        self.zoomed.connect(self.handle_signal_zoomed_or_scrolled)
        self.horizontalScrollBar().valueChanged.connect(self.handle_signal_zoomed_or_scrolled)


    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()

        zoom_factor = 1.001 ** delta
        p0scene = self.mapToScene(event.pos())
        w = self.view_rect().width()
        zooming_in = zoom_factor > 1
        if zooming_in and w / zoom_factor < self.min_width:
            return

        max_width = self.max_width
        if self.max_width == "auto":
            max_width = self.sceneRect().width()
        if not zooming_in and w / zoom_factor >= max_width and max_width:
            zoom_factor = w / max_width

        self.scale(zoom_factor, 1)
        p1mouse = self.mapFromScene(p0scene)
        move = p1mouse - event.pos()
        self.horizontalScrollBar().setValue(move.x() + self.horizontalScrollBar().value())
        self.zoomed.emit(zoom_factor)

    def update(self, *__args):
        super().update(*__args)
        vr = self.view_rect()

        self.fitInView(vr.x(), self.sceneRect().y() - self.margin, vr.width(), self.sceneRect().height() + self.margin)
        self.horizontalScrollBar().blockSignals(False)

    def draw_full(self):
        rect = self.sceneRect()
        self.fitInView(rect.x(), rect.y() -self.margin, rect.width(), rect.height() + self.margin)

    def setScene(self, scene: QGraphicsScene):
        super().setScene(scene)
        self.margin = 0.25 * self.scene().height()

    def plot_data(self, data):
        self.horizontalScrollBar().blockSignals(True)

        self.scene_creator = SceneManager(self)
        self.scene_creator.plot_data = data
        self.scene_creator.init_scene()
        self.setScene(self.scene_creator.scene)
        self.scene_creator.show_full_scene()
        self.update()

    def handle_signal_zoomed_or_scrolled(self):
        if self.scene_creator is not None:
            x1 = self.view_rect().x()
            x2 = x1 + self.view_rect().width()
            self.scene_creator.show_scene_section(x1, x2)

    def resizeEvent(self, event: QResizeEvent):
        self.draw_full()
        event.accept()