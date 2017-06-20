from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from urh.util.ProjectManager import ProjectManager

from urh.dev import config

class SimulatorSettingsTableModel(QAbstractTableModel):
    header_labels = ['Simulate', 'Receive', 'Send']

    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.project_manager.participants)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        i = index.row()
        j = index.column()
        participants = self.project_manager.participants

        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            if j == 0:
                return participants[i].name + " ("+ participants[i].shortname + ")"
            elif j == 1:
                profile = participants[i].recv_profile
                return profile['name'] if profile is not None else "Not configured"
            elif j == 2:
                profile = participants[i].send_profile
                return profile['name'] if profile is not None else "Not configured"
        elif role == Qt.CheckStateRole:
            if j == 0:
                return Qt.Checked if participants[i].simulate else Qt.Unchecked
        elif role == Qt.EditRole:
            if j == 1:
                return participants[i].recv_profile
            elif j == 2:
                return participants[i].send_profile

    def setData(self, index: QModelIndex, value, role=None):
        i = index.row()
        j = index.column()
        participants = self.project_manager.participants

        if role == Qt.EditRole:
            if j == 1:
                participants[i].recv_profile = value
            elif j == 2:
                participants[i].send_profile = value
        elif role == Qt.CheckStateRole:
            if j == 0:
                participants[i].simulate = value

        return True

    def flags(self, index: QModelIndex):
        row, col = index.row(), index.column()
        flags = super().flags(index)

        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable
        else:
            flags = Qt.ItemIsSelectable

            if self.project_manager.participants[row].simulate:
                flags |= Qt.ItemIsEnabled | Qt.ItemIsEditable

        return flags