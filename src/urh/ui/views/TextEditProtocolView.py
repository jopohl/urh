from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QKeyEvent, QContextMenuEvent, QTextCursor
from PyQt5.QtWidgets import QTextEdit, QMenu, QActionGroup


class TextEditProtocolView(QTextEdit):
    proto_view_changed = pyqtSignal()
    deletion_wanted = pyqtSignal()
    show_proto_clicked = pyqtSignal()
    participant_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cur_view = 0
        self.participants = None  # type: list[Participant]
        self.messages = None  # type: list[Message]

    @property
    def selected_text(self):
        return self.textCursor().selectedText().replace("\u2028", "\n")

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            self.deletion_wanted.emit()
            event.ignore()
        else:
            super().keyPressEvent(event)

    @pyqtSlot()
    def on_bit_action_triggered(self):
        self.cur_view = 0
        self.proto_view_changed.emit()

    @pyqtSlot()
    def on_hex_action_triggered(self):
        self.cur_view = 1
        self.proto_view_changed.emit()

    @pyqtSlot()
    def on_ascii_action_triggered(self):
        self.cur_view = 2
        self.proto_view_changed.emit()

    @pyqtSlot()
    def on_none_participant_action_triggered(self):
        for msg in self.selected_messages:
            msg.participant = None
        self.participant_changed.emit()

    @pyqtSlot()
    def on_participant_action_triggered(self):
        for msg in self.selected_messages:
            msg.participant = self.participant_actions[self.sender()]
        self.participant_changed.emit()

    @pyqtSlot()
    def on_zoom_to_bits_action_triggered(self):
        self.show_proto_clicked.emit()

    @pyqtSlot()
    def on_line_wrap_action_triggered(self):
        line_wrap = self.sender().isChecked()

        if line_wrap:
            self.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.setLineWrapMode(QTextEdit.NoWrap)

    def create_context_menu(self) -> QMenu:
        menu = QMenu(self)
        view_group = QActionGroup(self)
        view_menu = menu.addMenu("View")
        bit_action = view_menu.addAction("Bits")
        bit_action.setCheckable(True)
        bit_action.setActionGroup(view_group)
        bit_action.triggered.connect(self.on_bit_action_triggered)

        hex_action = view_menu.addAction("Hex")
        hex_action.setCheckable(True)
        hex_action.setActionGroup(view_group)
        hex_action.triggered.connect(self.on_hex_action_triggered)

        ascii_action = view_menu.addAction("ASCII")
        ascii_action.setCheckable(True)
        ascii_action.setActionGroup(view_group)
        ascii_action.triggered.connect(self.on_ascii_action_triggered)

        if self.cur_view == 0:
            bit_action.setChecked(True)
        elif self.cur_view == 1:
            hex_action.setChecked(True)
        elif self.cur_view == 2:
            ascii_action.setChecked(True)

        menu.addSeparator()

        self.participant_actions = {}
        cursor = self.textCursor()
        if self.participants and self.messages and not cursor.selection().isEmpty():
            self.selected_messages = []
            start_msg = self.toPlainText()[0 : cursor.selectionStart()].count("\n")
            end_msg = self.toPlainText()[0 : cursor.selectionEnd()].count("\n") + 1
            for i in range(start_msg, end_msg):
                self.selected_messages.append(self.messages[i])

            if len(self.selected_messages) == 1:
                selected_msg = self.selected_messages[0]
            else:
                selected_msg = None

            participant_group = QActionGroup(self)
            participant_menu = menu.addMenu("Participant")
            none_participant_action = participant_menu.addAction("None")
            none_participant_action.setCheckable(True)
            none_participant_action.setActionGroup(participant_group)
            none_participant_action.triggered.connect(
                self.on_none_participant_action_triggered
            )

            if selected_msg and selected_msg.participant is None:
                none_participant_action.setChecked(True)

            for participant in self.participants:
                pa = participant_menu.addAction(
                    participant.name + " (" + participant.shortname + ")"
                )
                pa.setCheckable(True)
                pa.setActionGroup(participant_group)
                if selected_msg and selected_msg.participant == participant:
                    pa.setChecked(True)

                self.participant_actions[pa] = participant
                pa.triggered.connect(self.on_participant_action_triggered)

        zoom_to_bits_action = menu.addAction("Zoom to bits in signal")
        zoom_to_bits_action.triggered.connect(self.on_zoom_to_bits_action_triggered)
        zoom_to_bits_action.setIcon(QIcon.fromTheme("zoom-in"))

        menu.addSeparator()

        line_wrap_action = menu.addAction(
            "Linewrap (may take a while for long protocols)"
        )
        line_wrap_action.setCheckable(True)
        line_wrap = self.lineWrapMode() == QTextEdit.WidgetWidth
        line_wrap_action.setChecked(line_wrap)
        line_wrap_action.triggered.connect(self.on_line_wrap_action_triggered)

        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = self.create_context_menu()
        menu.exec_(self.mapToGlobal(event.pos()))

    def textCursor(self) -> QTextCursor:
        return super().textCursor()
