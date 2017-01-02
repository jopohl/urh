from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, pyqtSignal
from urh.signalprocessing.Participant import Participant

class SimulateListModel(QAbstractListModel):
    simulate_state_changed = pyqtSignal()

    def __init__(self, participants, parent=None):
        """

        :type participants: list of Participant
        """
        super().__init__(parent)
        self.participants = participants

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.participants)

    def data(self, index: QModelIndex, role=None):
        row = index.row()
        if role == Qt.DisplayRole:
            try:
                return self.participants[row].name + " ("+ self.participants[row].shortname + ")"
            except IndexError:
                return None

        elif role == Qt.CheckStateRole:
            try:
                return Qt.Checked if self.participants[row].simulate else Qt.Unchecked
            except IndexError:
                return None

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.CheckStateRole:
            try:
                if self.participants[index.row()].simulate != value:
                    self.participants[index.row()].simulate = value
                    self.simulate_state_changed.emit()
            except IndexError:
                return False

        return True

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable

    def update(self):
        self.layoutChanged.emit()