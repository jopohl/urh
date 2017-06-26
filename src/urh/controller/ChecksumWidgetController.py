import array

from PyQt5.QtCore import pyqtSlot, QAbstractTableModel, QModelIndex, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QHeaderView, QAbstractItemView

from urh.signalprocessing.CRCLabel import CRCLabel
from urh.signalprocessing.Message import Message
from urh.ui.delegates.SpinBoxDelegate import SpinBoxDelegate
from urh.ui.ui_checksum_options_widget import Ui_ChecksumOptions
from urh.util import util
from urh.util.GenericCRC import GenericCRC


class ChecksumWidgetController(QWidget):
    class RangeTableModel(QAbstractTableModel):
        header_labels = ["Start", "End"]

        def __init__(self, crc_label: CRCLabel, message: Message, proto_view: int, parent=None):
            """

            :param message:
            :type field_types: list of FieldType
            :param parent:
            """
            super().__init__(parent)
            self.crc_label = crc_label
            self.message = message
            self.proto_view = proto_view
            self.update()

        def update(self):
            self.beginResetModel()
            self.endResetModel()

        def columnCount(self, parent: QModelIndex = None, *args, **kwargs):
            return len(self.header_labels)

        def rowCount(self, parent: QModelIndex = None, *args, **kwargs):
            return len(self.crc_label.data_ranges)

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if role == Qt.DisplayRole and orientation == Qt.Horizontal:
                return self.header_labels[section]
            return super().headerData(section, orientation, role)

        def data(self, index: QModelIndex, role=Qt.DisplayRole):
            if not index.isValid():
                return None

            i, j = index.row(), index.column()

            if role == Qt.DisplayRole:
                data_range = self.crc_label.data_ranges[i]
                if j == 0:
                    return self.message.convert_index(data_range[0], 0, self.proto_view, True)[0] + 1
                elif j == 1:
                    return self.message.convert_index(data_range[1], 0, self.proto_view, True)[0]
            return None

        def setData(self, index: QModelIndex, value, role: int = ...):
            try:
                int_val = int(value)
            except ValueError:
                return False

            i, j = index.row(), index.column()

            if i > len(self.crc_label.data_ranges):
                return False

            data_range = self.crc_label.data_ranges[i]

            if j == 0:
                converted_index = self.message.convert_index(int_val - 1, self.proto_view, 0, True)[0]
                if converted_index < data_range[1]:
                    data_range[0] = converted_index
            elif j == 1:
                converted_index = self.message.convert_index(int_val, self.proto_view, 0, True)[0]
                if converted_index > data_range[0]:
                    data_range[1] = converted_index

            return True

        def flags(self, index):
            if not index.isValid():
                return Qt.NoItemFlags

            try:
                _ = self.crc_label.data_ranges[index.row()]
            except IndexError:
                return Qt.NoItemFlags

            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def __init__(self, crc_label: CRCLabel, message: Message, proto_view: int, parent=None):
        super().__init__(parent)
        self.ui = Ui_ChecksumOptions()
        self.ui.setupUi(self)
        self.crc_label = crc_label
        self.data_range_table_model = self.RangeTableModel(crc_label, message, proto_view, parent=self)
        self.ui.tableViewDataRanges.setItemDelegateForColumn(0, SpinBoxDelegate(1, 999999, self))
        self.ui.tableViewDataRanges.setItemDelegateForColumn(1, SpinBoxDelegate(1, 999999, self))
        self.ui.tableViewDataRanges.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableViewDataRanges.setModel(self.data_range_table_model)
        self.ui.tableViewDataRanges.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.display_crc_data_ranges_in_table()
        self.ui.comboBoxCRCFunction.clear()
        self.ui.comboBoxCRCFunction.addItems([crc_name for crc_name in GenericCRC.DEFAULT_POLYNOMIALS])
        self.ui.lineEditCRCPolynomial.setValidator(QRegExpValidator(QRegExp("[0-9,a-f]*")))
        self.ui.lineEditCRCPolynomial.setText(util.bit2hex(self.crc_label.crc.polynomial))
        self.create_connects()

    @property
    def proto_view(self):
        return self.data_range_table_model.proto_view

    @proto_view.setter
    def proto_view(self, value):
        if value != self.data_range_table_model.proto_view:
            self.data_range_table_model.proto_view = value
            self.data_range_table_model.update()

    def create_connects(self):
        self.ui.comboBoxCRCFunction.currentIndexChanged.connect(self.on_combobox_crc_function_current_index_changed)
        self.ui.btnAddRange.clicked.connect(self.on_btn_add_range_clicked)
        self.ui.btnRemoveRange.clicked.connect(self.on_btn_remove_range_clicked)
        self.ui.lineEditCRCPolynomial.editingFinished.connect(self.on_line_edit_crc_polynomial_editing_finished)

    def display_crc_data_ranges_in_table(self):
        self.data_range_table_model.update()

    @pyqtSlot()
    def on_btn_add_range_clicked(self):
        self.crc_label.data_ranges.append([0, self.crc_label.start])
        self.data_range_table_model.update()

    @pyqtSlot()
    def on_btn_remove_range_clicked(self):
        if len(self.crc_label.data_ranges) > 1:
            self.crc_label.data_ranges.pop(-1)
            self.data_range_table_model.update()

    @pyqtSlot(int)
    def on_combobox_crc_function_current_index_changed(self, index: int):
        self.crc_label.crc.polynomial = self.crc_label.crc.choose_polynomial(self.ui.comboBoxCRCFunction.currentText())
        self.ui.lineEditCRCPolynomial.setText(util.bit2hex(self.crc_label.crc.polynomial))

    @pyqtSlot()
    def on_line_edit_crc_polynomial_editing_finished(self):
        self.crc_label.crc.polynomial = util.hex2bit(self.ui.lineEditCRCPolynomial.text())
