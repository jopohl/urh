from PyQt5.QtWidgets import QGraphicsView, QAction, QMenu
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt, pyqtSlot

from urh.ui.SimulatorScene import ParticipantItem

class SimulatorGraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setDragMode(QGraphicsView.RubberBandDrag)
        #self.setContextMenuPolicy(Qt.ActionsContextMenu)

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

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())

        if type(item) is not ParticipantItem and item is not None:
            super().contextMenuEvent(event)
            return

        menu = QMenu()

        addRuleAction = QAction("Add rule")
        addMessageAction = QAction("Add empty message")

        if len(self.scene().selectedItems()) > 0:
            menu.addAction(self.delete_action)

        if len(self.scene().items) > 0:
            menu.addAction(self.select_all_action)

        menu.addAction(addRuleAction)
        menu.addAction(addMessageAction)

        message_type_menu = menu.addMenu("Add message with message type ...")
        message_type_actions = {}

        for message_type in self.proto_analyzer.message_types:
            action = message_type_menu.addAction(message_type.name)
            message_type_actions[action] = message_type

        action = menu.exec_(event.globalPos())

        if action == addRuleAction:
            self.scene().add_rule()
        elif action == addMessageAction:
            self.scene().add_message()
        elif action in message_type_actions:
            self.scene().add_message(message_type=message_type_actions[action])

    @pyqtSlot()
    def on_delete_action_triggered(self):
        self.scene().delete_selected_items()

    @pyqtSlot()
    def on_select_all_action_triggered(self):
        self.scene().select_all_items()