from PyQt5.QtWidgets import QDialog, QGraphicsView
from PyQt5.QtCore import Qt

from urh.ui.SimulatorScene import SimulatorScene
from urh.ui.ui_simulate_dialog import Ui_SimulateDialog
from urh.ui.delegates.SimulatorSettingsComboBoxDelegate import SimulatorSettingsComboBoxDelegate
from urh.models.SimulatorSettingsTableModel import SimulatorSettingsTableModel
from urh.util.ProjectManager import ProjectManager
from urh.SimulatorProtocolManager import SimulatorProtocolManager

class SimulateDialogController(QDialog):
    def __init__(self, project_manager: ProjectManager, compare_frame_controller, sim_proto_manager: SimulatorProtocolManager, parent=None):
        super().__init__(parent)
        self.ui = Ui_SimulateDialog()
        self.ui.setupUi(self)

        self.project_manager = project_manager
        self.compare_frame_controller = compare_frame_controller
        self.sim_proto_manager = sim_proto_manager

        self.simulator_scene = SimulatorScene(mode=1, sim_proto_manager=self.sim_proto_manager)
        self.ui.gvSimulator.setScene(self.simulator_scene)

        self.simulator_settings_model = SimulatorSettingsTableModel(self.project_manager)
        self.ui.tableViewSimulate.setModel(self.simulator_settings_model)

        self.ui.tableViewSimulate.setItemDelegateForColumn(1, SimulatorSettingsComboBoxDelegate(
                                                           controller=self, parent=self.ui.tableViewSimulate))
        self.ui.tableViewSimulate.setItemDelegateForColumn(2, SimulatorSettingsComboBoxDelegate(
                                                           controller=self, parent=self.ui.tableViewSimulate))
        self.update_buttons()

        self.create_connects()

    def create_connects(self):
        self.project_manager.project_updated.connect(self.on_project_updated)
        self.simulator_scene.selectionChanged.connect(self.update_buttons)
        self.sim_proto_manager.items_updated.connect(self.update_buttons)

        self.ui.btnLogAll.clicked.connect(self.on_btn_log_all_clicked)
        self.ui.btnLogNone.clicked.connect(self.on_btn_log_none_clicked)
        self.ui.btnLog.clicked.connect(self.on_btn_log_clicked)

    def on_project_updated(self):
        self.simulator_settings_model.update()

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