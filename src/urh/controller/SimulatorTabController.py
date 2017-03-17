import re

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, Qt

from urh.models.SimulateListModel import SimulateListModel
from urh.models.GeneratorTreeModel import GeneratorTreeModel
from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.ui.SimulatorScene import SimulatorScene, GotoAction, MessageItem, RuleConditionItem, RuleItem, ConditionType
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

        self.selected_item = None

        self.create_connects(compare_frame_controller)

    def create_connects(self, compare_frame_controller):
        self.project_manager.project_updated.connect(self.on_project_updated)
        compare_frame_controller.proto_tree_model.modelReset.connect(self.refresh_tree)

        self.simulator_scene.selectionChanged.connect(self.on_simulator_scene_selection_changed)
        self.simulator_scene.items_changed.connect(self.update_ui)

        self.ui.btnStartSim.clicked.connect(self.on_show_simulate_dialog_action_triggered)

        self.ui.btnNextNav.clicked.connect(self.on_btn_next_nav_clicked)
        self.ui.btnPrevNav.clicked.connect(self.on_btn_prev_nav_clicked)
        self.ui.navLineEdit.returnPressed.connect(self.on_nav_line_edit_return_pressed)
        self.ui.goto_combobox.activated.connect(self.on_goto_combobox_activated)

    def update_goto_combobox(self):
        item = self.simulator_scene.get_first_item()
        goto_combobox = self.ui.goto_combobox
        goto_combobox.clear()

        while item:
            if item != self.selected_item and not (isinstance(item, RuleConditionItem)
            and (item.type == ConditionType.ELSE or item.type == ConditionType.ELSE_IF)):
                goto_combobox.addItem(item.index, item)

            item = item.next()

        if self.selected_item.goto_target:
            goto_combobox.setCurrentText(self.selected_item.goto_target.index)

    def update_ui(self):
        selected_items = self.simulator_scene.selectedItems()
        self.selected_item = None

        if selected_items:
            self.selected_item = selected_items[0]
                
            self.ui.navLineEdit.setText(self.selected_item.index)

            self.ui.btnNextNav.setEnabled(not self.selected_item.is_last_item())
            self.ui.btnPrevNav.setEnabled(not self.selected_item.is_first_item())

            self.ui.lblMsgFieldsValues.setText(self.tr("Detail view for item #") + self.selected_item.index)

            if isinstance(self.selected_item, GotoAction):
                self.update_goto_combobox()
                self.ui.detail_view_widget.setCurrentIndex(1)
            elif isinstance(self.selected_item, MessageItem):
                self.simulator_message_field_model.message = self.selected_item
                self.simulator_message_field_model.update()
                self.ui.detail_view_widget.setCurrentIndex(2)
            else:
                self.ui.detail_view_widget.setCurrentIndex(0)
        else:
            self.ui.navLineEdit.clear()
            self.ui.btnNextNav.setEnabled(False)
            self.ui.btnPrevNav.setEnabled(False)

            self.ui.lblMsgFieldsValues.setText(self.tr("Detail view for item"))
            self.ui.detail_view_widget.setCurrentIndex(0)

    @pyqtSlot()
    def on_goto_combobox_activated(self):
        if self.ui.goto_combobox.currentData():
            self.selected_item.goto_target = self.ui.goto_combobox.currentData()

    @pyqtSlot()
    def on_btn_next_nav_clicked(self):
        self.ui.gvSimulator.navigate_forward()

    @pyqtSlot()
    def on_btn_prev_nav_clicked(self):
        self.ui.gvSimulator.navigate_backward()

    @pyqtSlot()
    def on_simulator_scene_selection_changed(self):
        self.update_ui()

    @pyqtSlot()
    def on_show_simulate_dialog_action_triggered(self):
        s = SimulateDialogController(parent=self)
        s.show()

    @pyqtSlot()
    def on_nav_line_edit_return_pressed(self):
        items = self.simulator_scene.sim_items
        nav_text = self.ui.navLineEdit.text()
        target_item = None

        if re.match(r"^\d+(\.\d+){0,2}$", nav_text):
            index_list = nav_text.split(".")
            index_list = list(map(int, index_list))

            for index in index_list:
                if not items or index > len(items):
                    break

                target_item = items[index - 1]

                if isinstance(target_item, RuleItem):
                    items = target_item.conditions
                    target_item =  target_item.conditions[0]
                elif isinstance(target_item, RuleConditionItem):
                    items = target_item.sim_items
                else:
                    items = None

        if target_item:
            self.ui.gvSimulator.jump_to_item(target_item)
        else:
            self.update_ui()
                    
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