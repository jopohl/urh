from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu

from urh.ui.painting.SpectrogramScene import SpectrogramScene
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView


class SpectrogramGraphicView(ZoomableGraphicView):
    MINIMUM_VIEW_WIDTH = 10
    y_scale_changed = pyqtSignal(float)
    bandpass_filter_triggered = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.move_y_with_drag = True
        self.setScene(SpectrogramScene())

    @property
    def y_center(self):
        return self.sceneRect().height() // 2

    def scene(self) -> SpectrogramScene:
        return super().scene()

    def create_context_menu(self):
        menu = QMenu()
        self._add_zoom_actions_to_menu(menu)

        if self.something_is_selected:
            create_from_frequency_selection = menu.addAction("Create signal from frequency selection")
            create_from_frequency_selection.triggered.connect(self.on_create_from_frequency_selection_triggered)
            create_from_frequency_selection.setIcon(QIcon.fromTheme("view-filter"))

        return menu

    def zoom_to_selection(self, start: int, end: int):
        if start == end:
            return

        x_center = self.view_rect().x() + self.view_rect().width() / 2
        y_factor = self.view_rect().height() / (end - start)
        self.scale(1, y_factor)
        self.centerOn(x_center, start + (end - start) / 2)
        self.y_scale_changed.emit(y_factor)

    def auto_fit_view(self):
        pass

    def emit_selection_start_end_changed(self):
        h = self.sceneRect().height()
        self.sel_area_start_end_changed.emit(h - self.selection_area.end, h - self.selection_area.start)

    @pyqtSlot()
    def on_create_from_frequency_selection_triggered(self):
        sh = self.sceneRect().height()
        y1, y2 = sh / 2 - self.selection_area.start, sh / 2 - self.selection_area.end
        if y1 > y2:
            y1, y2 = y2, y1
        f_low, f_high = y1 / self.sceneRect().height(), y2 / self.sceneRect().height()
        self.bandpass_filter_triggered.emit(f_low, f_high)
