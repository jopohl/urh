from collections import OrderedDict

from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QContextMenuEvent, QKeySequence
from PyQt5.QtWidgets import QTableView, QMenu, QAction

from urh import constants
from urh.models.LabelValueTableModel import LabelValueTableModel
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.SectionComboBoxDelegate import SectionComboBoxDelegate


class LabelValueTableView(QTableView):
    edit_label_action_triggered = pyqtSignal()
    configure_field_types_action_triggered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegateForColumn(1, ComboBoxDelegate([""] * len(constants.LABEL_COLORS),
                                                          colors=constants.LABEL_COLORS,
                                                          parent=self))
        self.setItemDelegateForColumn(2, ComboBoxDelegate(ProtocolLabel.DISPLAY_FORMATS, parent=self))

        orders = OrderedDict([("Big Endian (BE)", [bo + "/BE" for bo in ProtocolLabel.DISPLAY_BIT_ORDERS]),
                              ("Little Endian (LE)", [bo + "/LE" for bo in ProtocolLabel.DISPLAY_BIT_ORDERS])])

        self.setItemDelegateForColumn(3, SectionComboBoxDelegate(orders, parent=self))

        self.del_rows_action = QAction("Delete selected labels", self)
        self.del_rows_action.setShortcut(QKeySequence.Delete)
        self.del_rows_action.setIcon(QIcon.fromTheme("edit-delete"))
        self.del_rows_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.del_rows_action.triggered.connect(self.delete_rows)

        self.addAction(self.del_rows_action)

    @property
    def selected_min_max_row(self):
        selected = self.selectionModel().selection()
        if selected.isEmpty():
            return -1, -1
        min_row = min(rng.top() for rng in selected)
        max_row = max(rng.bottom() for rng in selected)
        return min_row, max_row

    def create_context_menu(self):
        menu = QMenu()
        min_row, max_row = self.selected_min_max_row
        if self.model().rowCount() > 0 and min_row > -1:
            edit_label_action = menu.addAction(self.tr("Edit..."))
            edit_label_action.setIcon(QIcon.fromTheme("configure"))
            edit_label_action.triggered.connect(self.on_edit_label_action_triggered)

            if len(self.model().controller.proto_analyzer.message_types) > 1:
                msg_type_menu = menu.addMenu("Copy to message type")
                for i, message_type in enumerate(self.model().controller.proto_analyzer.message_types):
                    if message_type != self.model().controller.active_message_type:
                        msg_type_action = msg_type_menu.addAction(message_type.name)
                        msg_type_action.setData(i)
                        msg_type_action.triggered.connect(self.on_copy_to_msg_type_action_triggered)

            menu.addAction(self.del_rows_action)
        menu.addSeparator()
        configure_field_types_action = menu.addAction("Configure field types...")
        configure_field_types_action.triggered.connect(self.configure_field_types_action_triggered.emit)

        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = self.create_context_menu()
        menu.exec_(self.mapToGlobal(event.pos()))

    def model(self) -> LabelValueTableModel:
        return super().model()

    def delete_rows(self):
        min_row, max_row = self.selected_min_max_row
        if min_row > -1:
            self.model().delete_labels_at(min_row, max_row)

    @pyqtSlot()
    def on_edit_label_action_triggered(self):
        self.edit_label_action_triggered.emit()

    @pyqtSlot()
    def on_copy_to_msg_type_action_triggered(self):
        min_row, max_row = self.selected_min_max_row
        self.model().add_labels_to_message_type(min_row, max_row, int(self.sender().data()))
