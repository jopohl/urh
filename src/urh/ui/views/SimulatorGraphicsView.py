from PyQt5.QtWidgets import QGraphicsView, QAction, QActionGroup, QMenu, QAbstractItemView
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt, pyqtSlot

from urh.ui.SimulatorScene import MessageItem, RuleConditionItem, ParticipantItem, ActionItem, ActionType, SimulatorItem

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
        message_type = [] if not self.sender().data() else self.sender().data()

        ref_item = self.context_menu_item
        position = QAbstractItemView.OnItem if isinstance(ref_item, RuleConditionItem) else QAbstractItemView.BelowItem 
        self.scene().add_message(ref_item, position, message_type=message_type)

    @pyqtSlot()
    def on_add_rule_action_triggered(self):        
        self.scene().add_rule(self.context_menu_item, QAbstractItemView.BelowItem)

    @pyqtSlot()
    def on_add_action_triggered(self):
        ref_item = self.context_menu_item
        position = QAbstractItemView.OnItem if isinstance(ref_item, RuleConditionItem) else QAbstractItemView.BelowItem
        self.scene().add_action(ref_item, position, type=self.sender().data())

    @pyqtSlot()
    def on_delete_action_triggered(self):
        self.scene().delete_selected_items()

    @pyqtSlot()
    def on_select_all_action_triggered(self):
        self.scene().select_all_items()

    @pyqtSlot()
    def on_clear_all_action_triggered(self):
        self.scene().clear_all()

    @pyqtSlot()
    def on_add_else_if_cond_action_triggered(self):
        self.context_menu_item.parentItem().add_else_if_cond()
        self.scene().update_view()

    @pyqtSlot()
    def on_add_else_cond_action_triggered(self):
        self.context_menu_item.parentItem().add_else_cond()
        self.scene().update_view()

    @pyqtSlot()
    def on_source_action_triggered(self):
        self.context_menu_item.source = self.sender().data()
        self.scene().update_view()

    @pyqtSlot()
    def on_destination_action_triggered(self):
        self.context_menu_item.destination = self.sender().data()
        self.scene().update_view()

    @pyqtSlot()
    def on_swap_part_action_triggered(self):
        tmp = self.context_menu_item.source
        self.context_menu_item.source = self.context_menu_item.destination
        self.context_menu_item.destination = tmp
        self.scene().update_view()

    def create_context_menu(self):
        menu = QMenu()

        add_message_action = menu.addAction("Add empty message")
        add_message_action.triggered.connect(self.on_add_message_action_triggered)

        message_type_menu = menu.addMenu("Add message with message type ...")

        for message_type in self.proto_analyzer.message_types:
            action = message_type_menu.addAction(message_type.name)
            action.setData(message_type)
            action.triggered.connect(self.on_add_message_action_triggered)

        add_rule_action = menu.addAction("Add rule")
        add_rule_action.triggered.connect(self.on_add_rule_action_triggered)

        action_menu = menu.addMenu("Add action")
        add_goto_action = action_menu.addAction("Goto")
        add_goto_action.triggered.connect(self.on_add_action_triggered)
        add_goto_action.setData(ActionType.goto)
        add_external_program_action = action_menu.addAction("External program")
        add_external_program_action.setData(ActionType.external_program)
        add_external_program_action.triggered.connect(self.on_add_action_triggered)

        if isinstance(self.context_menu_item, RuleConditionItem):
            menu.addSeparator()

            add_else_if_cond_action = menu.addAction("Add else if block")
            add_else_if_cond_action.triggered.connect(self.on_add_else_if_cond_action_triggered)

            if not self.context_menu_item.parentItem().has_else_condition():
                add_else_cond_action = menu.addAction("Add else block")
                add_else_cond_action.triggered.connect(self.on_add_else_cond_action_triggered)

        if isinstance(self.context_menu_item, MessageItem):
            menu.addSeparator()

            source_group = QActionGroup(self.scene())
            source_menu = menu.addMenu("Source")

            for particpnt in self.scene().participants:
                if self.context_menu_item.destination == particpnt:
                    continue

                if particpnt == self.scene().broadcast_part:
                    continue

                pa = source_menu.addAction(particpnt.text.toPlainText())
                pa.setCheckable(True)
                pa.setActionGroup(source_group)

                if self.context_menu_item.source == particpnt:
                    pa.setChecked(True)

                pa.setData(particpnt)
                pa.triggered.connect(self.on_source_action_triggered)

            destination_group = QActionGroup(self.scene())
            destination_menu = menu.addMenu("Destination")

            for particpnt in self.scene().participants:
                if self.context_menu_item.source == particpnt:
                    continue

                pa = destination_menu.addAction(particpnt.text.toPlainText())
                pa.setCheckable(True)
                pa.setActionGroup(destination_group)

                if self.context_menu_item.destination == particpnt:
                    pa.setChecked(True)

                pa.setData(particpnt)
                pa.triggered.connect(self.on_destination_action_triggered)

            if self.context_menu_item.destination != self.scene().broadcast_part:
                swap_part_action = menu.addAction("Swap source and destination")
                swap_part_action.triggered.connect(self.on_swap_part_action_triggered)

        menu.addSeparator()

        if self.scene().sim_items:
            #menu.addAction(self.select_all_action)
            clear_all_action = menu.addAction("Clear all")
            clear_all_action.triggered.connect(self.on_clear_all_action_triggered)

        return menu

    def contextMenuEvent(self, event):
        items = [item for item in self.items(event.pos()) if isinstance(item, SimulatorItem)]
        self.context_menu_item = None if len(items) == 0 else items[0]

        if self.context_menu_item:
            self.scene().clearSelection()
            self.context_menu_item.setSelected(True)

        menu = self.create_context_menu()
        action = menu.exec_(event.globalPos())