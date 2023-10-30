import numpy
from PyQt5.QtCore import QItemSelection, pyqtSlot
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence, QDropEvent, QIcon
from PyQt5.QtWidgets import QHeaderView, QAction, QActionGroup

from urh.models.ProtocolTableModel import ProtocolTableModel
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Participant import Participant
from urh.ui.views.TableView import TableView


class ProtocolTableView(TableView):
    show_interpretation_clicked = pyqtSignal(int, int, int, int)
    selection_changed = pyqtSignal()
    protocol_view_change_clicked = pyqtSignal(int)
    row_visibility_changed = pyqtSignal()
    writeable_changed = pyqtSignal(bool)
    crop_sync_clicked = pyqtSignal()
    revert_sync_cropping_wanted = pyqtSignal()
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

        self.hide_row_action = QAction("Hide selected rows", self)
        self.hide_row_action.setShortcut(QKeySequence("H"))
        self.hide_row_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.hide_row_action.triggered.connect(self.hide_rows)

        self.addAction(self.ref_message_action)
        self.addAction(self.hide_row_action)

        self.zero_hide_offsets = dict()

    def model(self) -> ProtocolTableModel:
        return super().model()

    @property
    def selected_messages(self):
        messages = self.model().protocol.messages
        rows = set(i.row() for i in self.selectionModel().selectedIndexes())
        return [messages[i] for i in rows]

    def selectionChanged(
        self, selection_1: QItemSelection, selection_2: QItemSelection
    ):
        self.selection_changed.emit()
        super().selectionChanged(selection_1, selection_2)

    def dragMoveEvent(self, event):
        event.accept()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if len(event.mimeData().urls()) > 0:
            self.files_dropped.emit(event.mimeData().urls())

    def create_context_menu(self):
        menu = super().create_context_menu()
        row = self.rowAt(self.context_menu_pos.y())
        cols = [
            index.column()
            for index in self.selectionModel().selectedIndexes()
            if index.row() == row
        ]
        cols.sort()

        pos = self.context_menu_pos
        row = self.rowAt(pos.y())
        selected_messages = self.selected_messages
        self.participant_actions = {}

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

        message_type_menu_str = self.tr("Message type")
        if selected_message_type != -1:
            message_type_menu_str += self.tr(" (" + selected_message_type.name + ")")
        message_type_menu = menu.addMenu(message_type_menu_str)
        message_type_menu.setIcon(QIcon(":/icons/icons/message_type.svg"))
        message_type_group = QActionGroup(self)
        self.message_type_actions = {}

        for message_type in self.model().protocol.message_types:
            action = message_type_menu.addAction(message_type.name)
            action.setCheckable(True)
            action.setActionGroup(message_type_group)

            if selected_message_type == message_type:
                action.setChecked(True)

            self.message_type_actions[action] = message_type
            action.triggered.connect(self.on_message_type_action_triggered)

        new_message_type_action = message_type_menu.addAction("Create new")
        new_message_type_action.setIcon(QIcon.fromTheme("list-add"))
        new_message_type_action.triggered.connect(
            self.on_new_message_type_action_triggered
        )

        if (
            self.model().participants
            and self.model().protocol
            and not self.selection_is_empty
        ):
            participant_group = QActionGroup(self)
            participant_menu_str = self.tr("Participant")
            if selected_participant is None:
                participant_menu_str += self.tr(" (None)")
            elif isinstance(selected_participant, Participant):
                # Ensure we have correct type as selected_participant can be -1 if multiple participants are selected
                participant_menu_str += " (" + selected_participant.name + ")"

            participant_menu = menu.addMenu(participant_menu_str)
            none_participant_action = participant_menu.addAction("None")
            none_participant_action.setCheckable(True)
            none_participant_action.setActionGroup(participant_group)
            none_participant_action.triggered.connect(
                self.on_none_participant_action_triggered
            )

            if selected_participant is None:
                none_participant_action.setChecked(True)

            for participant in self.model().participants:
                pa = participant_menu.addAction(
                    participant.name + " (" + participant.shortname + ")"
                )
                pa.setCheckable(True)
                pa.setActionGroup(participant_group)
                if selected_participant == participant:
                    pa.setChecked(True)

                self.participant_actions[pa] = participant
                pa.triggered.connect(self.on_participant_action_triggered)

        menu.addSeparator()

        if not self.selection_is_empty:
            menu.addAction(self.copy_action)

        menu.addAction(self.hide_row_action)
        hidden_rows = self.model().hidden_rows
        if len(hidden_rows) > 0:
            show_row_action = menu.addAction(
                self.tr("Show all rows (reset {0:d} hidden)".format(len(hidden_rows)))
            )
            show_row_action.triggered.connect(self.on_show_row_action_triggered)

        if self.model().refindex != -1:
            menu.addAction(self.ref_message_action)

        if not self.model().is_writeable:
            show_interpretation_action = menu.addAction(
                self.tr("Show selection in Interpretation")
            )
            show_interpretation_action.setIcon(QIcon.fromTheme("zoom-select"))
            show_interpretation_action.triggered.connect(
                self.on_show_in_interpretation_action_triggered
            )

        if self.model().is_writeable:
            writeable_action = menu.addAction(self.tr("Writeable"))
            writeable_action.setCheckable(True)
            writeable_action.setChecked(True)
        else:
            writeable_action = menu.addAction(
                self.tr("Writeable (decouples from signal)")
            )
            writeable_action.setCheckable(True)
            writeable_action.setChecked(False)

        writeable_action.triggered.connect(self.on_writeable_action_triggered)

        menu.addSeparator()
        undo_stack = self.model().undo_stack
        view = self.model().proto_view

        for plugin in self.controller.plugin_manager.protocol_plugins:
            if plugin.enabled:
                act = plugin.get_action(
                    self,
                    undo_stack,
                    self.selection_range(),
                    self.controller.proto_analyzer,
                    view,
                )
                if act is not None:
                    menu.addAction(act)

                if hasattr(plugin, "zero_hide_offsets"):
                    self.zero_hide_offsets = plugin.command.zero_hide_offsets

        return menu

    @pyqtSlot()
    def set_ref_message(self):
        if self.model().refindex == -1:
            return

        if self.context_menu_pos is None:
            max_row = numpy.max([index.row() for index in self.selectedIndexes()])
            self.model().refindex = max_row
        else:
            self.model().refindex = self.rowAt(self.context_menu_pos.y())

    def set_row_visibility_status(self, show: bool, rows=None):
        if rows is None:
            rows = self.selected_rows
        elif isinstance(rows, set) or isinstance(rows, list) or isinstance(rows, range):
            rows = rows
        else:
            rows = [rows]

        refindex = self.model().refindex
        for row in rows:
            if show:
                self.showRow(row)
                self.model().hidden_rows.discard(row)
            else:
                if row == refindex:
                    refindex += 1
                self.hideRow(row)
                self.model().hidden_rows.add(row)

        self.model().refindex = refindex
        self.model().update()
        self.row_visibility_changed.emit()

    def show_rows(self, rows=None):
        self.set_row_visibility_status(show=True, rows=rows)

    @pyqtSlot()
    def hide_rows(self, row=None):
        self.set_row_visibility_status(show=False, rows=row)

    @pyqtSlot()
    def on_bit_action_triggered(self):
        self.protocol_view_change_clicked.emit(0)

    @pyqtSlot()
    def on_hex_action_triggered(self):
        self.protocol_view_change_clicked.emit(1)

    @pyqtSlot()
    def on_ascii_action_triggered(self):
        self.protocol_view_change_clicked.emit(2)

    @pyqtSlot()
    def on_none_participant_action_triggered(self):
        for message in self.selected_messages:
            message.participant = None
        self.participant_changed.emit()

    @pyqtSlot()
    def on_participant_action_triggered(self):
        for message in self.selected_messages:
            message.participant = self.participant_actions[self.sender()]
        self.participant_changed.emit()

    @pyqtSlot()
    def on_message_type_action_triggered(self):
        self.messagetype_selected.emit(
            self.message_type_actions[self.sender()], self.selected_messages
        )

    @pyqtSlot()
    def on_new_message_type_action_triggered(self):
        self.new_messagetype_clicked.emit(self.selected_messages)

    @pyqtSlot()
    def on_show_in_interpretation_action_triggered(self):
        min_row, max_row, start, end = self.selection_range()

        offsets = self.zero_hide_offsets.get(min_row, dict())
        start += sum(offsets[i] for i in offsets if i <= start)
        end += sum(offsets[i] for i in offsets if i <= end)

        self.show_interpretation_clicked.emit(min_row, start, max_row, end - 1)

    @pyqtSlot()
    def on_show_row_action_triggered(self):
        for i in self.model().hidden_rows:
            self.showRow(i)
        self.model().hidden_rows.clear()
        self.model().update()
        self.row_visibility_changed.emit()

    @pyqtSlot()
    def on_writeable_action_triggered(self):
        self.writeable_changed.emit(self.sender().isChecked())
