from PyQt5.QtWidgets import QAction, QUndoStack, QMessageBox


from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from ..Plugin import ProtocolPlugin
from ..MessageBreak.MessageBreakAction import MessageBreakAction


class MessageBreakPlugin(ProtocolPlugin):
    def __init__(self):
        super().__init__(name="MessageBreak")
        self.undo_stack = None
        self.command = None
        """:type: QUndoAction """

    def get_action(
        self,
        parent,
        undo_stack: QUndoStack,
        sel_range,
        protocol: ProtocolAnalyzer,
        view: int,
    ):
        """
        :type parent: QTableView
        :type undo_stack: QUndoStack
        :type protocol_analyzers: list of ProtocolAnalyzer
        """
        min_row, max_row, start, end = sel_range
        if min_row == -1 or max_row == -1 or start == -1 or end == -1:
            return None

        if max_row != min_row:
            return None

        end = protocol.convert_index(end, view, 0, True, message_indx=min_row)[0]
        # factor = 1 if view == 0 else 4 if view == 1 else 8

        self.command = MessageBreakAction(protocol, max_row, end)
        action = QAction(self.command.text(), parent)
        action.triggered.connect(self.action_triggered)
        self.undo_stack = undo_stack
        return action

    def action_triggered(self):
        self.undo_stack.push(self.command)
