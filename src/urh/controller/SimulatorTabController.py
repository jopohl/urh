from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, Qt

from urh.models.SimulateListModel import SimulateListModel
from urh.models.GeneratorTreeModel import GeneratorTreeModel
from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.ui.SimulatorScene import SimulatorScene, MessageItem
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.SimulateDialogController import SimulateDialogController

class SimulatorTabController(QWidget):
    def __init__(self, compare_frame_controller: CompareFrameController,
                 project_manager: ProjectManager, parent):

        super().__init__(parent)

        self.project_manager = project_manager
        self.compare_frame_controller = compare_frame_controller
        self.proto_analyzer = compare_frame_controller.proto_analyzer

        self.ui = Ui_SimulatorTab()
        self.ui.setupUi(self)

        self.ui.splitter_2.setSizes([self.width() / 0.7, self.width() / 0.3])

        #self.simulate_list_model = SimulateListModel(self.project_manager.participants)
        #self.ui.listViewSimulate.setModel(self.simulate_list_model)

        self.ui.treeProtocols.setHeaderHidden(True)
        self.tree_model = GeneratorTreeModel(compare_frame_controller)
        self.tree_model.set_root_item(compare_frame_controller.proto_tree_model.rootItem)
        self.tree_model.controller = self
        self.ui.treeProtocols.setModel(self.tree_model)

        self.simulator_scene = SimulatorScene(controller=self)
        self.simulator_scene.tree_root_item = compare_frame_controller.proto_tree_model.rootItem
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.ui.gvSimulator.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.ui.gvSimulator.proto_analyzer = compare_frame_controller.proto_analyzer

        self.simulator_message_field_model = SimulatorMessageFieldModel()
        self.ui.tblViewFieldValues.setModel(self.simulator_message_field_model)

        self.create_connects(compare_frame_controller)

    def create_connects(self, compare_frame_controller):
        self.project_manager.project_updated.connect(self.on_project_updated)
        compare_frame_controller.proto_tree_model.modelReset.connect(self.refresh_tree)

        self.simulator_scene.selectionChanged.connect(self.on_simulator_scene_selection_changed)

        self.ui.btnStartSim.clicked.connect(self.on_show_simulate_dialog_action_triggered)

        self.ui.btnNextNav.clicked.connect(self.on_btn_next_nav_clicked)
        self.ui.btnPrevNav.clicked.connect(self.on_btn_prev_nav_clicked)

    @pyqtSlot()
    def on_btn_next_nav_clicked(self):
        selected_items = self.simulator_scene.selectedItems()

        if len(selected_items) > 0:
            selected_item = selected_items[0]
            next_item = selected_item.next()
            self.simulator_scene.clearSelection()
            self.ui.gvSimulator.centerOn(next_item)
            next_item.setSelected(True)

    @pyqtSlot()
    def on_btn_prev_nav_clicked(self):
        selected_items = self.simulator_scene.selectedItems()

        if len(selected_items) > 0:
            selected_item = selected_items[0]
            prev_item = selected_item.prev()
            self.simulator_scene.clearSelection()
            self.ui.gvSimulator.centerOn(prev_item)
            prev_item.setSelected(True)

    @pyqtSlot()
    def on_simulator_scene_selection_changed(self):
        selected_items = self.simulator_scene.selectedItems()
        selected_messages = [item for item in selected_items if type(item) == MessageItem]

        first_message = None if len(selected_messages) == 0 else selected_messages[0]
        self.simulator_message_field_model.message = first_message
        self.simulator_message_field_model.update()

        if first_message:
            self.ui.lblMsgFieldsValues.setText(self.tr("Message fields for messsage #") + first_message.index)
        else:
            self.ui.lblMsgFieldsValues.setText(self.tr("Message fields for messsage "))

        if len(selected_items) > 0:
            self.ui.navLineEdit.setText(selected_items[0].index)

            self.ui.btnNextNav.setEnabled(not selected_items[0].is_last_item())
            self.ui.btnPrevNav.setEnabled(not selected_items[0].is_first_item())
        else:
            self.ui.navLineEdit.clear()

    @pyqtSlot()
    def on_show_simulate_dialog_action_triggered(self):
        s = SimulateDialogController(parent=self)
        s.show()
        
    def on_project_updated(self):
        #self.simulate_list_model.participants = self.project_manager.participants
        #self.simulate_list_model.update()

        self.simulator_scene.update_view()

    @pyqtSlot()
    def refresh_tree(self):
        self.tree_model.beginResetModel()
        self.tree_model.endResetModel()
        self.ui.treeProtocols.expandAll()

    def close_all(self):
        self.tree_model.rootItem.clearChilds()
        self.tree_model.rootItem.addGroup()
        self.refresh_tree()