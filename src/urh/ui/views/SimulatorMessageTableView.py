from PyQt5.QtGui import QContextMenuEvent, QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu, QActionGroup

from urh.ui.views.TableView import TableView

from urh.simulator.SimulatorItem import SimulatorItem

from urh.models.SimulatorMessageTableModel import SimulatorMessageTableModel

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHeaderView

class SimulatorMessageTableView(TableView):
    create_label_clicked = pyqtSignal(int, int, int)
    open_modulator_dialog_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

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

        if not self.selection_is_empty:
            selected_encoding = self.model().protocol.messages[self.selected_rows[0]].decoder

            if not all(self.model().protocol.messages[i].decoder is selected_encoding
                    for i in self.selected_rows):
                selected_encoding = None

            encoding_group = QActionGroup(self)
            encoding_menu = menu.addMenu("Enforce encoding")

            for decoding in self.model().project_manager.decodings:
                ea = encoding_menu.addAction(decoding.name)
                ea.setCheckable(True)
                ea.setActionGroup(encoding_group)

                if selected_encoding == decoding:
                    ea.setChecked(True)

                ea.setData(decoding)
                ea.triggered.connect(self.on_encoding_action_triggered)

            selected_modulation = self.model().protocol.messages[self.selected_rows[0]].modulator_index

            if not all(self.model().protocol.messages[i].modulator_index == selected_modulation
                    for i in self.selected_rows):
                selected_modulation = -1

            modulation_group = QActionGroup(self)
            modulation_menu = menu.addMenu("Modulation")

            for i, modulator in enumerate(self.model().project_manager.modulators):
                ma = modulation_menu.addAction(modulator.name)
                ma.setCheckable(True)
                ma.setActionGroup(modulation_group)

                if selected_modulation == i:
                    ma.setChecked(True)

                ma.setData(i)
                ma.triggered.connect(self.on_modulation_action_triggered)

            open_modulator_dialog_action = modulation_menu.addAction(self.tr("..."))
            open_modulator_dialog_action.triggered.connect(self.on_open_modulator_dialog_action_triggered)

        return menu

    @pyqtSlot()
    def on_encoding_action_triggered(self):
        updated_messages = []
        
        for row in self.selected_rows:
            self.model().protocol.messages[row].decoder = self.sender().data()
            updated_messages.append(self.model().protocol.messages[row])
        SimulatorItem.protocol_manager.items_updated.emit(updated_messages)

    @pyqtSlot()
    def on_modulation_action_triggered(self):
        for row in self.selected_rows:
            self.model().protocol.messages[row].modulator_index = self.sender().data()

    @pyqtSlot()
    def on_open_modulator_dialog_action_triggered(self):
        self.open_modulator_dialog_clicked.emit()

    @pyqtSlot()
    def on_create_label_action_triggered(self):
        min_row, _, start, end = self.selection_range()
        self.create_label_clicked.emit(min_row, start, end)
