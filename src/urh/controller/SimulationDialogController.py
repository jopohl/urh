import time

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCloseEvent, QIcon

from urh.ui.ui_simulation import Ui_SimulationDialog
from urh.util.Simulator import Simulator

class SimulationDialogController(QDialog):
    def __init__(self, sim_proto_manager, modulators, expression_parser, project_manager, parent=None):
        super().__init__(parent)
        self.ui = Ui_SimulationDialog()
        self.ui.setupUi(self)

        self.sim_proto_manager = sim_proto_manager
        self.modulators = modulators
        self.expression_parser = expression_parser
        self.project_manager = project_manager
        self.update_interval = 25

        self.timer = QTimer(self)

        self.simulator = Simulator(self.sim_proto_manager, self.modulators, self.expression_parser, self.project_manager)
        self.create_connects()

    def create_connects(self):
        self.ui.btnStartStop.clicked.connect(self.on_start_stop_clicked)
        self.timer.timeout.connect(self.update_view)
        self.simulator.simulation_started.connect(self.on_simulation_started)
        self.simulator.simulation_stopped.connect(self.on_simulation_stopped)

    def update_view(self):
        txt = self.ui.textEditDevices.toPlainText()
        device_messages = self.simulator.device_messages()

        if len(device_messages) > 1:
            self.ui.textEditDevices.setPlainText(txt + device_messages)

        txt = self.ui.textEditSimulation.toPlainText()
        simulator_messages = self.simulator.read_messages()

        if len(simulator_messages) > 1:
            self.ui.textEditSimulation.setPlainText(txt + simulator_messages)

        self.ui.textEditSimulation.verticalScrollBar().setValue(self.ui.textEditSimulation.verticalScrollBar().maximum())

        current_repeat = str(self.simulator.current_repeat + 1) if self.simulator.is_simulating else "-"
        self.ui.lblCurrentRepeatValue.setText(current_repeat)

        current_item = self.simulator.current_item.index() if self.simulator.is_simulating else "-"
        self.ui.lblCurrentItemValue.setText(current_item)

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