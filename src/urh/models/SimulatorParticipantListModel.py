from PyQt5.QtCore import Qt, QModelIndex, QAbstractListModel, pyqtSignal

from urh.signalprocessing.Participant import Participant
from urh.simulator.SimulatorConfiguration import SimulatorConfiguration


class SimulatorParticipantListModel(QAbstractListModel):

    participant_simulate_changed = pyqtSignal(Participant)

    def __init__(self, config: SimulatorConfiguration, parent=None):
        super().__init__(parent)
        self.simulator_config = config

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = None, *args, **kwargs):
        return len(self.simulator_config.active_participants)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        i = index.row()
        participant = self.simulator_config.active_participants[i]

        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return participant.name + " (" + participant.shortname + ")"
        elif role == Qt.CheckStateRole:
            return Qt.Checked if participant.simulate else Qt.Unchecked

    def setData(self, index: QModelIndex, value, role=None):
        i = index.row()
        participants = self.simulator_config.active_participants
        if role == Qt.CheckStateRole:
            participants[i].simulate = value
            self.update()
            self.participant_simulate_changed.emit(participants[i])

        return True

    def flags(self, index: QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
