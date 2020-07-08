import time

import numpy as np
from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox, QGraphicsTextItem

from urh import settings
from urh.controller.dialogs.ProtocolSniffDialog import ProtocolSniffDialog
from urh.controller.widgets.DeviceSettingsWidget import DeviceSettingsWidget
from urh.controller.widgets.ModulationSettingsWidget import ModulationSettingsWidget
from urh.controller.widgets.SniffSettingsWidget import SniffSettingsWidget
from urh.dev.BackendHandler import BackendHandler
from urh.dev.EndlessSender import EndlessSender
from urh.signalprocessing.IQArray import IQArray
from urh.simulator.Simulator import Simulator
from urh.simulator.SimulatorConfiguration import SimulatorConfiguration
from urh.ui.SimulatorScene import SimulatorScene
from urh.ui.painting.LiveSceneManager import LiveSceneManager
from urh.ui.painting.SniffSceneManager import SniffSceneManager
from urh.ui.ui_simulator_dialog import Ui_DialogSimulator
from urh.util import util, FileOperator
from urh.util.Errors import Errors
from urh.util.ProjectManager import ProjectManager


class SimulatorDialog(QDialog):
    rx_parameters_changed = pyqtSignal(dict)
    tx_parameters_changed = pyqtSignal(dict)
    sniff_parameters_changed = pyqtSignal(dict)
    open_in_analysis_requested = pyqtSignal(str)
    rx_file_saved = pyqtSignal(str)

    def __init__(self, simulator_config, modulators,
                 expression_parser, project_manager: ProjectManager, signals: list = None,
                 signal_tree_model=None,
                 parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogSimulator()
        self.ui.setupUi(self)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window)

        self.simulator_config = simulator_config  # type: SimulatorConfiguration
        self.rx_needed = self.simulator_config.rx_needed
        self.tx_needed = self.simulator_config.tx_needed

        self.current_transcript_index = 0

        self.simulator_scene = SimulatorScene(mode=1,
                                              simulator_config=self.simulator_config)
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.project_manager = project_manager

        self.update_interval = 25

        self.timer = QTimer(self)

        self.backend_handler = BackendHandler()
        if self.rx_needed:
            self.device_settings_rx_widget = DeviceSettingsWidget(project_manager,
                                                                  is_tx=False,
                                                                  backend_handler=self.backend_handler)

            self.sniff_settings_widget = SniffSettingsWidget(self.device_settings_rx_widget.ui.cbDevice.currentText(),
                                                             project_manager,
                                                             signal=None,
                                                             backend_handler=self.backend_handler,
                                                             network_raw_mode=True, signals=signals)

            self.device_settings_rx_widget.device = self.sniff_settings_widget.sniffer.rcv_device

            self.sniff_settings_widget.ui.lineEdit_sniff_OutputFile.hide()
            self.sniff_settings_widget.ui.label_sniff_OutputFile.hide()
            self.sniff_settings_widget.ui.label_sniff_viewtype.hide()
            self.sniff_settings_widget.ui.checkBox_sniff_Timestamp.hide()
            self.sniff_settings_widget.ui.comboBox_sniff_viewtype.hide()

            self.ui.scrollAreaWidgetContentsRX.layout().insertWidget(0, self.device_settings_rx_widget)
            self.ui.scrollAreaWidgetContentsRX.layout().insertWidget(1, self.sniff_settings_widget)

            sniffer = self.sniff_settings_widget.sniffer

            self.scene_manager = SniffSceneManager(np.array([], dtype=sniffer.rcv_device.data_type), parent=self)
            self.ui.graphicsViewPreview.setScene(self.scene_manager.scene)
        else:
            self.device_settings_rx_widget = self.sniff_settings_widget = self.scene_manager = None
            self.ui.tabWidgetSimulatorSettings.setTabEnabled(1, False)
            self.ui.graphicsViewPreview.hide()
            self.ui.btnSaveRX.hide()
            self.ui.checkBoxCaptureFullRX.hide()

            sniffer = None

        if self.tx_needed:
            self.device_settings_tx_widget = DeviceSettingsWidget(project_manager, is_tx=True,
                                                                  backend_handler=self.backend_handler,
                                                                  continuous_send_mode=True)
            self.device_settings_tx_widget.ui.spinBoxNRepeat.hide()
            self.device_settings_tx_widget.ui.labelNRepeat.hide()

            self.modulation_settings_widget = ModulationSettingsWidget(modulators, signal_tree_model=signal_tree_model,
                                                                       parent=None)

            self.ui.scrollAreaWidgetContentsTX.layout().insertWidget(0, self.device_settings_tx_widget)
            self.ui.scrollAreaWidgetContentsTX.layout().insertWidget(1, self.modulation_settings_widget)
            send_device = self.device_settings_tx_widget.ui.cbDevice.currentText()
            sender = EndlessSender(self.backend_handler, send_device)
        else:
            self.device_settings_tx_widget = self.modulation_settings_widget = None
            self.ui.tabWidgetSimulatorSettings.setTabEnabled(2, False)

            sender = None

        self.simulator = Simulator(self.simulator_config, modulators, expression_parser, project_manager,
                                   sniffer=sniffer, sender=sender)

        if self.device_settings_tx_widget:
            self.device_settings_tx_widget.device = self.simulator.sender.device

        self.update_buttons()
        self.create_connects()

        if self.device_settings_rx_widget:
            self.device_settings_rx_widget.bootstrap(project_manager.simulator_rx_conf)

        if self.device_settings_tx_widget:
            self.device_settings_tx_widget.bootstrap(project_manager.simulator_tx_conf)

        self.ui.textEditTranscript.setFont(util.get_monospace_font())

        if settings.read('default_view', 0, int) == 1:
            self.ui.radioButtonTranscriptHex.setChecked(True)

    def create_connects(self):
        if self.rx_needed:
            self.device_settings_rx_widget.selected_device_changed.connect(self.on_selected_rx_device_changed)
            self.device_settings_rx_widget.device_parameters_changed.connect(self.rx_parameters_changed.emit)

            self.sniff_settings_widget.sniff_parameters_changed.connect(self.sniff_parameters_changed.emit)

            self.ui.btnSaveRX.clicked.connect(self.on_btn_save_rx_clicked)
            self.ui.checkBoxCaptureFullRX.clicked.connect(self.on_checkbox_capture_full_rx_clicked)

            self.ui.btnTestSniffSettings.clicked.connect(self.on_btn_test_sniff_settings_clicked)
            self.ui.btnOpenInAnalysis.clicked.connect(self.on_btn_open_in_analysis_clicked)

        if self.tx_needed:
            self.device_settings_tx_widget.selected_device_changed.connect(self.on_selected_tx_device_changed)
            self.device_settings_tx_widget.device_parameters_changed.connect(self.tx_parameters_changed.emit)

        self.ui.radioButtonTranscriptBit.clicked.connect(self.on_radio_button_transcript_bit_clicked)
        self.ui.radioButtonTranscriptHex.clicked.connect(self.on_radio_button_transcript_hex_clicked)

        self.simulator_scene.selectionChanged.connect(self.update_buttons)
        self.simulator_config.items_updated.connect(self.update_buttons)

        self.ui.btnLogAll.clicked.connect(self.on_btn_log_all_clicked)
        self.ui.btnLogNone.clicked.connect(self.on_btn_log_none_clicked)
        self.ui.btnToggleLog.clicked.connect(self.on_btn_toggle_clicked)

        self.ui.btnStartStop.clicked.connect(self.on_btn_start_stop_clicked)
        self.ui.btnSaveLog.clicked.connect(self.on_btn_save_log_clicked)
        self.ui.btnSaveTranscript.clicked.connect(self.on_btn_save_transcript_clicked)
        self.timer.timeout.connect(self.on_timer_timeout)
        self.simulator.simulation_started.connect(self.on_simulation_started)
        self.simulator.simulation_stopped.connect(self.on_simulation_stopped)

    def update_buttons(self):
        selectable_items = self.simulator_scene.selectable_items()
        all_items_selected = all(item.model_item.logging_active for item in selectable_items)
        any_item_selected = any(item.model_item.logging_active for item in selectable_items)
        self.ui.btnToggleLog.setEnabled(len(self.simulator_scene.selectedItems()))
        self.ui.btnLogAll.setEnabled(not all_items_selected)
        self.ui.btnLogNone.setEnabled(any_item_selected)

    def __get_full_transcript(self) -> list:
        return self.simulator.transcript.get_for_all_participants(all_rounds=True,
                                                                  use_bit=self.ui.radioButtonTranscriptBit.isChecked())

    def update_view(self):
        for device_message in filter(None, map(str.rstrip, self.simulator.device_messages())):
            self.ui.textEditDevices.append(device_message)

        for log_msg in filter(None, map(str.rstrip, self.simulator.read_log_messages())):
            self.ui.textEditSimulation.append(log_msg)

        transcript = self.__get_full_transcript()
        for line in transcript[self.current_transcript_index:]:
            self.ui.textEditTranscript.append(line)

        self.current_transcript_index = len(transcript)
        current_repeat = str(self.simulator.current_repeat + 1) if self.simulator.is_simulating else "-"
        self.ui.lblCurrentRepeatValue.setText(current_repeat)

        current_item = self.simulator.current_item.index() if self.simulator.is_simulating else "-"
        self.ui.lblCurrentItemValue.setText(current_item)

    def update_rx_graphics_view(self):
        if self.scene_manager is None or not self.ui.graphicsViewPreview.isEnabled():
            return

        self.scene_manager.end = self.simulator.sniffer.rcv_device.current_index
        self.scene_manager.init_scene()
        self.scene_manager.show_full_scene()
        self.ui.graphicsViewPreview.update()

    def reset(self):
        self.ui.textEditDevices.clear()
        self.ui.textEditSimulation.clear()
        self.ui.textEditTranscript.clear()
        self.current_transcript_index = 0
        self.ui.lblCurrentRepeatValue.setText("-")
        self.ui.lblCurrentItemValue.setText("-")

    def emit_editing_finished_signals(self):
        if self.device_settings_rx_widget:
            self.device_settings_rx_widget.emit_editing_finished_signals()

        if self.device_settings_tx_widget:
            self.device_settings_tx_widget.emit_editing_finished_signals()

        if self.sniff_settings_widget:
            self.sniff_settings_widget.emit_editing_finished_signals()

    def update_transcript_view(self):
        self.ui.textEditTranscript.setText("\n".join(self.__get_full_transcript()))

    def closeEvent(self, event: QCloseEvent):
        self.timer.stop()
        self.simulator.stop()
        time.sleep(0.1)
        self.simulator.cleanup()

        self.emit_editing_finished_signals()
        if self.device_settings_rx_widget:
            self.device_settings_rx_widget.emit_device_parameters_changed()
        if self.device_settings_tx_widget:
            self.device_settings_tx_widget.emit_device_parameters_changed()
        if self.sniff_settings_widget:
            self.sniff_settings_widget.emit_sniff_parameters_changed()

        super().closeEvent(event)

    @pyqtSlot()
    def on_simulation_started(self):
        for i in range(3):
            self.ui.tabWidgetSimulatorSettings.setTabEnabled(i, False)
        self.ui.checkBoxCaptureFullRX.setDisabled(True)
        self.reset()
        self.timer.start(self.update_interval)
        self.ui.btnStartStop.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.ui.btnStartStop.setText("Stop")

        if not self.rx_needed:
            return

        rx_device = self.simulator.sniffer.rcv_device
        for item in self.scene_manager.scene.items():
            if isinstance(item, QGraphicsTextItem):
                self.scene_manager.scene.removeItem(item)

        if hasattr(rx_device.data, "real"):
            self.ui.graphicsViewPreview.setEnabled(True)
            if self.ui.checkBoxCaptureFullRX.isChecked():
                self.scene_manager.plot_data = rx_device.data.real
            else:
                self.scene_manager.data_array = rx_device.data.real
        else:
            self.ui.graphicsViewPreview.setEnabled(False)
            if self.ui.checkBoxCaptureFullRX.isChecked():
                self.scene_manager.plot_data = np.array([], dtype=rx_device.data_type)
            else:
                self.scene_manager.data_array = np.array([], dtype=rx_device.data_type)
            self.scene_manager.scene.addText("Could not generate RX preview.")

    @pyqtSlot()
    def on_simulation_stopped(self):
        self.ui.tabWidgetSimulatorSettings.setTabEnabled(0, True)
        self.ui.tabWidgetSimulatorSettings.setTabEnabled(1, self.rx_needed)
        self.ui.tabWidgetSimulatorSettings.setTabEnabled(2, self.tx_needed)

        self.timer.stop()
        self.update_view()
        self.ui.btnStartStop.setIcon(QIcon.fromTheme("media-playback-start"))
        self.ui.btnStartStop.setText("Start")
        self.ui.checkBoxCaptureFullRX.setEnabled(True)

    @pyqtSlot()
    def on_btn_log_all_clicked(self):
        self.simulator_scene.log_all_items(True)

    @pyqtSlot()
    def on_btn_log_none_clicked(self):
        self.simulator_scene.log_all_items(False)

    @pyqtSlot()
    def on_btn_toggle_clicked(self):
        self.simulator_scene.log_toggle_selected_items()

    @pyqtSlot()
    def on_btn_save_log_clicked(self):
        file_path = QFileDialog.getSaveFileName(self, "Save log", "", "Log file (*.log)")

        if file_path[0] == "":
            return

        log_string = self.ui.textEditSimulation.toPlainText()

        try:
            with open(str(file_path[0]), "w") as f:
                f.write(log_string)
        except Exception as e:
            QMessageBox.critical(self, "Error saving log", e.args[0])

    @pyqtSlot()
    def on_btn_save_transcript_clicked(self):
        file_path = QFileDialog.getSaveFileName(self, "Save transcript", "", "Text file (*.txt)")

        if file_path[0] == "":
            return

        transcript = self.ui.textEditTranscript.toPlainText()

        try:
            with open(str(file_path[0]), "w") as f:
                f.write(transcript)
        except Exception as e:
            QMessageBox.critical(self, "Error saving transcript", e.args[0])

    @pyqtSlot()
    def on_btn_start_stop_clicked(self):
        if self.simulator.is_simulating:
            self.simulator.stop()
        else:
            if self.rx_needed:
                self.device_settings_rx_widget.emit_editing_finished_signals()
                self.sniff_settings_widget.emit_editing_finished_signals()

                self.simulator.sniffer.rcv_device.current_index = 0
                self.simulator.sniffer.rcv_device.resume_on_full_receive_buffer = not self.ui.checkBoxCaptureFullRX.isChecked()

            if self.tx_needed:
                self.device_settings_tx_widget.emit_editing_finished_signals()

            self.simulator.start()

    @pyqtSlot()
    def on_timer_timeout(self):
        self.update_view()
        self.update_rx_graphics_view()

    @pyqtSlot()
    def on_selected_rx_device_changed(self):
        dev_name = self.device_settings_rx_widget.ui.cbDevice.currentText()
        self.simulator.sniffer.device_name = dev_name
        self.device_settings_rx_widget.device = self.simulator.sniffer.rcv_device
        self.__set_rx_scene()

    @pyqtSlot()
    def on_selected_tx_device_changed(self):
        old_name = self.simulator.sender.device_name
        try:
            dev_name = self.device_settings_tx_widget.ui.cbDevice.currentText()
            self.simulator.sender.device_name = dev_name
            self.device_settings_tx_widget.device = self.simulator.sender.device
        except Exception as e:
            self.device_settings_tx_widget.ui.cbDevice.setCurrentText(old_name)
            Errors.exception(e)

    @pyqtSlot()
    def on_btn_test_sniff_settings_clicked(self):
        def on_dialog_finished():
            self.device_settings_rx_widget.bootstrap(self.project_manager.simulator_rx_conf)
            self.sniff_settings_widget.bootstrap(self.project_manager.device_conf)

        self.device_settings_rx_widget.emit_device_parameters_changed()
        self.sniff_settings_widget.emit_sniff_parameters_changed()

        psd = ProtocolSniffDialog(self.project_manager, signals=self.sniff_settings_widget.signals, parent=self)
        psd.device_settings_widget.bootstrap(self.project_manager.simulator_rx_conf)
        psd.device_settings_widget.device_parameters_changed.connect(self.rx_parameters_changed.emit)
        psd.sniff_settings_widget.sniff_parameters_changed.connect(self.sniff_parameters_changed.emit)
        psd.finished.connect(on_dialog_finished)
        psd.ui.btnAccept.hide()
        psd.show()

    @pyqtSlot()
    def on_radio_button_transcript_hex_clicked(self):
        self.update_transcript_view()

    @pyqtSlot()
    def on_radio_button_transcript_bit_clicked(self):
        self.update_transcript_view()

    def __set_rx_scene(self):
        if not self.rx_needed:
            return

        if self.ui.checkBoxCaptureFullRX.isChecked():
            self.scene_manager = LiveSceneManager(np.array([], dtype=self.simulator.sniffer.rcv_device.data_type),
                                                  parent=self)
            self.ui.graphicsViewPreview.setScene(self.scene_manager.scene)
        else:
            self.scene_manager = SniffSceneManager(np.array([], dtype=self.simulator.sniffer.rcv_device.data_type),
                                                   parent=self)

            self.ui.graphicsViewPreview.setScene(self.scene_manager.scene)

    @pyqtSlot()
    def on_checkbox_capture_full_rx_clicked(self):
        self.simulator.sniffer.rcv_device.resume_on_full_receive_buffer = not self.ui.checkBoxCaptureFullRX.isChecked()
        self.__set_rx_scene()

    @pyqtSlot()
    def on_btn_save_rx_clicked(self):
        rx_device = self.simulator.sniffer.rcv_device
        if isinstance(rx_device.data, np.ndarray) or isinstance(rx_device.data, IQArray):
            data = IQArray(rx_device.data[:rx_device.current_index])
            filename = FileOperator.ask_signal_file_name_and_save("simulation_capture", data,
                                                                  sample_rate=rx_device.sample_rate, parent=self)
            if filename:
                data.tofile(filename)
                self.rx_file_saved.emit(filename)

    @pyqtSlot()
    def on_btn_open_in_analysis_clicked(self):
        text = self.ui.textEditTranscript.toPlainText()
        if len(text) > 0:
            self.open_in_analysis_requested.emit(text)
            self.close()
