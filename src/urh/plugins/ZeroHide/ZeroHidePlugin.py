from PyQt5.QtWidgets import QAction, QUndoStack

from ..Plugin import ProtocolPlugin
from ..ZeroHide.ZeroHideAction import ZeroHideAction


class ZeroHidePlugin(ProtocolPlugin):
    def __init__(self):
        super().__init__(name="ZeroHide")

        self.following_zeros = (
            5
            if "following_zeros" not in self.qsettings.allKeys()
            else self.qsettings.value("following_zeros", type=int)
        )
        self.undo_stack = None
        self.command = None
        self.zero_hide_offsets = dict()

    def create_connects(self):
        self.settings_frame.spinBoxFollowingZeros.setValue(self.following_zeros)
        self.settings_frame.spinBoxFollowingZeros.valueChanged.connect(
            self.set_following_zeros
        )

    def set_following_zeros(self):
        self.following_zeros = self.settings_frame.spinBoxFollowingZeros.value()
        self.qsettings.setValue("following_zeros", self.following_zeros)

    def get_action(
        self, parent, undo_stack: QUndoStack, sel_range, protocol, view: int
    ):
        """
        :type parent: QTableView
        :type undo_stack: QUndoStack
        """
        self.command = ZeroHideAction(
            protocol, self.following_zeros, view, self.zero_hide_offsets
        )
        action = QAction(self.command.text(), parent)
        action.triggered.connect(self.action_triggered)
        self.undo_stack = undo_stack
        return action

    def action_triggered(self):
        self.undo_stack.push(self.command)
