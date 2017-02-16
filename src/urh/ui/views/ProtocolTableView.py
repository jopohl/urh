from PyQt5.QtCore import QItemSelection, pyqtSlot
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QHeaderView, QAction, QMenu, QActionGroup
from PyQt5.QtGui import QKeySequence, QDropEvent, QIcon
import numpy

from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.models.ProtocolTableModel import ProtocolTableModel
from urh.ui.views.TableView import TableView


class ProtocolTableView(TableView):
    show_interpretation_clicked = pyqtSignal(int, int, int, int)
    selection_changed = pyqtSignal()
    protocol_view_change_clicked = pyqtSignal(int)
    row_visibility_changed = pyqtSignal()
    writeable_changed = pyqtSignal(bool)
    crop_sync_clicked = pyqtSignal()
    revert_sync_cropping_wanted = pyqtSignal()
    edit_label_clicked = pyqtSignal(ProtocolLabel)
    files_dropped = pyqtSignal(list)
    participant_changed = pyqtSignal()
    new_messagetype_clicked = pyqtSignal(list)  # list of protocol messages
    messagetype_selected = pyqtSignal(MessageType, list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.ref_message_action = QAction(self.tr("Mark as reference message"), self)
        self.ref_message_action.setShortcut(QKeySequence("R"))
        self.ref_message_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.ref_message_action.triggered.connect(self.set_ref_message)

        self.hide_row_action = QAction("Hide selected Rows", self)
        self.hide_row_action.setShortcut(QKeySequence("H"))
        self.hide_row_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.hide_row_action.triggered.connect(self.hide_row)

        self.addAction(self.ref_message_action)
        self.addAction(self.hide_row_action)

    def model(self) -> ProtocolTableModel:
        return super().model()

    @property
    def selected_messages(self):
        messages = self.model().protocol.messages
        rows = set(i.row() for i in self.selectionModel().selectedIndexes())
        return [messages[i] for i in rows]

    def selectionChanged(self, selection_1: QItemSelection, selection_2: QItemSelection):
        self.selection_changed.emit()
        super().selectionChanged(selection_1, selection_2)

    def dragMoveEvent(self, event):
        event.accept()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if len(event.mimeData().urls()) > 0:
            self.files_dropped.emit(event.mimeData().urls())

    @pyqtSlot()
    def set_ref_message(self, y=None):
        if self.model().refindex == -1:
            return

        if y is None:
            max_row = numpy.max([index.row() for index in self.selectedIndexes()])
            self.model().refindex = max_row
        else:
            self.model().refindex = self.rowAt(y)

    @pyqtSlot()
    def hide_row(self, row=None):
        if row is None:
            rows = [index.row() for index in self.selectionModel().selectedIndexes()]
        else:
            rows = [row]

        refindex = self.model().refindex
        for row in rows:
            if row == refindex:
                refindex += 1
            self.hideRow(row)
            self.model().hidden_rows.add(row)
        if refindex < self.model().row_count:
            self.model().refindex = refindex
        self.model().update()
        self.row_visibility_changed.emit()

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()

        view_group = QActionGroup(self)
        view_menu = menu.addMenu("View")
        bit_action = view_menu.addAction("Bits")
        bit_action.setCheckable(True)
        hex_action = view_menu.addAction("Hex")
        hex_action.setCheckable(True)
        ascii_action = view_menu.addAction("ASCII")
        ascii_action.setCheckable(True)
        bit_action.setActionGroup(view_group)
        hex_action.setActionGroup(view_group)
        ascii_action.setActionGroup(view_group)

        if self.model().proto_view == 0:
            bit_action.setChecked(True)
        elif self.model().proto_view == 1:
            hex_action.setChecked(True)
        elif self.model().proto_view == 2:
            ascii_action.setChecked(True)

        menu.addSeparator()
        row = self.rowAt(event.pos().y())
        cols = [index.column() for index in self.selectionModel().selectedIndexes() if index.row() == row]
        cols.sort()

        pos = event.pos()
        row = self.rowAt(pos.y())
        min_row, max_row, start, end = self.selection_range()
        selected_messages = self.selected_messages
        participant_actions = {}

        if len(selected_messages) == 0:
            selected_participant = -1
            selected_message_type = -1
        else:
            selected_participant = selected_messages[0].participant
            selected_message_type = selected_messages[0].message_type
            for message in selected_messages:
                if selected_participant != message.participant:
                    selected_participant = -1
                if selected_message_type != message.message_type:
                    selected_message_type = -1
                if selected_message_type == -1 and selected_participant == -1:
                    break

        if self.model().participants and self.model().protocol and not self.selection_is_empty:

            participant_group = QActionGroup(self)
            participant_menu = menu.addMenu("Participant")
            none_participant_action = participant_menu.addAction("None")
            none_participant_action.setCheckable(True)
            none_participant_action.setActionGroup(participant_group)

            if selected_participant is None:
                none_participant_action.setChecked(True)

            for participant in self.model().participants:
                pa = participant_menu.addAction(participant.name + " (" + participant.shortname + ")")
                pa.setCheckable(True)
                pa.setActionGroup(participant_group)
                if selected_participant == participant:
                    pa.setChecked(True)

                participant_actions[pa] = participant
        else:
            none_participant_action = 42

        try:
            selected_label = self.controller.get_labels_from_selection(row, row, cols[0], cols[-1])[0]
            edit_label_action = menu.addAction(self.tr("Edit Label ") + selected_label.name)
        except IndexError:
            edit_label_action = 42
            selected_label = None

        menu.addSeparator()

        create_label_action = menu.addAction(self.tr("Add protocol label"))  # type: QAction
        create_label_action.setIcon(QIcon.fromTheme("list-add"))
        create_label_action.setEnabled(not self.selection_is_empty)

        message_type_menu = menu.addMenu(self.tr("Message type"))
        message_type_group = QActionGroup(self)
        message_type_actions = {}
        for message_type in self.model().protocol.message_types:
            action = message_type_menu.addAction(message_type.name)
            action.setCheckable(True)
            action.setActionGroup(message_type_group)

            if selected_message_type == message_type:
                action.setChecked(True)

            message_type_actions[action] = message_type

        new_message_type_action = message_type_menu.addAction("Create new")

        menu.addSeparator()
        if not self.model().is_writeable:
            show_interpretation_action = menu.addAction(self.tr("Show in Interpretation"))
        else:
            show_interpretation_action = 42

        menu.addSeparator()
        menu.addAction(self.hide_row_action)
        hidden_rows = self.model().hidden_rows
        show_row_action = 42
        if len(hidden_rows) > 0:
            show_row_action = menu.addAction(self.tr("Show all rows (reset {0:d} hidden)".format(len(hidden_rows))))

        if self.model().refindex != -1:
            menu.addAction(self.ref_message_action)

        menu.addSeparator()
        if self.model().is_writeable:
            writeable_action = menu.addAction(self.tr("Writeable"))
            writeable_action.setCheckable(True)
            writeable_action.setChecked(True)
        else:
            writeable_action = menu.addAction(self.tr("Writeable (decouples from signal)"))
            writeable_action.setCheckable(True)
            writeable_action.setChecked(False)

        menu.addSeparator()
        undo_stack = self.model().undo_stack
        view = self.model().proto_view

        for plugin in self.controller.plugin_manager.protocol_plugins:
            if plugin.enabled:
                act = plugin.get_action(self, undo_stack, self.selection_range(),
                                        self.controller.proto_analyzer, view)
                if act is not None:
                    menu.addAction(act)

        action = menu.exec_(self.mapToGlobal(pos))
        if action == self.ref_message_action:
            self.set_ref_message(y=pos.y())
        elif action == edit_label_action:
            self.edit_label_clicked.emit(selected_label)
        elif action == create_label_action:
            self.model().addProtoLabel(start, end - 1, row)
        elif action == show_interpretation_action:
            self.show_interpretation_clicked.emit(min_row, start, max_row, end - 1)
        elif action == show_row_action:
            for i in hidden_rows:
                self.showRow(i)
            self.model().hidden_rows.clear()
            self.model().update()
            self.row_visibility_changed.emit()
        elif action == bit_action:
            self.protocol_view_change_clicked.emit(0)
        elif action == hex_action:
            self.protocol_view_change_clicked.emit(1)
        elif action == ascii_action:
            self.protocol_view_change_clicked.emit(2)
        elif action == writeable_action:
            self.writeable_changed.emit(writeable_action.isChecked())
        elif action == none_participant_action:
            for message in selected_messages:
                message.participant = None
            self.participant_changed.emit()
        elif action in participant_actions:
            for message in selected_messages:
                message.participant = participant_actions[action]
            self.participant_changed.emit()
        elif action == new_message_type_action:
            self.new_messagetype_clicked.emit(selected_messages)
        elif action in message_type_actions:
            self.messagetype_selected.emit(message_type_actions[action], selected_messages)
