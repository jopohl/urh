from PyQt5.QtGui import QContextMenuEvent, QIcon
from PyQt5.QtWidgets import QMenu

from urh.ui.views.TableView import TableView

from urh.models.SimulatorMessageTableModel import SimulatorMessageTableModel

from PyQt5.QtCore import pyqtSignal

class SimulatorMessageTableView(TableView):
    create_fuzzing_label_clicked = pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def model(self) -> SimulatorMessageTableModel:
        return super().model()

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.context_menu_pos = event.pos()
        menu = self.create_context_menu()
        menu.exec_(self.mapToGlobal(self.context_menu_pos))
        self.context_menu_pos = None

    def create_context_menu(self) -> QMenu:
        assert self.context_menu_pos is not None
        menu = QMenu()

        create_label_action = menu.addAction(self.tr("Add protocol label"))
        create_label_action.setIcon(QIcon.fromTheme("list-add"))
        create_label_action.setEnabled(not self.selection_is_empty)
        create_label_action.triggered.connect(self.on_create_label_action_triggered)

        return menu

    def on_create_label_action_triggered(self):
        _, _, start, end = self.selection_range()
        self.create_fuzzing_label_clicked.emit(self.rowAt(self.context_menu_pos.y()), start, end)