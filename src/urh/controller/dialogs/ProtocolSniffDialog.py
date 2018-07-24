import numpy as np
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QCloseEvent

from urh.controller.dialogs.SendRecvDialog import SendRecvDialog
from urh.controller.widgets.SniffSettingsWidget import SniffSettingsWidget
from urh.ui.painting.LiveSceneManager import LiveSceneManager
from urh.ui.painting.SniffSceneManager import SniffSceneManager
from urh.util import util


class ProtocolSniffDialog(SendRecvDialog):
    protocol_accepted = pyqtSignal(list)

    def __init__(self, project_manager, signal=None, signals=None, parent=None, testing_mode=False):
        super().__init__(project_manager, is_tx=False, parent=parent, testing_mode=testing_mode)

        self.graphics_view = self.ui.graphicsView_sniff_Preview
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_sniff)
        self.hide_send_ui_items()
        self.hide_receive_ui_items()
        self.ui.sliderYscale.hide()
        self.ui.label_y_scale.hide()

        signals = [] if signals is None else signals

        self.sniff_settings_widget = SniffSettingsWidget(project_manager=project_manager,
                                                         device_name=self.selected_device_name,
                                                         signal=signal, signals=signals,
                                                         backend_handler=self.backend_handler)
        self.ui.scrollAreaWidgetContents_2.layout().insertWidget(1, self.sniff_settings_widget)
        self.sniff_settings_widget.ui.btn_sniff_use_signal.setAutoDefault(False)

        self.sniffer = self.sniff_settings_widget.sniffer
        self.setWindowTitle(self.tr("Sniff Protocol"))
        self.setWindowIcon(QIcon.fromTheme(":/icons/icons/sniffer.svg"))

        self.ui.txtEd_sniff_Preview.setFont(util.get_monospace_font())

        # set really in on_device_started
        self.scene_manager = None  # type: LiveSceneManager
        self.create_connects()
        self.device_settings_widget.update_for_new_device(overwrite_settings=False)





    @property
    def view_type(self) -> int:
        return self.sniff_settings_widget.ui.comboBox_sniff_viewtype.currentIndex()

    @property
    def show_timestamp(self) -> bool:
        return self.sniff_settings_widget.ui.checkBox_sniff_Timestamp.isChecked()

    def closeEvent(self, event: QCloseEvent):
        self.sniff_settings_widget.emit_sniff_parameters_changed()
        super().closeEvent(event)

    def create_connects(self):
        super().create_connects()
        self.ui.btnAccept.clicked.connect(self.on_btn_accept_clicked)
        self.sniff_settings_widget.sniff_parameters_changed.connect(self.device_parameters_changed.emit)

        self.sniff_settings_widget.sniff_setting_edited.connect(self.on_sniff_setting_edited)
        self.sniff_settings_widget.sniff_file_edited.connect(self.on_sniff_file_edited)
        self.sniffer.message_sniffed.connect(self.on_message_sniffed)
        self.sniffer.qt_signals.sniff_device_errors_changed.connect(self.on_device_errors_changed)

    def init_device(self):
        self.sniffer.device_name = self.selected_device_name
        self.device = self.sniffer.rcv_device

        self._create_device_connects()
        self.scene_manager = SniffSceneManager(np.array([]), parent=self)

    def emit_editing_finished_signals(self):
        super().emit_editing_finished_signals()
        self.sniff_settings_widget.emit_editing_finished_signals()

    def update_view(self):
        if super().update_view():
            self.scene_manager.end = self.device.current_index
            self.scene_manager.init_scene()
            self.scene_manager.show_full_scene()
            self.graphics_view.update()

    @pyqtSlot()
    def on_device_started(self):
        self.scene_manager.data_array = self.device.data.real if hasattr(self.device.data, "real") else None

        super().on_device_started()

        self.ui.btnStart.setEnabled(False)
        self.set_device_ui_items_enabled(False)

    @pyqtSlot()
    def on_sniff_setting_edited(self):
        self.ui.txtEd_sniff_Preview.setPlainText(self.sniffer.decoded_to_string(self.view_type,
                                                                                include_timestamps=self.show_timestamp))

    @pyqtSlot()
    def on_start_clicked(self):
        super().on_start_clicked()
        self.sniffer.sniff()

    @pyqtSlot()
    def on_stop_clicked(self):
        self.sniffer.stop()

    @pyqtSlot()
    def on_clear_clicked(self):
        self.ui.txtEd_sniff_Preview.clear()
        self.scene_manager.clear_path()
        self.device.current_index = 0
        self.sniffer.clear()

    @pyqtSlot(int)
    def on_message_sniffed(self, index: int):
        try:
            msg = self.sniffer.messages[index]
        except IndexError:
            return
        new_data = self.sniffer.message_to_string(msg, self.view_type, include_timestamps=self.show_timestamp)
        if new_data.strip():
            self.ui.txtEd_sniff_Preview.appendPlainText(new_data)
            self.ui.txtEd_sniff_Preview.verticalScrollBar().setValue(
                self.ui.txtEd_sniff_Preview.verticalScrollBar().maximum())

    @pyqtSlot()
    def on_btn_accept_clicked(self):
        self.protocol_accepted.emit(self.sniffer.messages)
        self.close()

    @pyqtSlot(str)
    def on_device_errors_changed(self, txt: str):
        self.ui.txtEditErrors.append(txt)

    @pyqtSlot()
    def on_sniff_file_edited(self):
        self.ui.btnAccept.setDisabled(bool(self.sniffer.sniff_file))
