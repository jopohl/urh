from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtGui import QWheelEvent, QIcon, QPixmap, QResizeEvent
from PyQt5.QtWidgets import QGraphicsScene

from urh.controller.SendRecvDialogController import SendRecvDialogController
from urh.dev.VirtualDevice import VirtualDevice, Mode
from urh.signalprocessing.Spectrogram import Spectrogram
from urh.ui.painting.FFTSceneManager import FFTSceneManager


class SpectrumDialogController(SendRecvDialogController):
    def __init__(self, project_manager, parent=None, testing_mode=False):
        super().__init__(project_manager, is_tx=False, parent=parent, testing_mode=testing_mode)

        self.graphics_view = self.ui.graphicsViewFFT
        self.update_interval = 1
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_spectrum)
        self.hide_receive_ui_items()
        self.hide_send_ui_items()

        self.setWindowTitle("Spectrum Analyzer")
        self.setWindowIcon(QIcon(":/icons/data/icons/spectrum.svg"))
        self.ui.btnStart.setToolTip(self.tr("Start"))
        self.ui.btnStop.setToolTip(self.tr("Stop"))

        self.scene_manager = FFTSceneManager(parent=self, graphic_view=self.graphics_view)

        self.graphics_view.setScene(self.scene_manager.scene)
        self.graphics_view.scene_manager = self.scene_manager

        self.ui.graphicsViewSpectrogram.setScene(QGraphicsScene())
        self.__clear_spectrogram()

        self.init_device()
        self.set_bandwidth_status()

        self.gain_timer = QTimer()
        self.gain_timer.setSingleShot(True)
        self.gain_timer.timeout.connect(self.ui.spinBoxGain.editingFinished.emit)

        self.if_gain_timer = QTimer()
        self.if_gain_timer.setSingleShot(True)
        self.if_gain_timer.timeout.connect(self.ui.spinBoxIFGain.editingFinished.emit)

        self.bb_gain_timer = QTimer()
        self.bb_gain_timer.setSingleShot(True)
        self.bb_gain_timer.timeout.connect(self.ui.spinBoxBasebandGain.editingFinished.emit)

        self.create_connects()

    def __clear_spectrogram(self):
        self.ui.graphicsViewSpectrogram.scene().clear()
        window_size = Spectrogram.DEFAULT_FFT_WINDOW_SIZE
        self.ui.graphicsViewSpectrogram.scene().setSceneRect(0, 0, window_size, 20 * window_size)
        self.spectrogram_y_pos = 0
        self.ui.graphicsViewSpectrogram.fitInView(self.ui.graphicsViewSpectrogram.sceneRect())

    def __update_spectrogram(self):
        spectrogram = Spectrogram(self.device.data)
        spectrogram.data_min = -70
        spectrogram.data_max = 10
        scene = self.ui.graphicsViewSpectrogram.scene()
        pixmap = QPixmap.fromImage(spectrogram.create_spectrogram_image(transpose=True))
        scene.addPixmap(pixmap).moveBy(0, self.spectrogram_y_pos)
        self.spectrogram_y_pos += pixmap.height()
        if self.spectrogram_y_pos >= scene.sceneRect().height():
            scene.setSceneRect(0, 0, Spectrogram.DEFAULT_FFT_WINDOW_SIZE, self.spectrogram_y_pos)
            self.ui.graphicsViewSpectrogram.verticalScrollBar().setValue(
                self.ui.graphicsViewSpectrogram.verticalScrollBar().maximum())

    def _eliminate_graphic_view(self):
        super()._eliminate_graphic_view()
        if self.ui.graphicsViewSpectrogram.scene() is not None:
            self.ui.graphicsViewSpectrogram.scene().clear()
            self.ui.graphicsViewSpectrogram.scene().setParent(None)
            self.ui.graphicsViewSpectrogram.setScene(None)

        self.ui.graphicsViewSpectrogram = None

    def create_connects(self):
        super().create_connects()
        self.graphics_view.freq_clicked.connect(self.on_graphics_view_freq_clicked)
        self.graphics_view.wheel_event_triggered.connect(self.on_graphics_view_wheel_event_triggered)

    def resizeEvent(self, event: QResizeEvent):
        if self.ui.graphicsViewSpectrogram and self.ui.graphicsViewSpectrogram.sceneRect():
            self.ui.graphicsViewSpectrogram.fitInView(self.ui.graphicsViewSpectrogram.sceneRect())

    def update_view(self):
        if super().update_view():
            x, y = self.device.spectrum
            if x is None or y is None:
                return
            self.scene_manager.scene.frequencies = x
            self.scene_manager.plot_data = y
            self.scene_manager.init_scene()
            self.scene_manager.show_full_scene()
            self.graphics_view.fitInView(self.graphics_view.sceneRect())

            self.__update_spectrogram()

    def init_device(self):
        device_name = self.ui.cbDevice.currentText()
        self.device = VirtualDevice(self.backend_handler, device_name, Mode.spectrum,
                                    device_ip="192.168.10.2", parent=self)
        self._create_device_connects()

    @pyqtSlot(QWheelEvent)
    def on_graphics_view_wheel_event_triggered(self, event: QWheelEvent):
        self.ui.sliderYscale.wheelEvent(event)

    @pyqtSlot(float)
    def on_graphics_view_freq_clicked(self, freq: float):
        self.ui.spinBoxFreq.setValue(freq)
        self.ui.spinBoxFreq.editingFinished.emit()

    @pyqtSlot()
    def on_spinbox_frequency_editing_finished(self):
        self.device.frequency = self.ui.spinBoxFreq.value()
        self.scene_manager.scene.center_freq = self.ui.spinBoxFreq.value()
        self.scene_manager.clear_path()
        self.scene_manager.clear_peak()

    @pyqtSlot()
    def on_start_clicked(self):
        super().on_start_clicked()
        self.device.start()

    @pyqtSlot()
    def on_device_started(self):
        self.ui.graphicsViewSpectrogram.fitInView(self.ui.graphicsViewSpectrogram.scene().sceneRect())
        super().on_device_started()
        self.ui.btnClear.setEnabled(True)
        self.ui.spinBoxPort.setEnabled(False)
        self.ui.lineEditIP.setEnabled(False)
        self.ui.btnStart.setEnabled(False)

    @pyqtSlot()
    def on_clear_clicked(self):
        self.__clear_spectrogram()
        self.scene_manager.clear_path()
        self.scene_manager.clear_peak()

    @pyqtSlot(int)
    def on_slider_gain_value_changed(self, value: int):
        super().on_slider_gain_value_changed(value)
        self.gain_timer.start(250)

    @pyqtSlot(int)
    def on_slider_if_gain_value_changed(self, value: int):
        super().on_slider_if_gain_value_changed(value)
        self.if_gain_timer.start(250)

    @pyqtSlot(int)
    def on_slider_baseband_gain_value_changed(self, value: int):
        super().on_slider_baseband_gain_value_changed(value)
        self.bb_gain_timer.start(250)
