from PyQt5.QtCore import pyqtSlot

from urh.FFTSceneManager import FFTSceneManager
from urh.controller.SendRecvDialogController import SendRecvDialogController
from urh.dev.VirtualDevice import VirtualDevice, Mode


class SpectrumDialogController(SendRecvDialogController):
    def __init__(self, freq, samp_rate, bw, gain, device: str, parent=None, testing_mode=False):
        self.is_rx = True
        super().__init__(freq, samp_rate, bw, gain, device, parent=parent, testing_mode=testing_mode)

        self.graphics_view = self.ui.graphicsViewReceive
        self.update_interval = 1
        self.ui.stackedWidget.setCurrentIndex(0)
        self.hide_receive_ui_items()
        self.hide_send_ui_items()

        self.setWindowTitle("Spectrum analyzer")

        self.scene_manager = FFTSceneManager(parent=self, graphic_view=self.graphics_view)

        self.graphics_view.setScene(self.scene_manager.scene)
        self.graphics_view.scene_manager = self.scene_manager

        self.init_device()

        self.create_connects()

    def create_connects(self):
        super().create_connects()
        self.graphics_view.freq_clicked.connect(self.on_graphics_view_freq_clicked)

    def update_view(self):
        if super().update_view():
            x, y = self.device.spectrum
            if x is None or y is None:
                return
            self.scene_manager.scene.frequencies = x
            self.scene_manager.plot_data = y
            self.scene_manager.init_scene()
            self.scene_manager.show_full_scene()
            self.graphics_view.update()

    def init_device(self):
        device_name = self.ui.cbDevice.currentText()
        if self.device:
            self.device.free_data()
        # Can't perform gc.collect() here, because the dialog itself would be deleted
        # see https://github.com/jopohl/urh/issues/83
        # gc.collect()
        self.device = VirtualDevice(self.backend_handler, device_name, Mode.spectrum, bw=1e6,
                                    freq=433.92e6, gain=40, samp_rate=1e6,
                                    device_ip="192.168.10.2", parent=self)
        self._create_device_connects()

    @pyqtSlot(float)
    def on_graphics_view_freq_clicked(self, freq: float):
        self.ui.spinBoxFreq.setValue(freq)
        self.ui.spinBoxFreq.editingFinished.emit()

    @pyqtSlot()
    def on_freq_changed(self):
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
        super().on_device_started()
        self.ui.btnClear.setEnabled(False)
        self.ui.btnStart.setEnabled(False)

    @pyqtSlot()
    def on_clear_clicked(self):
        self.scene_manager.clear_path()
        self.scene_manager.clear_peak()
