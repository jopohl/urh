from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

from urh.signalprocessing.Ruleset import Ruleset, Rule


class RulesetTableModel(QAbstractTableModel):
    header_labels = ["Start", "End", "Viewtype", "Operator", "Value"]

    def __init__(self, ruleset: Ruleset, operator_descriptions: list, parent=None):
        self.ruleset = ruleset
        self.operator_descriptions = operator_descriptions
        super().__init__(parent)

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, parent: QModelIndex = None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, parent: QModelIndex = None, *args, **kwargs):
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
            assert isinstance(rule, Rule)

            if j == 0:
                return rule.start + 1
            elif j == 1:
                return rule.end
            elif j == 2:
                return rule.value_type
            elif j == 3:
                return rule.operator_description
            elif j == 4:
                return rule.target_value

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            i, j = index.row(), index.column()
            rule = self.ruleset[i]
            try:
                if j == 0:
                    rule.start = int(value) - 1
                elif j == 1:
                    rule.end = int(value)
                if j == 2:
                    rule.value_type = int(value)
                if j == 3:
                    rule.operator_description = self.operator_descriptions[int(value)]
                if j == 4:
                    rule.target_value = value
            except ValueError:
                return False

            return True

    def flags(self, index: QModelIndex):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
