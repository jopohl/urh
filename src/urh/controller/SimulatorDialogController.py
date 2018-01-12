import time
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from urh.models.SimulatorParticipantListModel import SimulatorParticipantListModel
from urh.ui.SimulatorScene import SimulatorScene
from urh.ui.ui_simulator_dialog import Ui_DialogSimulator
from urh.util.ProjectManager import ProjectManager
from urh.util.Simulator import Simulator


class SimulationDialogController(QDialog):
    def __init__(self, simulator_config, modulators,
                 expression_parser, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogSimulator()
        self.ui.setupUi(self)

        self.simulator_config = simulator_config

        self.simulator_scene = SimulatorScene(mode=1,
                                              simulator_config=self.simulator_config)
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.ui.listViewSimulate.setModel(SimulatorParticipantListModel(self.simulator_config))

        self.project_manager = project_manager

        self.ui.spinBoxNRepeat.setValue(self.project_manager.simulator_num_repeat)
        self.ui.spinBoxTimeout.setValue(self.project_manager.simulator_timeout)
        self.ui.spinBoxRetries.setValue(self.project_manager.simulator_retries)
        self.ui.comboBoxError.setCurrentIndex(self.project_manager.simulator_retries)

        self.update_interval = 25

        self.timer = QTimer(self)

        self.simulator = Simulator(self.simulator_config, modulators, expression_parser, project_manager)
        self.create_connects()

        self.update_buttons()
        self.create_connects()

    def create_connects(self):
        self.simulator_scene.selectionChanged.connect(self.update_buttons)
        self.simulator_config.items_updated.connect(self.update_buttons)

        self.ui.btnLogAll.clicked.connect(self.on_btn_log_all_clicked)
        self.ui.btnLogNone.clicked.connect(self.on_btn_log_none_clicked)
        self.ui.btnLog.clicked.connect(self.on_btn_log_clicked)

        self.ui.spinBoxNRepeat.valueChanged.connect(self.on_spinbox_num_repeat_value_changed)
        self.ui.spinBoxTimeout.valueChanged.connect(self.on_spinbox_timeout_value_changed)
        self.ui.comboBoxError.currentIndexChanged.connect(self.on_combobox_error_handling_index_changed)
        self.ui.spinBoxRetries.valueChanged.connect(self.on_retries_value_changed)

        self.ui.btnStartStop.clicked.connect(self.on_start_stop_clicked)
        self.ui.btnSaveLog.clicked.connect(self.on_save_log_clicked)
        self.timer.timeout.connect(self.update_view)
        self.simulator.simulation_started.connect(self.on_simulation_started)
        self.simulator.simulation_stopped.connect(self.on_simulation_stopped)

    def on_spinbox_num_repeat_value_changed(self, value):
        self.project_manager.simulator_num_repeat = value

    def on_spinbox_timeout_value_changed(self, value):
        self.project_manager.simulator_timeout = value

    def on_retries_value_changed(self, value):
        self.project_manager.simulator_retries = value

    def on_combobox_error_handling_index_changed(self, index: int):
        self.project_manager.simulator_error_handling_index = index

    def on_btn_log_all_clicked(self):
        self.simulator_scene.log_all_items(True)

    def on_btn_log_none_clicked(self):
        self.simulator_scene.log_all_items(False)

    def on_btn_log_clicked(self):
        self.simulator_scene.log_toggle_selected_items()

    def update_buttons(self):
        selectable_items = self.simulator_scene.selectable_items()
        all_items_selected = all(item.model_item.logging_active for item in selectable_items)
        any_item_selected = any(item.model_item.logging_active for item in selectable_items)
        self.ui.btnLog.setEnabled(len(self.simulator_scene.selectedItems()))
        self.ui.btnLogAll.setEnabled(not all_items_selected)
        self.ui.btnLogNone.setEnabled(any_item_selected)

    def update_view(self):
        txt = self.ui.textEditDevices.toPlainText()
        device_messages = self.simulator.device_messages()

        if len(device_messages) > 1:
            self.ui.textEditDevices.setPlainText(txt + device_messages)

        txt = self.ui.textEditSimulation.toPlainText()
        simulator_messages = self.simulator.read_messages()

        if len(simulator_messages) > 1:
            self.ui.textEditSimulation.setPlainText(txt + simulator_messages)

        self.ui.textEditSimulation.verticalScrollBar().setValue(
            self.ui.textEditSimulation.verticalScrollBar().maximum())

        current_repeat = str(self.simulator.current_repeat + 1) if self.simulator.is_simulating else "-"
        self.ui.lblCurrentRepeatValue.setText(current_repeat)

        current_item = self.simulator.current_item.index() if self.simulator.is_simulating else "-"
        self.ui.lblCurrentItemValue.setText(current_item)

    def on_save_log_clicked(self):
        file_path = QFileDialog.getSaveFileName(self, "Save log", "", "Log file (*.log)")

        if file_path[0] == "":
            return

        log_string = self.ui.textEditSimulation.toPlainText()

        try:
            with open(str(file_path[0]), "w") as f:
                f.write(log_string)
        except Exception as e:
            QMessageBox.critical(self, "Error saving log", e.args[0])

    def on_start_stop_clicked(self):
        if self.simulator.is_simulating:
            self.simulator.stop()
        else:
            self.simulator.start()

    def on_simulation_started(self):
        self.reset()
        self.timer.start(self.update_interval)
        self.ui.btnStartStop.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.ui.btnStartStop.setText("Stop")

    def on_simulation_stopped(self):
        self.timer.stop()
        self.update_view()
        self.ui.btnStartStop.setIcon(QIcon.fromTheme("media-playback-start"))
        self.ui.btnStartStop.setText("Start")

    def reset(self):
        self.ui.textEditDevices.clear()
        self.ui.textEditSimulation.clear()
        self.ui.lblCurrentRepeatValue.setText("-")
        self.ui.lblCurrentItemValue.setText("-")

    def closeEvent(self, event: QCloseEvent):
        self.timer.stop()
        self.simulator.stop()
        time.sleep(0.1)
        self.simulator.cleanup()

        super().closeEvent(event)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from urh.controller.MainController import MainController
    from urh.signalprocessing.Participant import Participant
    from urh.signalprocessing.SimulatorMessage import SimulatorMessage
    from array import array

    app = QApplication([])
    mc = MainController()
    alice = Participant("Alice", "A")
    bob = Participant("Bob", "B")
    mc.project_manager.participants.append(alice)
    mc.project_manager.participants.append(bob)
    mc.project_manager.project_updated.emit()

    mt = mc.compare_frame_controller.proto_analyzer.default_message_type
    msg1 = SimulatorMessage(destination=alice, plain_bits=array("B", [1, 0, 1, 1]), pause=100, message_type=mt)
    msg2 = SimulatorMessage(destination=bob, plain_bits=array("B", [1, 0, 1, 1]), pause=100, message_type=mt)

    simulator_manager = mc.simulator_tab_controller.simulator_config
    simulator_manager.add_items([msg1, msg2], 0, simulator_manager.rootItem)
    simulator_manager.add_label(5, 15, "test", parent_item=simulator_manager.rootItem.children[0])

    dialog = SimulationDialogController(mc.simulator_tab_controller.simulator_config,
                                        mc.generator_tab_controller.modulators,
                                        mc.simulator_tab_controller.sim_expression_parser,
                                        mc.project_manager)

    dialog.show()
    app.exec_()
