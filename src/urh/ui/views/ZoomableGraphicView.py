from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QGraphicsScene

from urh.SceneManager import SceneManager
from urh.ui.views.SelectableGraphicView import SelectableGraphicView


class ZoomableGraphicView(SelectableGraphicView):
    zoomed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.zoom_in_action = QAction(self.tr("Zoom in"), self)
        self.zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        self.zoom_in_action.triggered.connect(self.on_zoom_in_action_triggered)
        self.zoom_in_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.zoom_in_action.setIcon(QIcon.fromTheme("zoom-in"))
        self.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction(self.tr("Zoom out"), self)
        self.zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        self.zoom_out_action.triggered.connect(self.on_zoom_out_action_triggered)
        self.zoom_out_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.zoom_out_action.setIcon(QIcon.fromTheme("zoom-out"))
        self.addAction(self.zoom_out_action)

        self.margin = 0.25
        self.min_width = 100
        self.max_width = "auto"

        self.redraw_timer = QTimer()
        self.redraw_timer.setSingleShot(True)
        self.redraw_timer.timeout.connect(self.redraw_view)

        self.zoomed.connect(self.on_signal_zoomed)
        self.horizontalScrollBar().valueChanged.connect(self.on_signal_scrolled)

    @property
    def y_center(self):
        if not hasattr(self, "scene_type") or self.scene_type == 0:
            # Normal scene
            return 0
        else:
            return -self.signal.qad_center

    @property
    def scene_type(self):
        return 0  # gets overwritten in Epic Graphic View

    def zoom(self, factor, suppress_signal=False, event: QWheelEvent = None):
        if factor > 1 and self.view_rect().width() / factor < 300:
            factor = self.view_rect().width() / 300

        old_pos = self.mapToScene(event.pos()) if event is not None else None

        if self.view_rect().width() / factor > self.sceneRect().width():
            self.show_full_scene()
            factor = 1

        self.scale(factor, 1)

        if not suppress_signal:
            self.zoomed.emit(factor)

        if event:
            move = self.mapToScene(event.pos()) - old_pos
            self.translate(move.x(), 0)
        else:
            self.centerOn(self.view_rect().x() + self.view_rect().width() / 2, self.y_center)

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.001 ** event.angleDelta().y()
        self.zoom(zoom_factor, event=event)

    def resizeEvent(self, event):
        if self.sceneRect().width() == 0:
            return

        if self.view_rect().width() > self.sceneRect().width():
            x_factor = self.width() / self.sceneRect().width()
            self.scale(x_factor / self.transform().m11(), 1)

        self.auto_fit_view()

    def auto_fit_view(self):
        h_tar = self.sceneRect().height()
        h_view = self.view_rect().height()

        if abs(h_tar) > 0:
            self.scale(1, h_view / h_tar)
        self.centerOn(self.view_rect().x() + self.view_rect().width() / 2, self.y_center)

    def show_full_scene(self, reinitialize=False):
        y_factor = self.transform().m22()
        self.resetTransform()
        x_factor = self.width() / self.sceneRect().width() if self.sceneRect().width() else 1
        self.scale(x_factor, y_factor)
        self.centerOn(0, self.y_center)

        self.redraw_view(reinitialize)

    def zoom_to_selection(self, start: int, end: int):
        if start == end:
            return

        x_factor = self.view_rect().width() / (end - start)
        self.zoom(x_factor)
        self.centerOn(start + (end - start) / 2, self.y_center)

    def setScene(self, scene: QGraphicsScene):
        super().setScene(scene)
        self.margin = 0.25 * self.scene().height()

    def plot_data(self, data):
        if self.scene_manager is None:
            self.scene_manager = SceneManager(self)

        self.scene_manager.plot_data = data
        self.scene_manager.init_scene()
        self.setScene(self.scene_manager.scene)
        self.scene_manager.show_full_scene()

    def redraw_view(self, reinitialize=False):
        if self.scene_manager is not None:
            self.scene_manager.scene_type = self.scene_type
            if reinitialize:
                self.scene_manager.init_scene()
            vr = self.view_rect()
            start, end = vr.x(), vr.x() + vr.width()
            self.scene_manager.show_scene_section(start, end, *self._get_sub_path_ranges_and_colors(start, end))

    def _get_sub_path_ranges_and_colors(self, start: float, end: float):
        # Overwritten in Epic Graphic View
        return None, None

    @pyqtSlot()
    def on_signal_zoomed(self):
        self.redraw_timer.start(30)

    @pyqtSlot()
    def on_signal_scrolled(self):
        self.redraw_timer.start(0)

    @pyqtSlot()
    def on_zoom_in_action_triggered(self):
        self.zoom(1.1)

    @pyqtSlot()
    def on_zoom_out_action_triggered(self):
        self.zoom(0.9)
