
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeyEvent, QContextMenuEvent, QTextCursor
from PyQt5.QtWidgets import QTextEdit, QApplication, QMenu, QActionGroup


class TextEditProtocolView(QTextEdit):
    proto_view_changed = pyqtSignal()
    deletion_wanted = pyqtSignal()
    show_proto_clicked = pyqtSignal()
    participant_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cur_view = 0
        self.participants = None
        """:type: list of Participant """

        self.blocks = None
        """:type: list of ProtocolBlock """

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            self.deletion_wanted.emit()
        super().keyPressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        QApplication.processEvents()
        menu = QMenu(self)
        viewgroup = QActionGroup(self)
        viewmenu = menu.addMenu("View")
        bitAction = viewmenu.addAction("Bits")
        bitAction.setCheckable(True)
        hexAction = viewmenu.addAction("Hex")
        hexAction.setCheckable(True)
        asciiAction = viewmenu.addAction("ASCII")
        asciiAction.setCheckable(True)

        menu.addSeparator()

        particpnt_actions = {}
        selected_blocks = []
        cursor = self.textCursor()
        print(self.participants, self.blocks, cursor.selection().isEmpty())
        if self.participants and self.blocks and not cursor.selection().isEmpty():
            selected_blocks = []
            start_block = self.toPlainText()[0:cursor.selectionStart()].count("\n")
            end_block = self.toPlainText()[0:cursor.selectionEnd()].count("\n") + 1
            for i in range(start_block, end_block):
                selected_blocks.append(self.blocks[i])

            if len(selected_blocks) == 1:
                selected_block = selected_blocks[0]
            else:
                selected_block = None

            partigroup = QActionGroup(self)
            participant_menu = menu.addMenu("Participant")
            none_partipnt_action = participant_menu.addAction("None")
            none_partipnt_action.setCheckable(True)
            none_partipnt_action.setActionGroup(partigroup)

            if selected_block and selected_block.participant is None:
                none_partipnt_action.setChecked(True)

            for particpnt in self.participants:
                pa = participant_menu.addAction(particpnt.name + " (" + particpnt.shortname + ")")
                pa.setCheckable(True)
                pa.setActionGroup(partigroup)
                if selected_block and selected_block.participant == particpnt:
                    pa.setChecked(True)

                particpnt_actions[pa] = particpnt
        else:
            none_partipnt_action = 42

        show_proto_action = menu.addAction("Zoom to bits in signal")

        menu.addSeparator()

        linewrapAction = menu.addAction("Linewrap (may take a while for long protocols)")
        linewrapAction.setCheckable(True)

        linewrap = self.lineWrapMode() == QTextEdit.WidgetWidth

        linewrapAction.setChecked(linewrap)

        bitAction.setActionGroup(viewgroup)
        hexAction.setActionGroup(viewgroup)
        asciiAction.setActionGroup(viewgroup)

        if self.cur_view == 0:
            bitAction.setChecked(True)
        elif self.cur_view == 1:
            hexAction.setChecked(True)
        elif self.cur_view == 2:
            asciiAction.setChecked(True)

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action is None:
            return
        elif action == bitAction:
            self.cur_view = 0
            self.proto_view_changed.emit()
        elif action == hexAction:
            self.cur_view = 1
            self.proto_view_changed.emit()
        elif action == asciiAction:
            self.cur_view = 2
            self.proto_view_changed.emit()
        elif action == linewrapAction:
            linewrap = linewrapAction.isChecked()

            if linewrap:
                self.setLineWrapMode(QTextEdit.WidgetWidth)
            else:
                self.setLineWrapMode(QTextEdit.NoWrap)
        elif action == show_proto_action:
            self.show_proto_clicked.emit()
        elif action == none_partipnt_action:
            for block in selected_blocks:
                block.participant = None
            self.participant_changed.emit()

        elif action in particpnt_actions:
            for block in selected_blocks:
                block.participant = particpnt_actions[action]
            self.participant_changed.emit()

    def textCursor(self) -> QTextCursor:
        return super().textCursor()
