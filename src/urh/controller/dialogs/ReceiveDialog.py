import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox

from urh.controller.dialogs.SendRecvDialog import SendRecvDialog
from urh.dev.VirtualDevice import Mode, VirtualDevice
from urh.ui.painting.LiveSceneManager import LiveSceneManager
from urh.util import FileOperator
from urh.util.Formatter import Formatter
from datetime import datetime

class ReceiveDialog(SendRecvDialog):
    files_recorded = pyqtSignal(list, float)

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

        self.setWindowTitle("Record Signal")
        self.setWindowIcon(QIcon.fromTheme("media-record"))

        # set really in on_device_started
        self.scene_manager = None  # type: LiveSceneManager
        self.create_connects()
        self.device_settings_widget.update_for_new_device(overwrite_settings=False)

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

        try:
            sample_rate = self.device.sample_rate
        except:
            sample_rate = 1e6

        self.files_recorded.emit(self.recorded_files, sample_rate)
        return True

    def update_view(self):
        if super().update_view():
            self.scene_manager.end = self.device.current_index
            self.scene_manager.init_scene()
            self.scene_manager.show_full_scene()
            self.graphics_view.update()

    def init_device(self):
        self.device = VirtualDevice(self.backend_handler, self.selected_device_name, Mode.receive,
                                    device_ip="192.168.10.2", parent=self)
        self._create_device_connects()
        self.scene_manager = LiveSceneManager(np.array([], dtype=self.device.data_type), parent=self)

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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        initial_name = "{0}-{1}-{2}Hz-{3}Sps".format(dev.name, timestamp,
                                                     big_val(dev.frequency), big_val(dev.sample_rate))

        if dev.bandwidth_is_adjustable:
            initial_name += "-{}Hz".format(big_val(dev.bandwidth))

        initial_name = initial_name.replace(Formatter.local_decimal_seperator(), "_").replace("_000", "")

        filename = FileOperator.ask_signal_file_name_and_save(initial_name, data,
                                                              sample_rate=dev.sample_rate, parent=self)
        self.already_saved = True
        if filename is not None and filename not in self.recorded_files:
            self.recorded_files.append(filename)
