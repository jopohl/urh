from PyQt5.QtWidgets import QGraphicsView, QAction, QMenu
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt, pyqtSlot

from urh.ui.SimulatorScene import ParticipantItem, ActionType

class SimulatorGraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.proto_analyzer = None

        self.delete_action = QAction(self.tr("Delete selected items"), self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.triggered.connect(self.on_delete_action_triggered)
        self.delete_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.delete_action.setIcon(QIcon.fromTheme("edit-delete"))
        self.addAction(self.delete_action)

        self.select_all_action = QAction(self.tr("Select all"), self)
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.triggered.connect(self.on_select_all_action_triggered)
        self.delete_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.select_all_action)

    @pyqtSlot()
    def on_add_message_action_triggered(self):
        if self.sender() in self.message_type_actions:
            message_type = self.message_type_actions[self.sender()]
        else:
            message_type = []

        self.scene().add_message(None, len(self.scene().sim_items), message_type=message_type)

    @pyqtSlot()
    def on_add_rule_action_triggered(self):
        self.scene().add_rule()

    @pyqtSlot()
    def on_add_goto_action_triggered(self):
        self.scene().add_action(ActionType.goto)

    @pyqtSlot()
    def on_add_external_program_action_triggered(self):
        self.scene().add_action(ActionType.external_program)

    @pyqtSlot()
    def on_delete_action_triggered(self):
        self.scene().delete_selected_items()

    @pyqtSlot()
    def on_select_all_action_triggered(self):
        self.scene().select_all_items()

    @pyqtSlot()
    def on_clear_all_action_triggered(self):
        self.scene().clear_all()

    def create_context_menu(self):
        menu = QMenu()

        add_message_action = menu.addAction("Add empty message")
        add_message_action.triggered.connect(self.on_add_message_action_triggered)

        message_type_menu = menu.addMenu("Add message with message type ...")
        self.message_type_actions = {}

        for message_type in self.proto_analyzer.message_types:
            action = message_type_menu.addAction(message_type.name)
            action.triggered.connect(self.on_add_message_action_triggered)
            self.message_type_actions[action] = message_type

        add_rule_action = menu.addAction("Add rule")
        add_rule_action.triggered.connect(self.on_add_rule_action_triggered)

        action_menu = menu.addMenu("Add action")
        add_goto_action = action_menu.addAction("Goto")
        add_goto_action.triggered.connect(self.on_add_goto_action_triggered)
        add_external_program_action = action_menu.addAction("External program")
        add_external_program_action.triggered.connect(self.on_add_external_program_action_triggered)

        menu.addSeparator()

        if len(self.scene().selectedItems()) > 0:
            menu.addAction(self.delete_action)

        if len(self.scene().sim_items) > 0:
            menu.addAction(self.select_all_action)
            clear_all_action = menu.addAction("Clear all")
            clear_all_action.triggered.connect(self.on_clear_all_action_triggered)

        return menu

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())

        if type(item) is not ParticipantItem and item is not None:
            super().contextMenuEvent(event)
            return

        menu = self.create_context_menu()
        action = menu.exec_(event.globalPos())