import array
import copy
from collections import OrderedDict

from PyQt5.QtCore import pyqtSlot, QAbstractTableModel, QModelIndex, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QHeaderView, QAbstractItemView, QLineEdit

from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.Message import Message
from urh.ui.delegates.SpinBoxDelegate import SpinBoxDelegate
from urh.ui.ui_checksum_options_widget import Ui_ChecksumOptions
from urh.util import util
from urh.util.GenericCRC import GenericCRC
from urh.util.Logger import logger
from urh.util.WSPChecksum import WSPChecksum


class ChecksumWidget(QWidget):
    SPECIAL_CRCS = OrderedDict(
        [
            ("CC1101", GenericCRC(polynomial="16_standard", start_value=True)),
        ]
    )

    class RangeTableModel(QAbstractTableModel):
        header_labels = ["Start", "End"]

        def __init__(
            self,
            checksum_label: ChecksumLabel,
            message: Message,
            proto_view: int,
            parent=None,
        ):
            """

            :param message:
            :type field_types: list of FieldType
            :param parent:
            """
            super().__init__(parent)
            self.checksum_label = checksum_label
            self.message = message
            self.proto_view = proto_view
            self.update()

        def update(self):
            self.beginResetModel()
            self.endResetModel()

        def columnCount(self, parent: QModelIndex = None, *args, **kwargs):
            return len(self.header_labels)

        def rowCount(self, parent: QModelIndex = None, *args, **kwargs):
            return len(self.checksum_label.data_ranges)

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if role == Qt.DisplayRole and orientation == Qt.Horizontal:
                return self.header_labels[section]
            return super().headerData(section, orientation, role)

        def data(self, index: QModelIndex, role=Qt.DisplayRole):
            if not index.isValid():
                return None

            i, j = index.row(), index.column()

            if role == Qt.DisplayRole:
                data_range = self.checksum_label.data_ranges[i]
                if j == 0:
                    return (
                        self.message.convert_index(
                            data_range[0], 0, self.proto_view, True
                        )[0]
                        + 1
                    )
                elif j == 1:
                    return self.message.convert_index(
                        data_range[1], 0, self.proto_view, True
                    )[0]
            return None

        def setData(self, index: QModelIndex, value, role: int = ...):
            try:
                int_val = int(value)
            except ValueError:
                return False

            i, j = index.row(), index.column()

            if i > len(self.checksum_label.data_ranges):
                return False

            data_range = self.checksum_label.data_ranges[i]

            if j == 0:
                converted_index = self.message.convert_index(
                    int_val - 1, self.proto_view, 0, True
                )[0]
                if converted_index < data_range[1]:
                    data_range[0] = converted_index
            elif j == 1:
                converted_index = self.message.convert_index(
                    int_val, self.proto_view, 0, True
                )[0]
                if converted_index > data_range[0]:
                    data_range[1] = converted_index

            return True

        def flags(self, index):
            if not index.isValid():
                return Qt.NoItemFlags

            try:
                _ = self.checksum_label.data_ranges[index.row()]
            except IndexError:
                return Qt.NoItemFlags

            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def __init__(
        self,
        checksum_label: ChecksumLabel,
        message: Message,
        proto_view: int,
        parent=None,
    ):
        super().__init__(parent)
        self.ui = Ui_ChecksumOptions()
        self.ui.setupUi(self)
        self.checksum_label = checksum_label
        self.data_range_table_model = self.RangeTableModel(
            checksum_label, message, proto_view, parent=self
        )
        self.ui.tableViewDataRanges.setItemDelegateForColumn(
            0, SpinBoxDelegate(1, 999999, self)
        )
        self.ui.tableViewDataRanges.setItemDelegateForColumn(
            1, SpinBoxDelegate(1, 999999, self)
        )
        self.ui.tableViewDataRanges.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.ui.tableViewDataRanges.setModel(self.data_range_table_model)
        self.ui.tableViewDataRanges.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.display_crc_data_ranges_in_table()
        self.ui.comboBoxCRCFunction.addItems(
            [crc_name for crc_name in GenericCRC.DEFAULT_POLYNOMIALS]
        )
        self.ui.comboBoxCRCFunction.addItems(
            [special_crc_name for special_crc_name in self.SPECIAL_CRCS]
        )
        self.ui.lineEditCRCPolynomial.setValidator(
            QRegExpValidator(QRegExp("[0-9,a-f]*"))
        )
        self.ui.comboBoxCategory.clear()
        for _, member in self.checksum_label.Category.__members__.items():
            self.ui.comboBoxCategory.addItem(member.value)
        self.set_ui_for_category()
        self.setFocus()
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
        self.ui.comboBoxCRCFunction.currentIndexChanged.connect(
            self.on_combobox_crc_function_current_index_changed
        )
        self.ui.btnAddRange.clicked.connect(self.on_btn_add_range_clicked)
        self.ui.btnRemoveRange.clicked.connect(self.on_btn_remove_range_clicked)
        self.ui.lineEditCRCPolynomial.editingFinished.connect(
            self.on_line_edit_crc_polynomial_editing_finished
        )
        self.ui.lineEditStartValue.editingFinished.connect(
            self.on_line_edit_start_value_editing_finished
        )
        self.ui.lineEditFinalXOR.editingFinished.connect(
            self.on_line_edit_final_xor_editing_finished
        )
        self.ui.comboBoxCategory.currentIndexChanged.connect(
            self.on_combobox_category_current_index_changed
        )
        self.ui.radioButtonWSPAuto.clicked.connect(
            self.on_radio_button_wsp_auto_clicked
        )
        self.ui.radioButtonWSPChecksum4.clicked.connect(
            self.on_radio_button_wsp_checksum4_clicked
        )
        self.ui.radioButtonWSPChecksum8.clicked.connect(
            self.on_radio_button_wsp_checksum8_clicked
        )
        self.ui.radioButtonWSPCRC8.clicked.connect(
            self.on_radio_button_wsp_crc8_clicked
        )
        self.ui.checkBoxRefIn.clicked.connect(self.on_check_box_ref_in_clicked)
        self.ui.checkBoxRefOut.clicked.connect(self.on_check_box_ref_out_clicked)

    def set_checksum_ui_elements(self):
        if self.checksum_label.is_generic_crc:
            self.ui.lineEditCRCPolynomial.setText(
                self.checksum_label.checksum.polynomial_as_hex_str
            )
            self.ui.lineEditStartValue.setText(
                util.bit2hex(self.checksum_label.checksum.start_value)
            )
            self.ui.lineEditFinalXOR.setText(
                util.bit2hex(self.checksum_label.checksum.final_xor)
            )
            self.ui.checkBoxRefIn.setChecked(self.checksum_label.checksum.lsb_first)
            self.ui.checkBoxRefOut.setChecked(self.checksum_label.checksum.reverse_all)
            self.__set_crc_function_index()
            self.__ensure_same_length()
            self.__set_crc_info_label()
        elif self.checksum_label.category == self.checksum_label.Category.wsp:
            if self.checksum_label.checksum.mode == WSPChecksum.ChecksumMode.auto:
                self.ui.radioButtonWSPAuto.setChecked(True)
            elif (
                self.checksum_label.checksum.mode == WSPChecksum.ChecksumMode.checksum4
            ):
                self.ui.radioButtonWSPChecksum4.setChecked(True)
            elif (
                self.checksum_label.checksum.mode == WSPChecksum.ChecksumMode.checksum8
            ):
                self.ui.radioButtonWSPChecksum8.setChecked(True)
            elif self.checksum_label.checksum.mode == WSPChecksum.ChecksumMode.crc8:
                self.ui.radioButtonWSPCRC8.setChecked(True)

    def set_ui_for_category(self):
        self.ui.comboBoxCategory.setCurrentText(self.checksum_label.category.value)
        if self.checksum_label.category == self.checksum_label.Category.generic:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_crc)
        elif self.checksum_label.category == self.checksum_label.Category.wsp:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_wsp)
        else:
            raise ValueError("Unknown category")

        self.set_checksum_ui_elements()

    def display_crc_data_ranges_in_table(self):
        self.data_range_table_model.update()

    def __set_crc_function_index(self):
        # Get the combobox index
        crc_found = False
        for crc_name in GenericCRC.DEFAULT_POLYNOMIALS:
            test_crc = GenericCRC(crc_name)
            if test_crc == self.checksum_label.checksum:
                self.ui.comboBoxCRCFunction.setCurrentText(crc_name)
                crc_found = True
                break

        if not crc_found:
            for crc_name, crc in self.SPECIAL_CRCS.items():
                if self.checksum_label.checksum == crc:
                    self.ui.comboBoxCRCFunction.setCurrentText(crc_name)
                    crc_found = True
                    break

        if not crc_found:
            self.__add_and_select_custom_item()
        elif "Custom" in [
            self.ui.comboBoxCRCFunction.itemText(i)
            for i in range(self.ui.comboBoxCRCFunction.count())
        ]:
            self.ui.comboBoxCRCFunction.removeItem(
                self.ui.comboBoxCRCFunction.count() - 1
            )

    def __set_crc_info_label(self):
        crc = self.checksum_label.checksum  # type: GenericCRC
        self.ui.label_crc_info.setText(
            "<b>CRC Summary:</b><ul>"
            "<li>Polynomial = {}<>"
            "<li>Length of checksum = {} bit</li>"
            "<li>start value length = {} bit</li>"
            "<li>final XOR length = {} bit</li>"
            "</ul>".format(
                crc.polynomial_to_html,
                crc.poly_order - 1,
                len(crc.start_value),
                len(crc.final_xor),
            )
        )

    def __ensure_same_length(self):
        for dependant_line_edit in [
            self.ui.lineEditStartValue,
            self.ui.lineEditFinalXOR,
        ]:  # type: QLineEdit
            if len(self.ui.lineEditCRCPolynomial.text()) < len(
                dependant_line_edit.text()
            ):
                dependant_line_edit.setText(
                    dependant_line_edit.text()[
                        : len(self.ui.lineEditCRCPolynomial.text())
                    ]
                )
                dependant_line_edit.editingFinished.emit()
            elif len(self.ui.lineEditCRCPolynomial.text()) > len(
                dependant_line_edit.text()
            ):
                # pad zeros at front
                dependant_line_edit.setText(
                    "0"
                    * (
                        len(self.ui.lineEditCRCPolynomial.text())
                        - len(dependant_line_edit.text())
                    )
                    + dependant_line_edit.text()
                )
                dependant_line_edit.editingFinished.emit()

    def __add_and_select_custom_item(self):
        if "Custom" not in [
            self.ui.comboBoxCRCFunction.itemText(i)
            for i in range(self.ui.comboBoxCRCFunction.count())
        ]:
            self.ui.comboBoxCRCFunction.addItem("Custom")
        self.ui.comboBoxCRCFunction.blockSignals(True)
        self.ui.comboBoxCRCFunction.setCurrentText("Custom")
        self.ui.comboBoxCRCFunction.blockSignals(False)

    @pyqtSlot()
    def on_btn_add_range_clicked(self):
        self.checksum_label.data_ranges.append([0, self.checksum_label.start])
        self.data_range_table_model.update()

    @pyqtSlot()
    def on_btn_remove_range_clicked(self):
        if len(self.checksum_label.data_ranges) > 1:
            self.checksum_label.data_ranges.pop(-1)
            self.data_range_table_model.update()

    @pyqtSlot(int)
    def on_combobox_crc_function_current_index_changed(self, index: int):
        poly_str = self.ui.comboBoxCRCFunction.itemText(index)
        if poly_str in GenericCRC.DEFAULT_POLYNOMIALS:
            self.checksum_label.checksum.polynomial = (
                self.checksum_label.checksum.choose_polynomial(poly_str)
            )
            self.checksum_label.checksum.start_value = array.array(
                "B", [0] * (self.checksum_label.checksum.poly_order - 1)
            )
            self.checksum_label.checksum.final_xor = array.array(
                "B", [0] * (self.checksum_label.checksum.poly_order - 1)
            )
        elif poly_str in self.SPECIAL_CRCS:
            self.checksum_label.checksum = copy.deepcopy(self.SPECIAL_CRCS[poly_str])
        else:
            logger.error("Unknown CRC")
            return

        self.ui.lineEditCRCPolynomial.setText(
            self.checksum_label.checksum.polynomial_as_hex_str
        )
        self.ui.lineEditStartValue.setText(
            util.bit2hex(self.checksum_label.checksum.start_value)
        )
        self.ui.lineEditFinalXOR.setText(
            util.bit2hex(self.checksum_label.checksum.final_xor)
        )
        self.ui.lineEditCRCPolynomial.editingFinished.emit()

    @pyqtSlot()
    def on_line_edit_crc_polynomial_editing_finished(self):
        self.checksum_label.checksum.set_polynomial_from_hex(
            self.ui.lineEditCRCPolynomial.text()
        )
        self.__ensure_same_length()
        self.__set_crc_info_label()
        self.__set_crc_function_index()

    @pyqtSlot()
    def on_check_box_ref_in_clicked(self):
        self.checksum_label.checksum.lsb_first = self.ui.checkBoxRefIn.isChecked()

    @pyqtSlot()
    def on_check_box_ref_out_clicked(self):
        self.checksum_label.checksum.reverse_all = self.ui.checkBoxRefOut.isChecked()

    @pyqtSlot()
    def on_line_edit_start_value_editing_finished(self):
        crc = self.checksum_label.checksum
        start_value = util.hex2bit(self.ui.lineEditStartValue.text())
        # pad with zeros at front
        start_value = (
            array.array("B", [0] * (crc.poly_order - 1 - len(start_value)))
            + start_value
        )
        crc.start_value = start_value[0 : crc.poly_order - 1]
        self.ui.lineEditStartValue.setText(util.bit2hex(crc.start_value))
        self.__set_crc_info_label()
        self.__set_crc_function_index()

    @pyqtSlot()
    def on_line_edit_final_xor_editing_finished(self):
        crc = self.checksum_label.checksum
        final_xor = util.hex2bit(self.ui.lineEditFinalXOR.text())
        final_xor = (
            array.array("B", [0] * (crc.poly_order - 1 - len(final_xor))) + final_xor
        )
        crc.final_xor = final_xor[0 : crc.poly_order - 1]
        self.ui.lineEditFinalXOR.setText(util.bit2hex(crc.final_xor))
        self.__set_crc_info_label()
        self.__set_crc_function_index()

    @pyqtSlot(int)
    def on_combobox_category_current_index_changed(self, index: int):
        self.checksum_label.category = self.checksum_label.Category(
            self.ui.comboBoxCategory.currentText()
        )
        self.set_ui_for_category()

    @pyqtSlot()
    def on_radio_button_wsp_auto_clicked(self):
        self.checksum_label.checksum.mode = WSPChecksum.ChecksumMode.auto

    @pyqtSlot()
    def on_radio_button_wsp_checksum4_clicked(self):
        self.checksum_label.checksum.mode = WSPChecksum.ChecksumMode.checksum4

    @pyqtSlot()
    def on_radio_button_wsp_checksum8_clicked(self):
        self.checksum_label.checksum.mode = WSPChecksum.ChecksumMode.checksum8

    @pyqtSlot()
    def on_radio_button_wsp_crc8_clicked(self):
        self.checksum_label.checksum.mode = WSPChecksum.ChecksumMode.crc8
