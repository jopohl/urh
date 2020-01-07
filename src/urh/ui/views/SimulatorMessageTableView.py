from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QMenu, QActionGroup

from urh import settings
from urh.models.SimulatorMessageTableModel import SimulatorMessageTableModel
from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.ui.views.TableView import TableView


class SimulatorMessageTableView(TableView):
    open_modulator_dialog_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def _insert_column(self, pos):
        view_type = self.model().proto_view
        index = self.model().protocol.convert_index(pos, from_view=view_type, to_view=0, decoded=False)[0]
        nbits = 1 if view_type == 0 else 4 if view_type == 1 else 8
        for row in self.selected_rows:
            msg = self.model().protocol.messages[row]
            for j in range(nbits):
                msg.insert(index + j, 0)

        self.model().update()
        self.resize_columns()

    @property
    def selected_message(self) -> SimulatorMessage:
        try:
            return self.model().protocol.messages[self.selected_rows[0]]
        except IndexError:
            return None

    def model(self) -> SimulatorMessageTableModel:
        return super().model()

    def create_context_menu(self) -> QMenu:
        menu = super().create_context_menu()

        if self.selection_is_empty:
            return menu

        menu.addSeparator()
        self._add_insert_column_menu(menu)
        menu.addSeparator()

        selected_encoding = self.selected_message.decoder

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

        if settings.read("multiple_modulations", False, bool):
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
        SimulatorItem.simulator_config.items_updated.emit(updated_messages)

    @pyqtSlot()
    def on_modulation_action_triggered(self):
        for row in self.selected_rows:
            self.model().protocol.messages[row].modulator_index = self.sender().data()

    @pyqtSlot()
    def on_open_modulator_dialog_action_triggered(self):
        self.open_modulator_dialog_clicked.emit()

    @pyqtSlot()
    def on_insert_column_left_action_triggered(self):
        self._insert_column(self.selection_range()[2])

    @pyqtSlot()
    def on_insert_column_right_action_triggered(self):
        self._insert_column(self.selection_range()[3])
