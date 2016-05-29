import math

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog

from urh.models.FuzzingTableModel import FuzzingTableModel
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.ui.ui_fuzzing import Ui_FuzzingDialog


class FuzzingDialogController(QDialog):
    def __init__(self, proto_block: ProtocolBlock, label_index, proto_view: int, parent=None):
        super().__init__(parent)
        self.ui = Ui_FuzzingDialog()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.current_label_index = label_index
        self.block = proto_block

        self.proto_view = proto_view
        self.fuzz_table_model = FuzzingTableModel(self.current_label, proto_view)
        self.fuzz_table_model.remove_duplicates = self.ui.chkBRemoveDuplicates.isChecked()
        self.ui.tblFuzzingValues.setModel(self.fuzz_table_model)
        self.fuzz_table_model.update()

        self.ui.comboBoxFuzzingLabel.addItems([l.name for l in self.block.labelset])
        self.ui.comboBoxFuzzingLabel.setCurrentIndex(self.current_label_index)

        self.ui.spinBoxFuzzingStart.setValue(self.current_label_start + 1)
        self.ui.spinBoxFuzzingEnd.setValue(self.current_label_end)
        self.ui.spinBoxFuzzingStart.setMaximum(len(self.block_data))
        self.ui.spinBoxFuzzingEnd.setMaximum(len(self.block_data))

        self.epic_mode = False

        self.update_block_data_string()
        self.ui.tblFuzzingValues.resize_me()

        self.create_connects()

    @property
    def current_label(self) -> ProtocolLabel:
        cur_label = self.block.labelset[self.current_label_index]
        cur_label.fuzz_values = [fv for fv in cur_label.fuzz_values if fv] # Remove empty strings

        if len(cur_label.fuzz_values) == 0:
            cur_label.fuzz_values.append(self.block.plain_bits_str[cur_label.start:cur_label.end])
        return cur_label

    @property
    def current_label_start(self):
        return self.block.get_label_range(self.current_label, self.proto_view, False)[0]

    @property
    def current_label_end(self):
        return self.block.get_label_range(self.current_label, self.proto_view, False)[1]

    @property
    def block_data(self):
        if self.proto_view == 0:
            return self.block.plain_bits_str
        elif self.proto_view == 1:
            return self.block.plain_hex_str
        elif self.proto_view == 2:
            return self.block.plain_ascii_str
        else:
            return None

    def create_connects(self):
        self.ui.spinBoxFuzzingStart.valueChanged.connect(self.on_fuzzing_start_changed)
        self.ui.spinBoxFuzzingEnd.valueChanged.connect(self.on_fuzzing_end_changed)
        self.ui.comboBoxFuzzingLabel.currentIndexChanged.connect(self.on_current_label_changed)
        self.ui.spinBoxRefBlock.valueChanged.connect(self.on_fuzzing_ref_block_changed)
        self.ui.btnAddRow.clicked.connect(self.on_btn_add_row_clicked)
        self.ui.btnDelRow.clicked.connect(self.on_btn_del_row_clicked)
        self.ui.tblFuzzingValues.deletion_wanted.connect(self.delete_lines)
        self.ui.chkBRemoveDuplicates.stateChanged.connect(self.on_remove_duplicates_state_changed)
        self.ui.sBAddRangeStart.valueChanged.connect(self.on_fuzzing_range_start_changed)
        self.ui.sBAddRangeEnd.valueChanged.connect(self.on_fuzzing_range_end_changed)
        self.ui.checkBoxLowerBound.stateChanged.connect(self.on_lower_bound_checked_changed)
        self.ui.checkBoxUpperBound.stateChanged.connect(self.on_upper_bound_checked_changed)
        self.ui.spinBoxLowerBound.valueChanged.connect(self.on_lower_bound_changed)
        self.ui.spinBoxUpperBound.valueChanged.connect(self.on_upper_bound_changed)
        self.ui.spinBoxRandomMinimum.valueChanged.connect(self.on_random_range_min_changed)
        self.ui.spinBoxRandomMaximum.valueChanged.connect(self.on_random_range_max_changed)
        self.ui.btnAddRange.clicked.connect(self.on_btn_add_range_clicked)
        self.ui.btnAddBoundaries.clicked.connect(self.on_btn_add_boundaries_clicked)
        self.ui.btnAddRandom.clicked.connect(self.on_btn_add_random_clicked)
        self.ui.btnSaveAndClose.clicked.connect(self.close)
        self.ui.comboBoxFuzzingLabel.editTextChanged.connect(self.set_current_label_name)

    def update_block_data_string(self):
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
        if proto_end >= len(self.block_data) - 1:
            proto_end = len(self.block_data) - 1
            postambel = ""

        fuzamble = ""
        if fuz_end - fuz_start > num_fuz_bits:
            fuz_end = fuz_start + num_fuz_bits
            fuzamble = "..."

        self.ui.lPreBits.setText(preambel + self.block_data[proto_start:self.current_label_start])
        self.ui.lFuzzedBits.setText(self.block_data[fuz_start:fuz_end] + fuzamble)
        self.ui.lPostBits.setText(self.block_data[self.current_label_end:proto_end] + postambel)
        self.set_add_spinboxes_maximum_on_label_change()

    def enter_epic_mode(self):
        """
        Versetzt den Dialog in den Epic Mode: Alle Labels sind gleichzeitig editierbar,
        d.h. ihnen können alle auf einmal Werte hinzugefügt werden
        :return:
        """
        self.ui.comboBoxFuzzingLabel.setEnabled(False)
        self.ui.comboBoxFuzzingLabel.blockSignals(True)
        self.ui.comboBoxFuzzingLabel.addItem("All Labels")
        self.ui.comboBoxFuzzingLabel.setCurrentIndex(self.ui.comboBoxFuzzingLabel.count() - 1)
        self.ui.lSourceBlock.hide()
        self.ui.lPreBits.hide()
        self.ui.lFuzzedBits.hide()
        self.ui.lPostBits.hide()
        self.ui.lFuzzingStart.hide()
        self.ui.lFuzzingEnd.hide()
        self.ui.lFuzzingReferenceBlock.hide()
        self.ui.spinBoxFuzzingStart.hide()
        self.ui.spinBoxFuzzingEnd.hide()
        self.ui.spinBoxRefBlock.hide()
        self.ui.lFuzzedValues.setText(
            self.tr("In this dialog you can add fuzzed values to all labels for convenience."))
        self.ui.tblFuzzingValues.setDisabled(True)
        self.ui.btnAddRow.hide()
        self.ui.btnDelRow.hide()
        self.epic_mode = True

    @pyqtSlot()
    def on_fuzzing_start_changed(self):
        self.ui.spinBoxFuzzingEnd.setMinimum(self.ui.spinBoxFuzzingStart.value())
        value = self.ui.spinBoxFuzzingStart.value()
        new_start = \
        self.block.convert_index(value - 1, self.proto_view, 0, False)[0]
        self.block.labelset[self.current_label_index].start = new_start
        self.current_label.fuzz_values[:] = []
        self.update_block_data_string()
        self.fuzz_table_model.update()
        self.ui.tblFuzzingValues.resize_me()

    @pyqtSlot()
    def on_fuzzing_end_changed(self):
        self.ui.spinBoxFuzzingStart.setMaximum(self.ui.spinBoxFuzzingEnd.value())
        value = self.ui.spinBoxFuzzingEnd.value()
        new_end = self.block.convert_index(value - 1, self.proto_view, 0, False)[1] + 1
        self.block.labelset[self.current_label_index].end = new_end
        self.current_label.fuzz_values[:] = []
        self.update_block_data_string()
        self.fuzz_table_model.update()
        self.ui.tblFuzzingValues.resize_me()

    @pyqtSlot()
    def on_current_label_changed(self):
        self.current_label_index = self.ui.comboBoxFuzzingLabel.currentIndex()
        if self.current_label_index < self.ui.comboBoxFuzzingLabel.count():
            self.fuzz_table_model.fuzzing_label = self.current_label
            self.fuzz_table_model.update()
            self.update_block_data_string()
            self.ui.tblFuzzingValues.resize_me()

    @pyqtSlot()
    def on_fuzzing_ref_block_changed(self):
        self.current_label.refblock = self.ui.spinBoxRefBlock.value() - 1
        self.update_block_data_string()
        self.ui.spinBoxFuzzingStart.setMaximum(len(self.block_data))
        self.ui.spinBoxFuzzingEnd.setMaximum(len(self.block_data))
        self.ui.tblFuzzingValues.resize_me()

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
            self.current_label.fuzz_values = self.current_label.fuzz_values[:min_row] + self.current_label.fuzz_values[
                                                                                        max_row + 1:]

        _ = self.current_label  # if user deleted all, this will restore a fuzz value

        self.fuzz_table_model.update()

    @pyqtSlot()
    def on_remove_duplicates_state_changed(self):
        self.fuzz_table_model.remove_duplicates = self.ui.chkBRemoveDuplicates.isChecked()
        self.fuzz_table_model.update()
        self.remove_duplicates()

    @pyqtSlot()
    def set_add_spinboxes_maximum_on_label_change(self):
        nbits = self.current_label.end - self.current_label.start  # Use Bit Start/End for maximum calc.
        if nbits >= 32:
            nbits = 31
        max_val = 2 ** (nbits) - 1
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

    @pyqtSlot()
    def on_fuzzing_range_start_changed(self):
        self.ui.sBAddRangeEnd.setMinimum(self.ui.sBAddRangeStart.value())
        self.ui.sBAddRangeStep.setMaximum(self.ui.sBAddRangeEnd.value() - self.ui.sBAddRangeStart.value())

    @pyqtSlot()
    def on_fuzzing_range_end_changed(self):
        self.ui.sBAddRangeStart.setMaximum(self.ui.sBAddRangeEnd.value() - 1)
        self.ui.sBAddRangeStep.setMaximum(self.ui.sBAddRangeEnd.value() - self.ui.sBAddRangeStart.value())

    @pyqtSlot()
    def on_lower_bound_checked_changed(self):
        if self.ui.checkBoxLowerBound.isChecked():
            self.ui.spinBoxLowerBound.setEnabled(True)
            self.ui.btnAddBoundaries.setEnabled(True)
            self.ui.spinBoxBoundaryNumber.setEnabled(True)
        elif not self.ui.checkBoxUpperBound.isChecked():
            self.ui.spinBoxLowerBound.setEnabled(False)
            self.ui.btnAddBoundaries.setEnabled(False)
            self.ui.spinBoxBoundaryNumber.setEnabled(False)
        else:
            self.ui.spinBoxLowerBound.setEnabled(False)

    @pyqtSlot()
    def on_upper_bound_checked_changed(self):
        if self.ui.checkBoxUpperBound.isChecked():
            self.ui.spinBoxUpperBound.setEnabled(True)
            self.ui.btnAddBoundaries.setEnabled(True)
            self.ui.spinBoxBoundaryNumber.setEnabled(True)
        elif not self.ui.checkBoxLowerBound.isChecked():
            self.ui.spinBoxUpperBound.setEnabled(False)
            self.ui.btnAddBoundaries.setEnabled(False)
            self.ui.spinBoxBoundaryNumber.setEnabled(False)
        else:
            self.ui.spinBoxUpperBound.setEnabled(False)

    @pyqtSlot()
    def on_lower_bound_changed(self):
        self.ui.spinBoxUpperBound.setMinimum(self.ui.spinBoxLowerBound.value())
        self.ui.spinBoxBoundaryNumber.setMaximum(math.ceil((self.ui.spinBoxUpperBound.value()
                                                            - self.ui.spinBoxLowerBound.value()) / 2))

    @pyqtSlot()
    def on_upper_bound_changed(self):
        self.ui.spinBoxLowerBound.setMaximum(self.ui.spinBoxUpperBound.value() - 1)
        self.ui.spinBoxBoundaryNumber.setMaximum(math.ceil((self.ui.spinBoxUpperBound.value()
                                                            - self.ui.spinBoxLowerBound.value()) / 2))

    @pyqtSlot()
    def on_random_range_min_changed(self):
        self.ui.spinBoxRandomMaximum.setMinimum(self.ui.spinBoxRandomMinimum.value())

    @pyqtSlot()
    def on_random_range_max_changed(self):
        self.ui.spinBoxRandomMinimum.setMaximum(self.ui.spinBoxRandomMaximum.value() - 1)

    @pyqtSlot()
    def on_btn_add_range_clicked(self):
        start = self.ui.sBAddRangeStart.value()
        end = self.ui.sBAddRangeEnd.value()
        step = self.ui.sBAddRangeStep.value()
        if not self.epic_mode:
            self.fuzz_table_model.add_range(start, end + 1, step)
        else:
            self.fuzz_table_model.add_range(start, end + 1, step, self.block.labelset)
            self.remove_duplicates()

    @pyqtSlot()
    def on_btn_add_boundaries_clicked(self):
        lower_bound = -1
        if self.ui.spinBoxLowerBound.isEnabled():
            lower_bound = self.ui.spinBoxLowerBound.value()

        upper_bound = -1
        if self.ui.spinBoxUpperBound.isEnabled():
            upper_bound = self.ui.spinBoxUpperBound.value()

        num_vals = self.ui.spinBoxBoundaryNumber.value()

        if not self.epic_mode:
            self.fuzz_table_model.add_boundaries(lower_bound, upper_bound, num_vals)
        else:
            self.fuzz_table_model.add_boundaries(lower_bound, upper_bound, num_vals,
                                                 self.block.labelset)
            self.remove_duplicates()

    @pyqtSlot()
    def on_btn_add_random_clicked(self):
        n = self.ui.spinBoxNumberRandom.value()
        minimum = self.ui.spinBoxRandomMinimum.value()
        maximum = self.ui.spinBoxRandomMaximum.value()

        if not self.epic_mode:
            self.fuzz_table_model.add_random(n, minimum, maximum)
        else:
            self.fuzz_table_model.add_random(n, minimum, maximum, self.block.labelset)
            self.remove_duplicates()

    def remove_duplicates(self):
        if self.epic_mode and self.ui.chkBRemoveDuplicates.isChecked():
            for lbl in self.block.labelset:
                seq = lbl.fuzz_values[:]
                seen = set()
                add_seen = seen.add
                lbl.fuzz_values = [l for l in seq if not (l in seen or add_seen(l))]

    @pyqtSlot()
    def set_current_label_name(self):
        lbl = self.block.labelset[self.ui.comboBoxFuzzingLabel.currentIndex()]
        lbl.name = self.ui.comboBoxFuzzingLabel.currentText()
        self.ui.comboBoxFuzzingLabel.setItemText(self.ui.comboBoxFuzzingLabel.currentIndex(), lbl.name)
