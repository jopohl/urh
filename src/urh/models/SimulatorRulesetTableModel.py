from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

class SimulatorRulesetTableModel(QAbstractTableModel):
    header_labels = ["Variable", "Viewtype", "Operator", "Value"]

    def __init__(self, operator_descriptions: list, controller, ruleset=[], parent=None):
        super().__init__(parent)
        self.ruleset = ruleset
        self.controller = controller # type: SimulatorTabController
        self.operator_descriptions = operator_descriptions

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, parent: QModelIndex=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, parent: QModelIndex=None, *args, **kwargs):
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

            if j == 0:
                return rule.variable
            elif j == 1:
                return rule.VIEW_TYPES[rule.value_type]
            elif j == 2:
                return rule.operator_description
            elif j == 3:
                return rule.target_value

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            i, j = index.row(), index.column()
            rule = self.ruleset[i]

            try:
                if j == 0:
                    if value in self.controller.sim_formula_parser.label_list:
                        rule.variable = value
                    else:
                        return False
                elif j == 1:
                        rule.value_type = value
                elif j == 2:
                    rule.operator_description = self.operator_descriptions[int(value)]
                elif j == 3:
                    rule.target_value = value
            except ValueError:
                return False

            return True

    def flags(self, index: QModelIndex):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable