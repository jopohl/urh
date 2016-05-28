import locale

import numpy
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFontMetrics, QFont
from PyQt5.QtWidgets import QInputDialog, QApplication, QWidget, QUndoStack

from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.FuzzingDialogController import FuzzingDialogController
from urh.controller.ModulatorDialogController import ModulatorDialogController
from urh.controller.SendRecvDialogController import SendRecvDialogController, Mode
from urh.models.GeneratorListModel import GeneratorListModel
from urh.models.GeneratorTableModel import GeneratorTableModel
from urh.models.GeneratorTreeModel import GeneratorTreeModel
from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.signalprocessing.encoding import encoding
from urh.ui.actions.Fuzz import Fuzz
from urh.ui.ui_generator import Ui_GeneratorTab
from urh.util import FileOperator
from urh.util.Errors import Errors
from urh.util.Formatter import Formatter
from urh.util.ProjectManager import ProjectManager
from urh.util.Logger import logger


class GeneratorTabController(QWidget):
    def __init__(self, compare_frame_controller: CompareFrameController,
                 project_manager: ProjectManager, parent=None):
        """
        :type encoders: list of encoding
        :return:
        """
        super().__init__(parent)
        self.ui = Ui_GeneratorTab()
        self.ui.setupUi(self)

        self.modulated_scene_is_locked = False

        self.ui.treeProtocols.setHeaderHidden(True)
        self.tree_model = GeneratorTreeModel(compare_frame_controller)
        self.tree_model.set_root_item(compare_frame_controller.proto_tree_model.rootItem)
        self.tree_model.controller = self
        self.ui.treeProtocols.setModel(self.tree_model)

        self.has_default_modulation = True

        self.table_model = GeneratorTableModel(compare_frame_controller.proto_tree_model.rootItem, [Modulator("Modulation")])
        """:type: GeneratorTableModel """
        self.table_model.controller = self
        self.ui.tableBlocks.setModel(self.table_model)

        self.label_list_model = GeneratorListModel(self.table_model.protocol)
        self.ui.listViewProtoLabels.setModel(self.label_list_model)

        self.refresh_modulators()
        self.on_selected_modulation_changed()
        self.set_fuzzing_ui_status()
        self.project_manager = project_manager
        self.ui.prBarGeneration.hide()
        self.create_connects(compare_frame_controller)


    def create_connects(self, compare_frame_controller):
        compare_frame_controller.proto_tree_model.layoutChanged.connect(self.refresh_tree)
        self.ui.btnEditModulation.clicked.connect(self.show_modulation_dialog)
        self.ui.cBoxModulations.currentIndexChanged.connect(self.on_selected_modulation_changed)
        self.ui.tableBlocks.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        self.table_model.undo_stack.indexChanged.connect(self.refresh_table)
        self.table_model.undo_stack.indexChanged.connect(self.refresh_pause_list)
        self.table_model.undo_stack.indexChanged.connect(self.refresh_label_list)
        self.table_model.undo_stack.indexChanged.connect(self.refresh_estimated_time)
        self.table_model.undo_stack.indexChanged.connect(self.set_fuzzing_ui_status)
        self.table_model.protocol.qt_signals.line_duplicated.connect(self.refresh_pause_list)
        self.label_list_model.protolabel_fuzzing_status_changed.connect(self.set_fuzzing_ui_status)
        self.ui.cbViewType.currentIndexChanged.connect(self.on_view_type_changed)
        self.ui.btnSend.clicked.connect(self.on_btn_send_clicked)
        self.ui.btnSave.clicked.connect(self.on_btn_save_clicked)

        self.label_list_model.protolabel_removed.connect(self.handle_proto_label_removed)

        self.ui.lWPauses.item_edit_clicked.connect(self.edit_pause_item)
        self.ui.lWPauses.itemSelectionChanged.connect(self.on_lWpauses_selection_changed)
        self.ui.lWPauses.lost_focus.connect(self.on_lWPauses_lost_focus)
        self.ui.lWPauses.doubleClicked.connect(self.on_lWPauses_double_clicked)
        self.ui.btnGenerate.clicked.connect(self.generate_file)
        self.ui.listViewProtoLabels.editActionTriggered.connect(self.show_fuzzing_dialog)
        self.ui.listViewProtoLabels.editAllActionTriggered.connect(self.show_epic_fuzzing_dialog)
        self.label_list_model.protolabel_fuzzing_status_changed.connect(self.handle_plabel_fuzzing_state_changed)
        self.ui.btnFuzz.clicked.connect(self.on_btn_fuzzing_clicked)
        self.ui.tableBlocks.create_fuzzing_label_clicked.connect(self.create_fuzzing_label)
        self.ui.tableBlocks.edit_fuzzing_label_clicked.connect(self.show_fuzzing_dialog)
        self.ui.listViewProtoLabels.selection_changed.connect(self.handle_label_selection_changed)
        self.ui.listViewProtoLabels.edit_on_item_triggered.connect(self.show_fuzzing_dialog)

    @property
    def active_groups(self):
        return self.tree_model.groups

    @property
    def modulators(self):
        return self.table_model.protocol.modulators

    @modulators.setter
    def modulators(self, value):
        assert type(value) == list
        self.table_model.protocol.modulators = value

    @pyqtSlot()
    def refresh_tree(self):
        #self.tree_model.reset()
        self.tree_model.layoutChanged.emit()
        self.ui.treeProtocols.expandAll()

    @pyqtSlot()
    def refresh_table(self):
        self.table_model.update()
        self.ui.tableBlocks.resize_columns()
        is_data_there = self.table_model.display_data is not None and len(self.table_model.display_data) > 0
        self.ui.btnSend.setEnabled(is_data_there)
        self.ui.btnGenerate.setEnabled(is_data_there)

    @pyqtSlot()
    def refresh_label_list(self):
        self.label_list_model.layoutChanged.emit()

    @property
    def generator_undo_stack(self) -> QUndoStack:
        return self.table_model.undo_stack

    def refresh_modulators(self):
        current_index = 0
        if type(self.sender()) == ModulatorDialogController:
            current_index = self.sender().ui.comboBoxCustomModulations.currentIndex()
        self.ui.cBoxModulations.clear()
        for modulator in self.modulators:
            self.ui.cBoxModulations.addItem(modulator.name)

        self.ui.cBoxModulations.setCurrentIndex(current_index)

    @pyqtSlot()
    def on_selected_modulation_changed(self):
        cur_ind = self.ui.cBoxModulations.currentIndex()
        min_row, max_row, _, _ = self.ui.tableBlocks.selection_range()
        if min_row > -1:
            # Modulation für Selektierte Blöcke setzen
            for row in range(min_row, max_row + 1):
                try:
                    self.table_model.protocol.blocks[row].modulator_indx = cur_ind
                except IndexError:
                    continue


        self.show_modulation_info()

    def show_modulation_info(self):

        show = not self.has_default_modulation or self.modulators[0] != Modulator("Modulation")

        if not show:
            self.ui.btnEditModulation.setStyleSheet("background: orange")
            font = QFont()
            font.setBold(True)
            self.ui.btnEditModulation.setFont(font)
        else:
            self.ui.btnEditModulation.setStyleSheet("")
            self.ui.btnEditModulation.setFont(QFont())

        cur_ind = self.ui.cBoxModulations.currentIndex()
        cur_mod = self.modulators[cur_ind]
        self.ui.lCarrierFreqValue.setText(cur_mod.carrier_frequency_str)
        self.ui.lCarrierPhaseValue.setText(cur_mod.carrier_phase_str)
        self.ui.lBitLenValue.setText(cur_mod.bit_len_str)
        self.ui.lSampleRateValue.setText(cur_mod.sample_rate_str)
        mod_type = cur_mod.modulation_type_str
        self.ui.lModTypeValue.setText(mod_type)
        if mod_type == "ASK":
            prefix = "Amplitude"
        elif mod_type == "PSK":
            prefix = "Phase"
        elif mod_type in ("FSK", "GFSK"):
            prefix = "Frequency"
        else:
            prefix = "Unknown Modulation Type (This should not happen...)"

        self.ui.lParamForZero.setText(prefix + " for 0:")
        self.ui.lParamForZeroValue.setText(cur_mod.param_for_zero_str)
        self.ui.lParamForOne.setText(prefix + " for 1:")
        self.ui.lParamForOneValue.setText(cur_mod.param_for_one_str)

    @pyqtSlot()
    def show_modulation_dialog(self):
        preselected_index = self.ui.cBoxModulations.currentIndex()
        min_row, max_row, start, end = self.ui.tableBlocks.selection_range()
        if min_row > -1:
            try:
                block = self.table_model.protocol.blocks[min_row]
                preselected_index = block.modulator_indx
            except IndexError:
                block = ProtocolBlock([True, False, True, False], 0, [], LabelSet("empty"))
        else:
            block = ProtocolBlock([True, False, True, False], 0, [], LabelSet("empty"))
            if len(self.table_model.protocol.blocks) > 0:
                block.bit_len = self.table_model.protocol.blocks[0].bit_len

        for m in self.modulators:
            m.default_sample_rate = self.project_manager.sample_rate

        c = ModulatorDialogController(self.modulators, parent = self)
        c.ui.treeViewSignals.setModel(self.tree_model)
        c.ui.treeViewSignals.expandAll()
        c.ui.comboBoxCustomModulations.setCurrentIndex(preselected_index)
        # c.ui.spinBoxBitLength.setValue(block.bit_len) Overrides Modulators value

        c.finished.connect(self.refresh_modulators)
        c.finished.connect(self.refresh_pause_list)
        c.show()
        bits = block.encoded_bits_str[0:10]
        c.original_bits = bits
        c.ui.linEdDataBits.setText(bits)
        c.ui.gVOriginalSignal.signal_tree_root = self.tree_model.rootItem
        c.draw_original_signal()
        c.ui.gVModulated.draw_full()
        c.ui.gVData.draw_full()
        c.ui.gVCarrier.draw_full()

        self.has_default_modulation = False

    @pyqtSlot()
    def on_table_selection_changed(self):
        min_row, max_row, start, end = self.ui.tableBlocks.selection_range()

        if min_row == -1:
            self.ui.lEncodingValue.setText("-")  #
            self.ui.lEncodingValue.setToolTip("")
            return

        container = self.table_model.protocol
        block = container.blocks[min_row]
        decoder_name = block.decoder.name
        metrics = QFontMetrics(self.ui.lEncodingValue.font())
        elidedName = metrics.elidedText(decoder_name, Qt.ElideRight, self.ui.lEncodingValue.width())
        self.ui.lEncodingValue.setText(elidedName)
        self.ui.lEncodingValue.setToolTip(decoder_name)
        self.ui.cBoxModulations.blockSignals(True)
        self.ui.cBoxModulations.setCurrentIndex(block.modulator_indx)
        self.show_modulation_info()
        self.ui.cBoxModulations.blockSignals(False)

    @pyqtSlot(int)
    def edit_pause_item(self, index: int):
        block = self.table_model.protocol.blocks[index]
        cur_len = block.pause
        new_len, ok = QInputDialog.getInt(self, self.tr("Enter new Pause Length"),
                                          self.tr("Pause Length:"), cur_len, 0)
        if ok:
            block.pause = new_len
            self.refresh_pause_list()

    @pyqtSlot()
    def on_lWPauses_double_clicked(self):
        sel_indexes = [index.row() for index in self.ui.lWPauses.selectedIndexes()]
        if len(sel_indexes) > 0:
            self.edit_pause_item(sel_indexes[0])

    @pyqtSlot()
    def refresh_pause_list(self):
        self.ui.lWPauses.clear()
        fmt_str = "Pause ({1:d}-{2:d}) <{0:d} samples ({3})>"
        for i, pause in enumerate(self.table_model.protocol.pauses):
            sr = self.modulators[self.table_model.protocol.blocks[i].modulator_indx].sample_rate
            item = fmt_str.format(pause, i + 1, i + 2, Formatter.science_time(pause / sr))
            self.ui.lWPauses.addItem(item)

    @pyqtSlot()
    def on_lWpauses_selection_changed(self):
        rows = [index.row() for index in self.ui.lWPauses.selectedIndexes()]
        if len(rows) == 0:
            return
        self.ui.tableBlocks.show_pause_active = True
        self.ui.tableBlocks.pause_row = rows[0]
        self.ui.tableBlocks.viewport().update()
        self.ui.tableBlocks.scrollTo(self.table_model.index(rows[0], 0))

    @pyqtSlot()
    def on_lWPauses_lost_focus(self):
        self.ui.tableBlocks.show_pause_active = False
        self.ui.tableBlocks.viewport().update()

    @pyqtSlot()
    def generate_file(self):
        modulated_samples = self.modulate_data()
        FileOperator.save_data_dialog("", modulated_samples, parent=self)

    def modulate_data(self):
        pos = 0
        modulated_samples = []
        container = self.table_model.protocol
        self.ui.prBarGeneration.show()
        self.ui.prBarGeneration.setValue(0)
        self.ui.prBarGeneration.setMaximum(self.table_model.row_count)
        for i in range(0, self.table_model.row_count):
            block = container.blocks[i]
            modulator = self.modulators[block.modulator_indx]
            modulator.modulate(start=pos, data=block.encoded_bits, pause=block.pause)
            modulated_samples.append(modulator.modulated_samples)
            pos += len(modulator.modulated_samples)
            self.ui.prBarGeneration.setValue(i + 1)
            QApplication.processEvents()

        self.ui.prBarGeneration.hide()
        return numpy.concatenate(modulated_samples).astype(numpy.complex64)

    @pyqtSlot(int)
    def show_fuzzing_dialog(self, label_index: int):
        view = self.ui.cbViewType.currentIndex()
        fdc = FuzzingDialogController(self.table_model.protocol, label_index, view, parent=self)
        fdc.show()
        fdc.finished.connect(self.refresh_label_list)
        fdc.finished.connect(self.refresh_table)
        fdc.finished.connect(self.set_fuzzing_ui_status)

    @pyqtSlot()
    def show_epic_fuzzing_dialog(self):
        view = self.ui.cbViewType.currentIndex()
        fdc = FuzzingDialogController(self.table_model.protocol, 0, view, parent=self)
        fdc.enter_epic_mode()
        fdc.show()
        fdc.finished.connect(self.refresh_label_list)
        fdc.finished.connect(self.refresh_table)
        fdc.finished.connect(self.set_fuzzing_ui_status)

    @pyqtSlot()
    def handle_plabel_fuzzing_state_changed(self):
        self.refresh_table()
        self.label_list_model.layoutChanged.emit()

    @pyqtSlot(ProtocolLabel)
    def handle_proto_label_removed(self, plabel: ProtocolLabel):
        self.refresh_label_list()
        self.refresh_table()
        self.set_fuzzing_ui_status()

    @pyqtSlot()
    def on_btn_fuzzing_clicked(self):
        fuz_mode = "Successive"
        if self.ui.rbConcurrent.isChecked():
            fuz_mode = "Concurrent"
        elif self.ui.rBExhaustive.isChecked():
            fuz_mode = "Exhaustive"

        fuzz_action = Fuzz(self.table_model.protocol, fuz_mode)
        self.table_model.undo_stack.push(fuzz_action)

    @pyqtSlot()
    def set_fuzzing_ui_status(self):
        btn_was_enabled = self.ui.btnFuzz.isEnabled()
        pac = self.table_model.protocol
        self.ui.btnFuzz.setEnabled(len(pac.active_fuzzing_labels) > 0)
        if self.ui.btnFuzz.isEnabled() and not btn_was_enabled:
            font = self.ui.btnFuzz.font()
            font.setBold(True)
            self.ui.btnFuzz.setFont(font)
        else:
            font = self.ui.btnFuzz.font()
            font.setBold(False)
            self.ui.btnFuzz.setFont(font)
            self.ui.btnFuzz.setStyleSheet("")

        has_same_block = pac.has_fuzz_labels_with_same_block
        self.ui.rBSuccessive.setEnabled(has_same_block)
        self.ui.rBExhaustive.setEnabled(has_same_block)
        self.ui.rbConcurrent.setEnabled(has_same_block)

    @pyqtSlot()
    def refresh_estimated_time(self):
        c = self.table_model.protocol
        if c.num_blocks == 0:
            self.ui.lEstimatedTime.setText("Estimated Time: ")
            return

        avg_block_len = numpy.mean([len(block.encoded_bits) for block in c.blocks])
        avg_bit_len = numpy.mean([m.samples_per_bit for m in self.modulators])
        avg_sample_rate = numpy.mean([m.sample_rate for m in self.modulators])
        pause_samples = sum(c.pauses)
        nsamples = c.num_blocks * avg_block_len * avg_bit_len + pause_samples

        self.ui.lEstimatedTime.setText(locale.format_string("Estimated Time: %.04f seconds", nsamples / avg_sample_rate))

    @pyqtSlot(int, int, int)
    def create_fuzzing_label(self, refblock: int, start: int, end: int):
        con = self.table_model.protocol
        start, end = con.convert_range(start, end - 1, self.ui.cbViewType.currentIndex(), 0, False, refblock)
        lbl = con.create_fuzzing_label(start, end, refblock)
        self.show_fuzzing_dialog(con.protocol_labels.index(lbl))

    @pyqtSlot()
    def handle_label_selection_changed(self):
        rows = [index.row() for index in self.ui.listViewProtoLabels.selectedIndexes()]
        if len(rows) == 0:
            return

        maxrow = numpy.max(rows)

        label = self.table_model.protocol.protocol_labels[maxrow]
        if not label.show:
            return
        start, end = self.table_model.protocol.get_label_range(label, self.table_model.proto_view,
                                                                               False)

        # start = int(label.start / factor)
        # end = math.ceil(label.end / factor)
        indx = self.table_model.index(0, int((start + end) / 2))

        self.ui.tableBlocks.scrollTo(indx)

    @pyqtSlot()
    def on_view_type_changed(self):
        self.table_model.proto_view = self.ui.cbViewType.currentIndex()
        self.table_model.update()
        self.ui.tableBlocks.resize_columns()

    def refresh_protocol_labels(self):
        self.table_model.protocol.refresh_protolabel_blocks()

    def close_all(self):
        self.tree_model.rootItem.clearChilds()
        self.tree_model.rootItem.addGroup()
        self.table_model.protocol.clear()
        self.table_model.clear()
        self.refresh_tree()
        self.refresh_table()
        self.refresh_label_list()

    @pyqtSlot()
    def on_btn_send_clicked(self):
        modulated_data = self.modulate_data()
        dialog = SendRecvDialogController(self.project_manager.frequency,
                                          self.project_manager.sample_rate,
                                          self.project_manager.bandwidth,
                                          self.project_manager.gain,
                                          self.project_manager.device,
                                          Mode.send, modulated_data=modulated_data,
                                          parent=self)
        if dialog.has_empty_device_list:
            Errors.no_device()
            dialog.close()
            return

        dialog.recording_parameters.connect(self.project_manager.set_recording_parameters)
        dialog.show()


    @pyqtSlot()
    def on_btn_save_clicked(self):
        filename = FileOperator.get_save_file_name("profile", parent=self, caption="Save fuzz profile")
        if filename:
            self.table_model.protocol.to_xml_file(filename)

    def load_from_file(self, filename: str):
        try:
            self.table_model.protocol.from_xml_file(filename)
            self.refresh_pause_list()
            self.refresh_estimated_time()
            self.refresh_modulators()
            self.show_modulation_info()
            self.refresh_protocol_labels()
            self.refresh_table()
            self.set_fuzzing_ui_status()
        except:
            logger.error("You done something wrong to the xml fuzzing profile.")