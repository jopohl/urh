from PyQt5.QtCore import QTimer, pyqtSlot, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence, QWheelEvent, QCursor
from PyQt5.QtWidgets import QAction, QGraphicsScene

from urh.SceneManager import SceneManager
from urh.ui.views.SelectableGraphicView import SelectableGraphicView
from urh.util.Logger import logger


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

    def scrollContentsBy(self, dx: int, dy: int):
        try:
            super().scrollContentsBy(dx, dy)
            self.redraw_timer.start(0)
        except RuntimeError as e:
            logger.warning("Graphic View already closed: " + str(e))

    def zoom(self, factor, zoom_to_mouse_cursor=True, cursor_pos=None):
        if factor > 1 and self.view_rect().width() / factor < 300:
            factor = self.view_rect().width() / 300

        if zoom_to_mouse_cursor:
            pos = self.mapFromGlobal(QCursor.pos()) if cursor_pos is None else cursor_pos
        else:
            pos = None
        old_pos = self.mapToScene(pos) if pos is not None else None

        if self.view_rect().width() / factor > self.sceneRect().width():
            self.show_full_scene()
            factor = 1

        self.scale(factor, 1)
        self.zoomed.emit(factor)

        if pos is not None:
            move = self.mapToScene(pos) - old_pos
            self.translate(move.x(), 0)

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.001 ** event.angleDelta().y()
        self.zoom(zoom_factor, cursor_pos=event.pos())

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
        self.zoom(x_factor, zoom_to_mouse_cursor=False)
        self.centerOn(start + (end - start) / 2, self.y_center)

    def setScene(self, scene: QGraphicsScene):
        super().setScene(scene)
        if self.scene() is not None:
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

    def eliminate(self):
        self.redraw_timer.stop()
        super().eliminate()

    @pyqtSlot()
    def on_signal_zoomed(self):
        self.redraw_timer.start(30)

    @pyqtSlot()
    def on_zoom_in_action_triggered(self):
        self.zoom(1.1)

    @pyqtSlot()
    def on_zoom_out_action_triggered(self):
        self.zoom(0.9)
