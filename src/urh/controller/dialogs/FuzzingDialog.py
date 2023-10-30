import math

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QInputDialog

from urh import settings
from urh.models.FuzzingTableModel import FuzzingTableModel
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.ui.ui_fuzzing import Ui_FuzzingDialog


class FuzzingDialog(QDialog):
    def __init__(
        self,
        protocol: ProtocolAnalyzerContainer,
        label_index: int,
        msg_index: int,
        proto_view: int,
        parent=None,
    ):
        super().__init__(parent)
        self.ui = Ui_FuzzingDialog()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window)

        self.protocol = protocol
        msg_index = msg_index if msg_index != -1 else 0
        self.ui.spinBoxFuzzMessage.setValue(msg_index + 1)
        self.ui.spinBoxFuzzMessage.setMinimum(1)
        self.ui.spinBoxFuzzMessage.setMaximum(self.protocol.num_messages)

        self.ui.comboBoxFuzzingLabel.addItems(
            [l.name for l in self.message.message_type]
        )
        self.ui.comboBoxFuzzingLabel.setCurrentIndex(label_index)

        self.proto_view = proto_view
        self.fuzz_table_model = FuzzingTableModel(self.current_label, proto_view)
        self.fuzz_table_model.remove_duplicates = (
            self.ui.chkBRemoveDuplicates.isChecked()
        )
        self.ui.tblFuzzingValues.setModel(self.fuzz_table_model)
        self.fuzz_table_model.update()

        self.ui.spinBoxFuzzingStart.setValue(self.current_label_start + 1)
        self.ui.spinBoxFuzzingEnd.setValue(self.current_label_end)
        self.ui.spinBoxFuzzingStart.setMaximum(len(self.message_data))
        self.ui.spinBoxFuzzingEnd.setMaximum(len(self.message_data))

        self.update_message_data_string()
        self.ui.tblFuzzingValues.resize_me()

        self.create_connects()
        self.restoreGeometry(
            settings.read("{}/geometry".format(self.__class__.__name__), type=bytes)
        )

    @property
    def message(self):
        return self.protocol.messages[int(self.ui.spinBoxFuzzMessage.value() - 1)]

    @property
    def current_label_index(self):
        return self.ui.comboBoxFuzzingLabel.currentIndex()

    @property
    def current_label(self) -> ProtocolLabel:
        if len(self.message.message_type) == 0:
            return None

        cur_label = self.message.message_type[self.current_label_index].get_copy()
        self.message.message_type[self.current_label_index] = cur_label
        cur_label.fuzz_values = [
            fv for fv in cur_label.fuzz_values if fv
        ]  # Remove empty strings

        if len(cur_label.fuzz_values) == 0:
            cur_label.fuzz_values.append(
                self.message.plain_bits_str[cur_label.start : cur_label.end]
            )
        return cur_label

    @property
    def current_label_start(self):
        if self.current_label and self.message:
            return self.message.get_label_range(
                self.current_label, self.proto_view, False
            )[0]
        else:
            return -1

    @property
    def current_label_end(self):
        if self.current_label and self.message:
            return self.message.get_label_range(
                self.current_label, self.proto_view, False
            )[1]
        else:
            return -1

    @property
    def message_data(self):
        if self.proto_view == 0:
            return self.message.plain_bits_str
        elif self.proto_view == 1:
            return self.message.plain_hex_str
        elif self.proto_view == 2:
            return self.message.plain_ascii_str
        else:
            return None

    def create_connects(self):
        self.ui.spinBoxFuzzingStart.valueChanged.connect(self.on_fuzzing_start_changed)
        self.ui.spinBoxFuzzingEnd.valueChanged.connect(self.on_fuzzing_end_changed)
        self.ui.comboBoxFuzzingLabel.currentIndexChanged.connect(
            self.on_combo_box_fuzzing_label_current_index_changed
        )
        self.ui.btnRepeatValues.clicked.connect(self.on_btn_repeat_values_clicked)
        self.ui.btnAddRow.clicked.connect(self.on_btn_add_row_clicked)
        self.ui.btnDelRow.clicked.connect(self.on_btn_del_row_clicked)
        self.ui.tblFuzzingValues.deletion_wanted.connect(self.delete_lines)
        self.ui.chkBRemoveDuplicates.stateChanged.connect(
            self.on_remove_duplicates_state_changed
        )
        self.ui.sBAddRangeStart.valueChanged.connect(
            self.on_fuzzing_range_start_changed
        )
        self.ui.sBAddRangeEnd.valueChanged.connect(self.on_fuzzing_range_end_changed)
        self.ui.checkBoxLowerBound.stateChanged.connect(
            self.on_lower_bound_checked_changed
        )
        self.ui.checkBoxUpperBound.stateChanged.connect(
            self.on_upper_bound_checked_changed
        )
        self.ui.spinBoxLowerBound.valueChanged.connect(self.on_lower_bound_changed)
        self.ui.spinBoxUpperBound.valueChanged.connect(self.on_upper_bound_changed)
        self.ui.spinBoxRandomMinimum.valueChanged.connect(
            self.on_random_range_min_changed
        )
        self.ui.spinBoxRandomMaximum.valueChanged.connect(
            self.on_random_range_max_changed
        )
        self.ui.spinBoxFuzzMessage.valueChanged.connect(self.on_fuzz_msg_changed)
        self.ui.btnAddFuzzingValues.clicked.connect(
            self.on_btn_add_fuzzing_values_clicked
        )
        self.ui.comboBoxFuzzingLabel.editTextChanged.connect(
            self.set_current_label_name
        )

    def update_message_data_string(self):
        fuz_start = self.current_label_start
        fuz_end = self.current_label_end
        num_proto_bits = 10
        num_fuz_bits = 16

        proto_start = fuz_start - num_proto_bits
        preambel = "... "
        if proto_start <= 0:
            proto_start = 0
            preambel = ""

        proto_end = fuz_end + num_proto_bits
        postambel = " ..."
        if proto_end >= len(self.message_data) - 1:
            proto_end = len(self.message_data) - 1
            postambel = ""

        fuzamble = ""
        if fuz_end - fuz_start > num_fuz_bits:
            fuz_end = fuz_start + num_fuz_bits
            fuzamble = "..."

        self.ui.lPreBits.setText(
            preambel + self.message_data[proto_start : self.current_label_start]
        )
        self.ui.lFuzzedBits.setText(self.message_data[fuz_start:fuz_end] + fuzamble)
        self.ui.lPostBits.setText(
            self.message_data[self.current_label_end : proto_end] + postambel
        )
        self.set_add_spinboxes_maximum_on_label_change()

    def closeEvent(self, event: QCloseEvent):
        settings.write(
            "{}/geometry".format(self.__class__.__name__), self.saveGeometry()
        )
        super().closeEvent(event)

    @pyqtSlot(int)
    def on_fuzzing_start_changed(self, value: int):
        self.ui.spinBoxFuzzingEnd.setMinimum(self.ui.spinBoxFuzzingStart.value())
        new_start = self.message.convert_index(value - 1, self.proto_view, 0, False)[0]
        self.current_label.start = new_start
        self.current_label.fuzz_values[:] = []
        self.update_message_data_string()
        self.fuzz_table_model.update()
        self.ui.tblFuzzingValues.resize_me()

    @pyqtSlot(int)
    def on_fuzzing_end_changed(self, value: int):
        self.ui.spinBoxFuzzingStart.setMaximum(self.ui.spinBoxFuzzingEnd.value())
        new_end = (
            self.message.convert_index(value - 1, self.proto_view, 0, False)[1] + 1
        )
        self.current_label.end = new_end
        self.current_label.fuzz_values[:] = []
        self.update_message_data_string()
        self.fuzz_table_model.update()
        self.ui.tblFuzzingValues.resize_me()

    @pyqtSlot(int)
    def on_combo_box_fuzzing_label_current_index_changed(self, index: int):
        self.fuzz_table_model.fuzzing_label = self.current_label
        self.fuzz_table_model.update()
        self.update_message_data_string()
        self.ui.tblFuzzingValues.resize_me()

        self.ui.spinBoxFuzzingStart.blockSignals(True)
        self.ui.spinBoxFuzzingStart.setValue(self.current_label_start + 1)
        self.ui.spinBoxFuzzingStart.blockSignals(False)

        self.ui.spinBoxFuzzingEnd.blockSignals(True)
        self.ui.spinBoxFuzzingEnd.setValue(self.current_label_end)
        self.ui.spinBoxFuzzingEnd.blockSignals(False)

    @pyqtSlot()
    def on_btn_add_row_clicked(self):
        self.current_label.add_fuzz_value()
        self.fuzz_table_model.update()

    @pyqtSlot()
    def on_btn_del_row_clicked(self):
        min_row, max_row, _, _ = self.ui.tblFuzzingValues.selection_range()
        self.delete_lines(min_row, max_row)

    @pyqtSlot(int, int)
    def delete_lines(self, min_row, max_row):
        if min_row == -1:
            self.current_label.fuzz_values = self.current_label.fuzz_values[:-1]
        else:
            self.current_label.fuzz_values = (
                self.current_label.fuzz_values[:min_row]
                + self.current_label.fuzz_values[max_row + 1 :]
            )

        _ = self.current_label  # if user deleted all, this will restore a fuzz value

        self.fuzz_table_model.update()

    @pyqtSlot()
    def on_remove_duplicates_state_changed(self):
        self.fuzz_table_model.remove_duplicates = (
            self.ui.chkBRemoveDuplicates.isChecked()
        )
        self.fuzz_table_model.update()
        self.remove_duplicates()

    @pyqtSlot()
    def set_add_spinboxes_maximum_on_label_change(self):
        nbits = (
            self.current_label.end - self.current_label.start
        )  # Use Bit Start/End for maximum calc.
        if nbits >= 32:
            nbits = 31
        max_val = 2**nbits - 1
        self.ui.sBAddRangeStart.setMaximum(max_val - 1)
        self.ui.sBAddRangeEnd.setMaximum(max_val)
        self.ui.sBAddRangeEnd.setValue(max_val)
        self.ui.sBAddRangeStep.setMaximum(max_val)
        self.ui.spinBoxLowerBound.setMaximum(max_val - 1)
        self.ui.spinBoxUpperBound.setMaximum(max_val)
        self.ui.spinBoxUpperBound.setValue(max_val)
        self.ui.spinBoxBoundaryNumber.setMaximum(int(max_val / 2) + 1)
        self.ui.spinBoxRandomMinimum.setMaximum(max_val - 1)
        self.ui.spinBoxRandomMaximum.setMaximum(max_val)
        self.ui.spinBoxRandomMaximum.setValue(max_val)

    @pyqtSlot(int)
    def on_fuzzing_range_start_changed(self, value: int):
        self.ui.sBAddRangeEnd.setMinimum(value)
        self.ui.sBAddRangeStep.setMaximum(self.ui.sBAddRangeEnd.value() - value)

    @pyqtSlot(int)
    def on_fuzzing_range_end_changed(self, value: int):
        self.ui.sBAddRangeStart.setMaximum(value - 1)
        self.ui.sBAddRangeStep.setMaximum(value - self.ui.sBAddRangeStart.value())

    @pyqtSlot()
    def on_lower_bound_checked_changed(self):
        if self.ui.checkBoxLowerBound.isChecked():
            self.ui.spinBoxLowerBound.setEnabled(True)
            self.ui.spinBoxBoundaryNumber.setEnabled(True)
        elif not self.ui.checkBoxUpperBound.isChecked():
            self.ui.spinBoxLowerBound.setEnabled(False)
            self.ui.spinBoxBoundaryNumber.setEnabled(False)
        else:
            self.ui.spinBoxLowerBound.setEnabled(False)

    @pyqtSlot()
    def on_upper_bound_checked_changed(self):
        if self.ui.checkBoxUpperBound.isChecked():
            self.ui.spinBoxUpperBound.setEnabled(True)
            self.ui.spinBoxBoundaryNumber.setEnabled(True)
        elif not self.ui.checkBoxLowerBound.isChecked():
            self.ui.spinBoxUpperBound.setEnabled(False)
            self.ui.spinBoxBoundaryNumber.setEnabled(False)
        else:
            self.ui.spinBoxUpperBound.setEnabled(False)

    @pyqtSlot()
    def on_lower_bound_changed(self):
        self.ui.spinBoxUpperBound.setMinimum(self.ui.spinBoxLowerBound.value())
        self.ui.spinBoxBoundaryNumber.setMaximum(
            math.ceil(
                (self.ui.spinBoxUpperBound.value() - self.ui.spinBoxLowerBound.value())
                / 2
            )
        )

    @pyqtSlot()
    def on_upper_bound_changed(self):
        self.ui.spinBoxLowerBound.setMaximum(self.ui.spinBoxUpperBound.value() - 1)
        self.ui.spinBoxBoundaryNumber.setMaximum(
            math.ceil(
                (self.ui.spinBoxUpperBound.value() - self.ui.spinBoxLowerBound.value())
                / 2
            )
        )

    @pyqtSlot()
    def on_random_range_min_changed(self):
        self.ui.spinBoxRandomMaximum.setMinimum(self.ui.spinBoxRandomMinimum.value())

    @pyqtSlot()
    def on_random_range_max_changed(self):
        self.ui.spinBoxRandomMinimum.setMaximum(
            self.ui.spinBoxRandomMaximum.value() - 1
        )

    @pyqtSlot()
    def on_btn_add_fuzzing_values_clicked(self):
        if self.ui.comboBoxStrategy.currentIndex() == 0:
            self.__add_fuzzing_range()
        elif self.ui.comboBoxStrategy.currentIndex() == 1:
            self.__add_fuzzing_boundaries()
        elif self.ui.comboBoxStrategy.currentIndex() == 2:
            self.__add_random_fuzzing_values()

    def __add_fuzzing_range(self):
        start = self.ui.sBAddRangeStart.value()
        end = self.ui.sBAddRangeEnd.value()
        step = self.ui.sBAddRangeStep.value()
        self.fuzz_table_model.add_range(start, end + 1, step)

    def __add_fuzzing_boundaries(self):
        lower_bound = -1
        if self.ui.spinBoxLowerBound.isEnabled():
            lower_bound = self.ui.spinBoxLowerBound.value()

        upper_bound = -1
        if self.ui.spinBoxUpperBound.isEnabled():
            upper_bound = self.ui.spinBoxUpperBound.value()

        num_vals = self.ui.spinBoxBoundaryNumber.value()
        self.fuzz_table_model.add_boundaries(lower_bound, upper_bound, num_vals)

    def __add_random_fuzzing_values(self):
        n = self.ui.spinBoxNumberRandom.value()
        minimum = self.ui.spinBoxRandomMinimum.value()
        maximum = self.ui.spinBoxRandomMaximum.value()
        self.fuzz_table_model.add_random(n, minimum, maximum)

    def remove_duplicates(self):
        if self.ui.chkBRemoveDuplicates.isChecked():
            for lbl in self.message.message_type:
                seq = lbl.fuzz_values[:]
                seen = set()
                add_seen = seen.add
                lbl.fuzz_values = [l for l in seq if not (l in seen or add_seen(l))]

    @pyqtSlot()
    def set_current_label_name(self):
        self.current_label.name = self.ui.comboBoxFuzzingLabel.currentText()
        self.ui.comboBoxFuzzingLabel.setItemText(
            self.ui.comboBoxFuzzingLabel.currentIndex(), self.current_label.name
        )

    @pyqtSlot(int)
    def on_fuzz_msg_changed(self, index: int):
        self.ui.comboBoxFuzzingLabel.setDisabled(False)

        sel_label_ind = self.ui.comboBoxFuzzingLabel.currentIndex()
        self.ui.comboBoxFuzzingLabel.blockSignals(True)
        self.ui.comboBoxFuzzingLabel.clear()

        if len(self.message.message_type) == 0:
            self.ui.comboBoxFuzzingLabel.setDisabled(True)
            return

        self.ui.comboBoxFuzzingLabel.addItems(
            [lbl.name for lbl in self.message.message_type]
        )
        self.ui.comboBoxFuzzingLabel.blockSignals(False)

        if sel_label_ind < self.ui.comboBoxFuzzingLabel.count():
            self.ui.comboBoxFuzzingLabel.setCurrentIndex(sel_label_ind)
        else:
            self.ui.comboBoxFuzzingLabel.setCurrentIndex(0)

        self.fuzz_table_model.fuzzing_label = self.current_label
        self.fuzz_table_model.update()
        self.update_message_data_string()

    @pyqtSlot()
    def on_btn_repeat_values_clicked(self):
        num_repeats, ok = QInputDialog.getInt(
            self,
            self.tr("How many times shall values be repeated?"),
            self.tr("Number of repeats:"),
            1,
            1,
        )
        if ok:
            self.ui.chkBRemoveDuplicates.setChecked(False)
            min_row, max_row, _, _ = self.ui.tblFuzzingValues.selection_range()
            if min_row == -1:
                start, end = 0, len(self.current_label.fuzz_values)
            else:
                start, end = min_row, max_row + 1
            self.fuzz_table_model.repeat_fuzzing_values(start, end, num_repeats)
