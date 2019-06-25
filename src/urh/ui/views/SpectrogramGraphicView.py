import numpy as np
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QMenu

from urh.controller.dialogs.FilterBandwidthDialog import FilterBandwidthDialog
from urh.signalprocessing.Filter import Filter
from urh.ui.painting.SpectrogramScene import SpectrogramScene
from urh.ui.painting.SpectrogramSceneManager import SpectrogramSceneManager
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView
from urh.util.Logger import logger


class SpectrogramGraphicView(ZoomableGraphicView):
    MINIMUM_VIEW_WIDTH = 10
    y_scale_changed = pyqtSignal(float)
    bandpass_filter_triggered = pyqtSignal(float, float)
    export_fta_wanted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.move_y_with_drag = True
        self.scene_manager = SpectrogramSceneManager(np.zeros(1, dtype=np.complex64), parent=self)
        self.setScene(self.scene_manager.scene)

    @property
    def y_center(self):
        return self.sceneRect().height() // 2

    @property
    def height_spectrogram(self):
        if self.scene_manager and self.scene_manager.spectrogram:
            return self.scene_manager.spectrogram.freq_bins
        else:
            return 0

    @property
    def width_spectrogram(self):
        if self.scene_manager and self.scene_manager.spectrogram:
            return self.scene_manager.spectrogram.time_bins
        else:
            return 0

    def scene(self) -> SpectrogramScene:
        return super().scene()

    def create_context_menu(self):
        menu = QMenu()
        menu.setToolTipsVisible(True)
        self._add_zoom_actions_to_menu(menu)

        if self.something_is_selected:
            filter_bw = Filter.read_configured_filter_bw()
            text = self.tr("Apply bandpass filter (filter bw={0:n})".format(filter_bw))
            create_from_frequency_selection = menu.addAction(text)
            create_from_frequency_selection.triggered.connect(self.on_create_from_frequency_selection_triggered)
            create_from_frequency_selection.setIcon(QIcon.fromTheme("view-filter"))

            try:
                cancel_button = " or ".join(k.toString() for k in QKeySequence.keyBindings(QKeySequence.Cancel))
            except Exception as e:
                logger.debug("Error reading cancel button: " + str(e))
                cancel_button = "Esc"

            create_from_frequency_selection.setToolTip("You can abort filtering with <b>{}</b>.".format(cancel_button))

        configure_filter_bw = menu.addAction(self.tr("Configure filter bandwidth..."))
        configure_filter_bw.triggered.connect(self.on_configure_filter_bw_triggered)
        configure_filter_bw.setIcon(QIcon.fromTheme("configure"))

        menu.addSeparator()

        export_fta_action = menu.addAction("Export spectrogram...")
        export_fta_action.triggered.connect(self.on_export_fta_action_triggered)

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
        self.bandpass_filter_triggered.emit(*self.__get_freqs())

    def __get_freqs(self):
        sh = self.sceneRect().height()
        y1, y2 = sh / 2 - self.selection_area.start, sh / 2 - self.selection_area.end
        f_low, f_high = y1 / self.sceneRect().height(), y2 / self.sceneRect().height()
        return f_low, f_high

    @pyqtSlot()
    def on_configure_filter_bw_triggered(self):
        dialog = FilterBandwidthDialog(parent=self)
        dialog.show()

    @pyqtSlot()
    def on_export_fta_action_triggered(self):
        if not(self.scene_manager and self.scene_manager.spectrogram):
            return

        self.export_fta_wanted.emit()
