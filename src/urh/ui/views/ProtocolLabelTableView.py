from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import QTableView, QMenu, QAction, QActionGroup

from urh.models.PLabelTableModel import PLabelTableModel
from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel


class ProtocolLabelTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.delete_action = QAction("Delete selected labels", self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.delete_action.triggered.connect(self.delete_selected_rows)
        self.addAction(self.delete_action)

    @property
    def selected_rows(self) -> list:
        return [i.row() for i in self.selectedIndexes()]

    def model(self) -> PLabelTableModel:
        return super().model()

    def create_context_menu(self):
        menu = QMenu(self)
        if self.model().rowCount() == 0:
            return menu

        if isinstance(self.model(), SimulatorMessageFieldModel):
            value_type_group = QActionGroup(self)
            value_type_menu = menu.addMenu("Set value type")
            labels = [self.model().message_type[i] for i in self.selected_rows
                      if not self.model().message_type[i].is_checksum_label]

            for i, value_type in enumerate(SimulatorProtocolLabel.VALUE_TYPES):
                va = value_type_menu.addAction(value_type)
                va.setCheckable(True)
                va.setActionGroup(value_type_group)
                va.setData(i)

                if all(lbl.value_type_index == i for lbl in labels):
                    va.setChecked(True)

                va.triggered.connect(self.on_set_value_type_action_triggered)

        menu.addAction(self.delete_action)
        return menu

    def contextMenuEvent(self, event):
        self.create_context_menu().exec_(self.mapToGlobal(event.pos()))

    def delete_selected_rows(self):
        for row in sorted(self.selected_rows, reverse=True):
            self.model().remove_label_at(row)

    def on_set_value_type_action_triggered(self):
        assert isinstance(self.model(), SimulatorMessageFieldModel)
        value_type_index = self.sender().data()
        self.model().set_value_type_index(self.selected_rows, value_type_index)

