from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QCloseEvent

from urh.controller.dialogs.SendDialog import SendDialog
from urh.controller.dialogs.SendRecvDialog import SendRecvDialog
from urh.dev.VirtualDevice import VirtualDevice, Mode
from urh.signalprocessing.ContinuousModulator import ContinuousModulator
from urh.ui.painting.ContinuousSceneManager import ContinuousSceneManager


class ContinuousSendDialog(SendDialog):
    def __init__(self, project_manager, messages, modulators, total_samples: int, parent, testing_mode=False):
        super().__init__(project_manager, modulated_data=None, modulation_msg_indices=None,
                         continuous_send_mode=True, parent=parent, testing_mode=testing_mode)
        self.messages = messages
        self.modulators = modulators

        self.graphics_view = self.ui.graphicsViewContinuousSend
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_continuous_send)
        self.ui.progressBarSample.hide()
        self.ui.lSamplesSentText.hide()

        self.total_samples = total_samples
        self.ui.progressBarMessage.setMaximum(len(messages))

        num_repeats = self.device_settings_widget.ui.spinBoxNRepeat.value()
        self.continuous_modulator = ContinuousModulator(messages, modulators, num_repeats=num_repeats)
        self.scene_manager = ContinuousSceneManager(ring_buffer=self.continuous_modulator.ring_buffer, parent=self)
        self.scene_manager.init_scene()
        self.graphics_view.setScene(self.scene_manager.scene)
        self.graphics_view.scene_manager = self.scene_manager

        self.setWindowTitle("Send Signal (continuous mode)")
        self.ui.lSamplesSentText.setText("Progress:")

        self.create_connects()
        self.device_settings_widget.update_for_new_device(overwrite_settings=False)

    def create_connects(self):
        SendRecvDialog.create_connects(self)

    def _update_send_indicator(self, width: int):
        pass

    def update_view(self):
        super().update_view()
        self.ui.progressBarMessage.setValue(self.continuous_modulator.current_message_index.value + 1)
        self.scene_manager.init_scene()
        self.scene_manager.show_full_scene()
        self.graphics_view.update()

    def closeEvent(self, event: QCloseEvent):
        self.continuous_modulator.stop()
        super().closeEvent(event)

    @pyqtSlot()
    def on_device_started(self):
        super().on_device_started()

    @pyqtSlot()
    def on_device_stopped(self):
        super().on_device_stopped()
        self.continuous_modulator.stop(clear_buffer=False)

    @pyqtSlot()
    def on_stop_clicked(self):
        super().on_stop_clicked()
        self.continuous_modulator.stop()
        self.continuous_modulator.current_message_index.value = 0
        self.scene_manager.clear_path()

    @pyqtSlot()
    def on_start_clicked(self):
        self.device_settings_widget.ui.spinBoxNRepeat.editingFinished.emit()  # inform continuous modulator
        if not self.continuous_modulator.is_running:
            self.continuous_modulator.start()
        super().on_start_clicked()

    @pyqtSlot()
    def on_clear_clicked(self):
        self.continuous_modulator.stop()
        self.continuous_modulator.current_message_index.value = 0
        self.scene_manager.clear_path()
        self.reset()

    @pyqtSlot()
    def on_num_repeats_changed(self):
        super().on_num_repeats_changed()
        self.continuous_modulator.num_repeats = self.device_settings_widget.ui.spinBoxNRepeat.value()

    def on_selected_device_changed(self):
        self.ui.txtEditErrors.clear()
        super().on_selected_device_changed()

    def init_device(self):
        device_name = self.selected_device_name
        num_repeats = self.device_settings_widget.ui.spinBoxNRepeat.value()

        self.device = VirtualDevice(self.backend_handler, device_name, Mode.send,
                                    device_ip="192.168.10.2", sending_repeats=num_repeats, parent=self)
        self.ui.btnStart.setEnabled(True)

        try:
            self.device.is_send_continuous = True
            self.device.continuous_send_ring_buffer = self.continuous_modulator.ring_buffer
            self.device.num_samples_to_send = self.total_samples

            self._create_device_connects()
        except ValueError as e:
            self.ui.txtEditErrors.setText("<font color='red'>" + str(e) + "<font>")
            self.ui.btnStart.setEnabled(False)
