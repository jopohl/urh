from PyQt5.QtWidgets import QDialog, QGraphicsView, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

from urh.ui.SimulatorScene import SimulatorScene
from urh.ui.ui_simulate_dialog import Ui_SimulateDialog
from urh.ui.delegates.SimulatorSettingsComboBoxDelegate import SimulatorSettingsComboBoxDelegate
from urh.models.SimulatorSettingsTableModel import SimulatorSettingsTableModel
from urh.util.ProjectManager import ProjectManager
from urh.SimulatorProtocolManager import SimulatorProtocolManager
from urh import SimulatorSettings

class SimulateDialogController(QDialog):
    simulator_settings_confirmed = pyqtSignal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.ui = Ui_SimulateDialog()
        self.ui.setupUi(self)

        self.project_manager = controller.project_manager
        self.generator_tab_controller = controller.generator_tab_controller
        self.compare_frame_controller = controller.compare_frame_controller
        self.sim_proto_manager = controller.sim_proto_manager

        self.simulator_scene = SimulatorScene(mode=1, sim_proto_manager=self.sim_proto_manager)
        self.ui.gvSimulator.setScene(self.simulator_scene)

        self.simulator_settings_model = SimulatorSettingsTableModel(self.sim_proto_manager)
        self.ui.tableViewSimulate.setModel(self.simulator_settings_model)

        self.ui.tableViewSimulate.setItemDelegateForColumn(1, SimulatorSettingsComboBoxDelegate(
                                                           controller=self, is_rx=True, parent=self.ui.tableViewSimulate))
        self.ui.tableViewSimulate.setItemDelegateForColumn(2, SimulatorSettingsComboBoxDelegate(
                                                           controller=self, is_rx=False, parent=self.ui.tableViewSimulate))

        self.ui.spinBoxNRepeat.setValue(SimulatorSettings.num_repeat)
        self.ui.spinBoxTimeout.setValue(SimulatorSettings.timeout)
        self.ui.spinBoxRetries.setValue(SimulatorSettings.retries)
        self.ui.comboBoxError.setCurrentIndex(SimulatorSettings.error_handling_index)

        self.update_buttons()

        self.create_connects()

    def create_connects(self):
        self.project_manager.project_updated.connect(self.on_project_updated)
        self.simulator_scene.selectionChanged.connect(self.update_buttons)
        self.sim_proto_manager.items_updated.connect(self.update_buttons)

        self.ui.btnLogAll.clicked.connect(self.on_btn_log_all_clicked)
        self.ui.btnLogNone.clicked.connect(self.on_btn_log_none_clicked)
        self.ui.btnSimulate.clicked.connect(self.on_btn_simulate_clicked)
        self.ui.btnLog.clicked.connect(self.on_btn_log_clicked)

        self.ui.spinBoxNRepeat.valueChanged.connect(self.on_repeat_value_changed)
        self.ui.spinBoxTimeout.valueChanged.connect(self.on_timeout_value_changed)
        self.ui.comboBoxError.currentIndexChanged.connect(self.on_error_handling_index_changed)
        self.ui.spinBoxRetries.valueChanged.connect(self.on_retries_value_changed)

    def on_repeat_value_changed(self, value):
        SimulatorSettings.num_repeat = value
 
    def on_timeout_value_changed(self, value):
        SimulatorSettings.timeout = value

    def on_retries_value_changed(self, value):
        SimulatorSettings.retries = value

    def on_error_handling_index_changed(self, index):
        SimulatorSettings.error_handling_index = index

    def on_project_updated(self):
        self.simulator_settings_model.update()

    def on_btn_log_all_clicked(self):
        self.simulator_scene.log_all_items(True)

    def on_btn_log_none_clicked(self):
        self.simulator_scene.log_all_items(False)

    def on_btn_log_clicked(self):
        self.simulator_scene.log_toggle_selected_items()

    def on_btn_simulate_clicked(self):
        for part in self.sim_proto_manager.active_participants:
            if part.simulate and part.send_profile is None:
                QMessageBox.critical(self, self.tr("Invalid simulation settings"),
                    self.tr("Please set a send profile for participant '" + part.name) + "'.")
                return

            if not part.simulate and part.recv_profile is None:
                QMessageBox.critical(self, self.tr("Invalid simulation settings"),
                    self.tr("Please set a receive profile for participant '" + part.name + "'."))
                return

        self.close()
        self.simulator_settings_confirmed.emit()

    def update_buttons(self):
        selectable_items = self.simulator_scene.selectable_items()
        all_items_selected = all(item.model_item.logging_active for item in selectable_items)
        any_item_selected = any(item.model_item.logging_active for item in selectable_items)
        self.ui.btnLog.setEnabled(len(self.simulator_scene.selectedItems()))
        self.ui.btnLogAll.setEnabled(not all_items_selected)
        self.ui.btnLogNone.setEnabled(any_item_selected)