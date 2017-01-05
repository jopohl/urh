from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QContextMenuEvent

from PyQt5.QtWidgets import QHeaderView, QMenu, QActionGroup

from urh.models.SimulatorTableModel import SimulatorTableModel
from urh.ui.views.TableView import TableView

class SimulatorTableView(TableView):
    participant_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def model(self) -> SimulatorTableModel:
        return super().model()

    @property
    def selected_messages(self):
        messages = self.model().protocol.messages
        rows = set(i.row() for i in self.selectionModel().selectedIndexes())
        return [messages[i] for i in rows]

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()
        pos = event.pos()

        selected_messages = self.selected_messages
        particpnt_actions = {}
        target_actions = {}

        if len(selected_messages) == 0:
            selected_participant = -1
            selected_target = -1
        else:
            selected_participant = selected_messages[0].participant
            selected_target = selected_messages[0].target

        if self.model().participants and self.model().protocol and not self.selectionModel().selection().isEmpty():

            partigroup = QActionGroup(self)
            participant_menu = menu.addMenu("Participant")
            none_partipnt_action = participant_menu.addAction("None")
            none_partipnt_action.setCheckable(True)
            none_partipnt_action.setActionGroup(partigroup)

            if selected_participant is None:
                none_partipnt_action.setChecked(True)

            for particpnt in self.model().participants:
                pa = participant_menu.addAction(particpnt.name + " (" + particpnt.shortname + ")")
                pa.setCheckable(True)
                pa.setActionGroup(partigroup)
                if selected_participant == particpnt:
                    pa.setChecked(True)

                particpnt_actions[pa] = particpnt

            targetgroup = QActionGroup(self)
            target_menu = menu.addMenu("Target")
            none_target_action = target_menu.addAction("None")
            none_target_action.setCheckable(True)
            none_target_action.setActionGroup(targetgroup)

            if selected_target is None:
                none_target_action.setChecked(True)

            for target in self.model().participants:
                ta = target_menu.addAction(target.name + " (" + target.shortname + ")")
                ta.setCheckable(True)
                ta.setActionGroup(targetgroup)
                if selected_target == target:
                    ta.setChecked(True)

                target_actions[ta] = target
        else:
            none_partipnt_action = 42
            none_target_action = 42

        action = menu.exec_(self.mapToGlobal(pos))
        if action == none_partipnt_action:
            for message in selected_messages:
                message.participant = None
            self.participant_changed.emit()
        elif action in particpnt_actions:
            for message in selected_messages:
                message.participant = particpnt_actions[action]
            self.participant_changed.emit()
        elif action == none_target_action:
            for message in selected_messages:
                message.target = None
            self.participant_changed.emit()
        elif action in target_actions:
            for message in selected_messages:
                message.target = target_actions[action]
            self.participant_changed.emit()