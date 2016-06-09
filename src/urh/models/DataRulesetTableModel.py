from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

from urh.signalprocessing.Ruleset import Ruleset, DataRule


class DataRulesetTableModel(QAbstractTableModel):
    header_labels = ["Start", 'End', "Viewtype", "Operator", 'Value']


    def __init__(self, ruleset: Ruleset, parent=None):
        self.ruleset = ruleset
        super().__init__(parent)

    def update(self):
        self.layoutChanged.emit()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.ruleset)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            rule = self.ruleset[i]
            assert isinstance(rule, DataRule)

            if j == 0:
                return rule.start
            elif j == 1:
                return rule.end
            elif j == 2:
                return rule.value_type
            elif j == 3:
                return rule.operator
            elif j == 4:
                return rule.target_value

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            lbl = self.display_labels[index.row()]
            if index.column() == 1:
                lbl.display_type_index = value

    def flags(self, index: QModelIndex):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


