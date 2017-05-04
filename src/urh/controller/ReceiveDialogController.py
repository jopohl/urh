import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMessageBox

from urh.LiveSceneManager import LiveSceneManager
from urh.controller.SendRecvDialogController import SendRecvDialogController
from urh.dev.VirtualDevice import Mode, VirtualDevice
from urh.util import FileOperator
from urh.util.Formatter import Formatter


class ReceiveDialogController(SendRecvDialogController):
    files_recorded = pyqtSignal(list)

    def __init__(self, project_manager, parent=None, testing_mode=False):
        try:
            super().__init__(project_manager, is_tx=False, parent=parent, testing_mode=testing_mode)
        except ValueError:
            return

        self.graphics_view = self.ui.graphicsViewReceive
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_receive)
        self.hide_send_ui_items()
        self.already_saved = True
        self.recorded_files = []

        # set really in on_device_started
        self.scene_manager = None  # type: LiveSceneManager

        self.init_device()
        self.set_bandwidth_status()

        self.graphics_view.setScene(self.scene_manager.scene)
        self.graphics_view.scene_manager = self.scene_manager

        self.create_connects()

    def create_connects(self):
        super().create_connects()
        self.ui.btnSave.clicked.connect(self.on_save_clicked)

    def save_before_close(self):
        if not self.already_saved and self.device.current_index > 0:
            reply = QMessageBox.question(self, self.tr("Save data?"),
                                         self.tr("Do you want to save the data you have captured so far?"),
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Abort)
            if reply == QMessageBox.Yes:
                self.on_save_clicked()
            elif reply == QMessageBox.Abort:
                return False

        self.files_recorded.emit(self.recorded_files)
        return True

    def update_view(self):
        if super().update_view():
            self.scene_manager.end = self.device.current_index
            self.scene_manager.init_scene()
            self.scene_manager.show_full_scene()
            self.graphics_view.update()

    def init_device(self):
        device_name = self.ui.cbDevice.currentText()
        self.device = VirtualDevice(self.backend_handler, device_name, Mode.receive,
                                    device_ip="192.168.10.2", parent=self)
        self._create_device_connects()
        self.scene_manager = LiveSceneManager(np.array([]), parent=self)

    @pyqtSlot()
    def on_start_clicked(self):
        super().on_start_clicked()
        self.device.start()

    @pyqtSlot()
    def on_device_started(self):
        self.scene_manager.plot_data = self.device.data.real if self.device.data is not None else None

        super().on_device_started()

        self.already_saved = False
        self.ui.btnStart.setEnabled(False)
        self.set_device_ui_items_enabled(False)

    @pyqtSlot()
    def on_clear_clicked(self):
        self.scene_manager.clear_path()
        self.reset()

    @pyqtSlot()
    def on_save_clicked(self):
        data = self.device.data[:self.device.current_index]

        dev = self.device
        big_val = Formatter.big_value_with_suffix
        initial_name = "{0}-{1}Hz-{2}Sps".format(dev.name, big_val(dev.frequency), big_val(dev.sample_rate))

        if dev.bandwidth_is_adjustable:
            initial_name += "-{}Hz".format(big_val(dev.bandwidth))

        initial_name = initial_name.replace(Formatter.local_decimal_seperator(), "_").replace("_000", "")

        filename = FileOperator.save_data_dialog(initial_name + ".complex", data, parent=self)
        self.already_saved = True
        if filename is not None and filename not in self.recorded_files:
            self.recorded_files.append(filename)
