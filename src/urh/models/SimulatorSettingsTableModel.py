from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtGui import QFont
from urh.SimulatorProtocolManager import SimulatorProtocolManager

from urh.dev import config

class SimulatorSettingsTableModel(QAbstractTableModel):
    header_labels = ['Simulate', 'Receive', 'Send']

    def __init__(self, protocol_manager: SimulatorProtocolManager, parent=None):
        super().__init__(parent)
        self.protocol_manager = protocol_manager

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.protocol_manager.active_participants)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        i = index.row()
        j = index.column()
        participant = self.protocol_manager.active_participants[i]

        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            if j == 0:
                return participant.name + " ("+ participant.shortname + ")"
            elif j == 1:
                if not participant.simulate:
                    profile = participant.recv_profile
                    return profile['name'] if profile is not None else "Not configured"
                else:
                    return ""
            elif j == 2:
                if participant.simulate:
                    profile = participant.send_profile
                    return profile['name'] if profile is not None else "Not configured"
                else:
                    return ""
        elif role == Qt.CheckStateRole:
            if j == 0:
                return Qt.Checked if participant.simulate else Qt.Unchecked
        elif role == Qt.EditRole:
            if j == 1:
                return participant.recv_profile
            elif j == 2:
                return participant.send_profile
        elif role == Qt.FontRole:
            font = QFont()

            if ((j == 1 and not participant.simulate and participant.recv_profile is None) or
                 j == 2 and participant.simulate and participant.send_profile is None):
                font.setItalic(True)

            return font

    def setData(self, index: QModelIndex, value, role=None):
        i = index.row()
        j = index.column()
        participants = self.protocol_manager.active_participants

        if role == Qt.EditRole:
            if j == 1:
                participants[i].recv_profile = value
            elif j == 2:
                participants[i].send_profile = value
        elif role == Qt.CheckStateRole:
            if j == 0:
                participants[i].simulate = value
                self.update()

        return True

    def flags(self, index: QModelIndex):
        row, col = index.row(), index.column()
        flags = super().flags(index)

        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable
        elif index.column() == 1:
            flags = Qt.ItemIsSelectable

            if not self.protocol_manager.active_participants[row].simulate:
                flags |= Qt.ItemIsEnabled | Qt.ItemIsEditable
        elif index.column() == 2:
            flags = Qt.ItemIsSelectable

            if self.protocol_manager.active_participants[row].simulate:
                flags |= Qt.ItemIsEnabled | Qt.ItemIsEditable

        return flags