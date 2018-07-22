import copy

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import QGraphicsView, QAction, QActionGroup, QMenu, QAbstractItemView, QInputDialog

from urh.signalprocessing.MessageType import MessageType
from urh.simulator.GraphicsItem import GraphicsItem
from urh.simulator.MessageItem import MessageItem
from urh.simulator.RuleItem import RuleConditionItem
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.simulator.SimulatorRule import ConditionType
from urh.ui.SimulatorScene import SimulatorScene


class SimulatorGraphicsView(QGraphicsView):
    message_updated = pyqtSignal(SimulatorMessage)
    consolidate_messages_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.proto_analyzer = None
        self.context_menu_item = None
        self.copied_items = []

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

        self.copy_action = QAction(self.tr("Copy selected items"), self)  # type: QAction
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.on_copy_action_triggered)
        self.copy_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.copy_action.setIcon(QIcon.fromTheme("edit-copy"))
        self.addAction(self.copy_action)

        self.paste_action = QAction(self.tr("Paste"), self)  # type: QAction
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.triggered.connect(self.on_paste_action_triggered)
        self.paste_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.paste_action.setIcon(QIcon.fromTheme("edit-paste"))
        self.addAction(self.paste_action)

    def scene(self) -> SimulatorScene:
        return super().scene()

    @pyqtSlot()
    def on_add_message_action_triggered(self):
        num_bits, ok = QInputDialog.getInt(self,
                                           self.tr("How many bits shall the new message have?"),
                                           self.tr("Number of bits:"), 42, 1)

        if ok:
            self.add_empty_message(num_bits)

    def add_empty_message(self, num_bits):
        if hasattr(self.sender(), "data") and self.sender().data():
            message_type = self.sender().data()
        else:
            message_type = MessageType("default")
        ref_item = self.context_menu_item
        if isinstance(ref_item, RuleConditionItem):
            position = QAbstractItemView.OnItem
        else:
            position = QAbstractItemView.BelowItem

        message = self.scene().add_message(plain_bits=[0] * num_bits,
                                           pause=0,
                                           message_type=message_type,
                                           ref_item=ref_item,
                                           position=position)
        self.jump_to_item(message)

    @pyqtSlot()
    def on_add_rule_action_triggered(self):
        rule = self.scene().add_rule(self.context_menu_item, QAbstractItemView.BelowItem)
        if_cond = rule.children[0]
        self.jump_to_item(if_cond)

    @pyqtSlot()
    def on_add_goto_action_triggered(self):
        ref_item = self.context_menu_item
        position = QAbstractItemView.OnItem if isinstance(ref_item, RuleConditionItem) else QAbstractItemView.BelowItem
        ga = self.scene().add_goto_action(ref_item, position)
        self.jump_to_item(ga)

    @pyqtSlot()
    def on_add_sleep_action_triggered(self):
        ref_item = self.context_menu_item
        position = QAbstractItemView.OnItem if isinstance(ref_item, RuleConditionItem) else QAbstractItemView.BelowItem
        sa = self.scene().add_sleep_action(ref_item, position)
        self.jump_to_item(sa)

    @pyqtSlot()
    def on_add_counter_action_triggered(self):
        ref_item = self.context_menu_item
        position = QAbstractItemView.OnItem if isinstance(ref_item, RuleConditionItem) else QAbstractItemView.BelowItem
        ca = self.scene().add_counter_action(ref_item, position)
        self.jump_to_item(ca)

    @pyqtSlot()
    def on_trigger_command_action_triggered(self):
        ref_item = self.context_menu_item
        position = QAbstractItemView.OnItem if isinstance(ref_item, RuleConditionItem) else QAbstractItemView.BelowItem
        pa = self.scene().add_trigger_command_action(ref_item, position)
        self.jump_to_item(pa)

    @pyqtSlot()
    def on_add_else_if_cond_action_triggered(self):
        rule = self.context_menu_item.parentItem().model_item
        cond = self.scene().add_rule_condition(rule, ConditionType.ELSE_IF)
        self.jump_to_item(cond)

    @pyqtSlot()
    def on_add_else_cond_action_triggered(self):
        rule = self.context_menu_item.parentItem().model_item
        cond = self.scene().add_rule_condition(rule, ConditionType.ELSE)
        self.jump_to_item(cond)

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
    def on_set_value_type_action_triggered(self):
        value_type_index = self.sender().data()
        for msg in self.scene().get_selected_messages():
            for lbl in msg.message_type:
                if not lbl.is_checksum_label:
                    lbl.value_type_index = value_type_index
            self.message_updated.emit(msg)

    @pyqtSlot()
    def on_source_action_triggered(self):
        for msg in self.scene().get_selected_messages():
            if msg.destination != self.sender().data():
                msg.source = self.sender().data()
                self.message_updated.emit(msg)

    @pyqtSlot()
    def on_destination_action_triggered(self):
        for msg in self.scene().get_selected_messages():
            if msg.source != self.sender().data():
                msg.destination = self.sender().data()
                self.message_updated.emit(msg)

    @pyqtSlot()
    def on_swap_part_action_triggered(self):
        for msg in self.scene().get_selected_messages():
            if msg.destination != self.scene().simulator_config.broadcast_part:
                msg.participant, msg.destination = msg.destination, msg.participant
                self.message_updated.emit(msg)

    @pyqtSlot()
    def on_consolidate_messages_action_triggered(self):
        self.consolidate_messages_clicked.emit()

    def on_select_from_action_triggered(self):
        self.scene().select_messages_with_participant(self.sender().data())

    def on_select_to_action_triggered(self):
        self.scene().select_messages_with_participant(self.sender().data(), from_part=False)

    def create_context_menu(self):
        menu = QMenu()

        add_message_action = menu.addAction("Add empty message...")
        add_message_action.triggered.connect(self.on_add_message_action_triggered)

        message_type_menu = menu.addMenu("Add message with type...")

        for message_type in self.proto_analyzer.message_types:
            action = message_type_menu.addAction(message_type.name)
            action.setData(message_type)
            action.triggered.connect(self.on_add_message_action_triggered)

        add_rule_action = menu.addAction("Add rule")
        add_rule_action.triggered.connect(self.on_add_rule_action_triggered)

        action_menu = menu.addMenu("Add action")
        add_goto_action = action_menu.addAction("Goto")
        add_goto_action.triggered.connect(self.on_add_goto_action_triggered)
        add_sleep_action = action_menu.addAction("Sleep")
        add_sleep_action.triggered.connect(self.on_add_sleep_action_triggered)
        add_counter_action = action_menu.addAction("Counter")
        add_counter_action.triggered.connect(self.on_add_counter_action_triggered)
        trigger_command_action = action_menu.addAction("Trigger command")
        trigger_command_action.triggered.connect(self.on_trigger_command_action_triggered)

        if isinstance(self.context_menu_item, RuleConditionItem):
            menu.addSeparator()

            add_else_if_cond_action = menu.addAction("Add else if block")
            add_else_if_cond_action.triggered.connect(self.on_add_else_if_cond_action_triggered)

            if not self.context_menu_item.parentItem().has_else_condition:
                add_else_cond_action = menu.addAction("Add else block")
                add_else_cond_action.triggered.connect(self.on_add_else_cond_action_triggered)

        menu.addSeparator()
        menu.addAction(self.copy_action)
        self.copy_action.setEnabled(len(self.scene().selectedItems()) > 0)
        menu.addAction(self.paste_action)
        self.paste_action.setEnabled(len(self.copied_items) > 0)

        if isinstance(self.context_menu_item, MessageItem):
            menu.addSeparator()

            value_type_group = QActionGroup(self.scene())
            value_type_menu = menu.addMenu("Set value type")
            messages = self.scene().get_selected_messages()

            for i, value_type in enumerate(SimulatorProtocolLabel.VALUE_TYPES):
                va = value_type_menu.addAction(value_type)
                va.setCheckable(True)
                va.setActionGroup(value_type_group)
                va.setData(i)

                if all(lbl.value_type_index == i for msg in messages for lbl in msg.message_type
                       if not lbl.is_checksum_label):
                    va.setChecked(True)

                va.triggered.connect(self.on_set_value_type_action_triggered)

            source_group = QActionGroup(self.scene())
            source_menu = menu.addMenu("Source")

            for participant_item in self.scene().participant_items:
                if self.context_menu_item.destination == participant_item:
                    continue

                if participant_item == self.scene().broadcast_part:
                    continue

                pa = source_menu.addAction(participant_item.text.toPlainText())
                pa.setCheckable(True)
                pa.setActionGroup(source_group)

                if self.context_menu_item.source == participant_item:
                    pa.setChecked(True)

                pa.setData(participant_item.model_item)
                pa.triggered.connect(self.on_source_action_triggered)

            destination_group = QActionGroup(self.scene())
            destination_menu = menu.addMenu("Destination")

            for participant_item in self.scene().participant_items:
                if self.context_menu_item.source == participant_item:
                    continue

                pa = destination_menu.addAction(participant_item.text.toPlainText())
                pa.setCheckable(True)
                pa.setActionGroup(destination_group)

                if self.context_menu_item.destination == participant_item:
                    pa.setChecked(True)

                pa.setData(participant_item.model_item)
                pa.triggered.connect(self.on_destination_action_triggered)

            if self.context_menu_item.destination != self.scene().broadcast_part:
                swap_part_action = menu.addAction("Swap source and destination")
                swap_part_action.triggered.connect(self.on_swap_part_action_triggered)
                swap_part_action.setIcon(QIcon.fromTheme("object-flip-horizontal"))

            pause_action = menu.addAction("Set subsequent pause ({} samples)".format(self.context_menu_item.model_item.pause))
            pause_action.triggered.connect(self.on_pause_action_triggered)

        menu.addSeparator()

        if len(self.scene().get_all_message_items()) > 1:
            consolidate_messages_action = menu.addAction("Consolidate messages")
            consolidate_messages_action.triggered.connect(self.on_consolidate_messages_action_triggered)

        if len([item for item in self.scene().items() if isinstance(item, GraphicsItem)]):
            # menu.addAction(self.select_all_action)
            clear_all_action = menu.addAction("Clear all")
            clear_all_action.triggered.connect(self.on_clear_all_action_triggered)
            clear_all_action.setIcon(QIcon.fromTheme("edit-clear"))

        self.add_select_actions_to_menu(menu, self.scene(),
                                        select_to_trigger=self.on_select_to_action_triggered,
                                        select_from_trigger=self.on_select_from_action_triggered)

        return menu

    def navigate_forward(self):
        selected_items = self.scene().selectedItems()

        if selected_items:
            selected_item = selected_items[0]
            next_item = selected_item.next()
            self.jump_to_scene_item(next_item)

    def navigate_backward(self):
        selected_items = self.scene().selectedItems()

        if selected_items:
            selected_item = selected_items[0]
            prev_item = selected_item.prev()
            self.jump_to_scene_item(prev_item)

    def jump_to_item(self, item):
        self.jump_to_scene_item(self.scene().model_to_scene(item))

    def jump_to_scene_item(self, item):
        if item:
            self.scene().clearSelection()
            self.centerOn(item)
            item.setSelected(True)

    def contextMenuEvent(self, event):
        items = [item for item in self.items(event.pos()) if isinstance(item, GraphicsItem) and item.is_selectable()]
        self.context_menu_item = None if len(items) == 0 else items[0]
        menu = self.create_context_menu()
        menu.exec_(event.globalPos())
        self.copy_action.setEnabled(True)
        self.paste_action.setEnabled(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.navigate_backward()
        elif event.key() == Qt.Key_Down:
            self.navigate_forward()
        else:
            super().keyPressEvent(event)

    @pyqtSlot()
    def on_pause_action_triggered(self):
        p = self.context_menu_item.model_item.pause if isinstance(self.context_menu_item, MessageItem) else 0
        pause, ok = QInputDialog.getInt(self, self.tr("Enter new pause"),
                                        self.tr("Pause in samples:"), p, 0)
        if ok:
            for msg in self.scene().get_selected_messages():
                msg.pause = pause

    @classmethod
    def add_select_actions_to_menu(cls, menu, scene: SimulatorScene, select_to_trigger, select_from_trigger):
        if len(scene.visible_participants) == 0:
            return

        menu.addSeparator()

        select_from_menu = menu.addMenu("Select all messages from")

        for vp in scene.visible_participants_without_broadcast:
            vpa = select_from_menu.addAction(vp.text.toPlainText())
            vpa.setData(vp)
            vpa.triggered.connect(select_from_trigger)

        select_to_menu = menu.addMenu("Select all messages to")

        for vp in scene.visible_participants:
            vpa = select_to_menu.addAction(vp.text.toPlainText())
            vpa.setData(vp)
            vpa.triggered.connect(select_to_trigger)

    @pyqtSlot()
    def on_copy_action_triggered(self):
        self.copied_items = self.scene().selectedItems()

    @pyqtSlot()
    def on_paste_action_triggered(self):
        for item in self.copied_items:
            assert isinstance(item, GraphicsItem)
            parent = item.model_item.parent()
            pos = parent.child_count() if parent is not None else 0
            self.scene().simulator_config.add_items([copy.deepcopy(item.model_item)], pos, parent)

