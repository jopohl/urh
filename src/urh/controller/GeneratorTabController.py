import locale
import traceback

import numpy
import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QInputDialog, QWidget, QUndoStack, QApplication

from urh import constants
from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.dialogs.ContinuousSendDialog import ContinuousSendDialog
from urh.controller.dialogs.FuzzingDialog import FuzzingDialog
from urh.controller.dialogs.ModulatorDialog import ModulatorDialog
from urh.controller.dialogs.SendDialog import SendDialog
from urh.models.GeneratorListModel import GeneratorListModel
from urh.models.GeneratorTableModel import GeneratorTableModel
from urh.models.GeneratorTreeModel import GeneratorTreeModel
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.plugins.PluginManager import PluginManager
from urh.plugins.RfCat.RfCatPlugin import RfCatPlugin
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.ui.actions.Fuzz import Fuzz
from urh.ui.ui_generator import Ui_GeneratorTab
from urh.util import FileOperator, util
from urh.util.Errors import Errors
from urh.util.Formatter import Formatter
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class GeneratorTabController(QWidget):
    def __init__(self, compare_frame_controller: CompareFrameController, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.ui = Ui_GeneratorTab()
        self.ui.setupUi(self)
        util.set_splitter_stylesheet(self.ui.splitter)

        self.project_manager = project_manager

        self.ui.treeProtocols.setHeaderHidden(True)
        self.tree_model = GeneratorTreeModel(compare_frame_controller)
        self.tree_model.set_root_item(compare_frame_controller.proto_tree_model.rootItem)
        self.tree_model.controller = self
        self.ui.treeProtocols.setModel(self.tree_model)

        self.table_model = GeneratorTableModel(compare_frame_controller.proto_tree_model.rootItem,
                                               compare_frame_controller.decodings)
        self.table_model.controller = self
        self.ui.tableMessages.setModel(self.table_model)

        self.label_list_model = GeneratorListModel(None)
        self.ui.listViewProtoLabels.setModel(self.label_list_model)

        self.network_sdr_button_orig_tooltip = self.ui.btnNetworkSDRSend.toolTip()
        self.set_network_sdr_send_button_visibility()
        self.set_rfcat_button_visibility()
        self.network_sdr_plugin = NetworkSDRInterfacePlugin()
        self.rfcat_plugin = RfCatPlugin()
        self.init_rfcat_plugin()

        self.modulation_msg_indices = []

        self.refresh_modulators()
        self.on_selected_modulation_changed()
        self.set_fuzzing_ui_status()
        self.ui.prBarGeneration.hide()
        self.create_connects(compare_frame_controller)

        self.set_modulation_profile_status()

    def __get_modulator_of_message(self, message: Message) -> Modulator:
        if message.modulator_index > len(self.modulators) - 1:
            message.modulator_index = 0
        return self.modulators[message.modulator_index]

    @property
    def selected_message_index(self) -> int:
        min_row, _, _, _ = self.ui.tableMessages.selection_range()
        return min_row  #

    @property
    def selected_message(self) -> Message:
        selected_msg_index = self.selected_message_index
        if selected_msg_index == -1 or selected_msg_index >= len(self.table_model.protocol.messages):
            return None

        return self.table_model.protocol.messages[selected_msg_index]

    @property
    def active_groups(self):
        return self.tree_model.groups

    @property
    def modulators(self):
        return self.project_manager.modulators

    @property
    def total_modulated_samples(self) -> int:
        return sum(int(len(msg.encoded_bits) * self.__get_modulator_of_message(msg).samples_per_bit + msg.pause)
                   for msg in self.table_model.protocol.messages)

    @modulators.setter
    def modulators(self, value):
        assert type(value) == list
        self.project_manager.modulators = value

    def create_connects(self, compare_frame_controller):
        compare_frame_controller.proto_tree_model.modelReset.connect(self.refresh_tree)
        compare_frame_controller.participant_changed.connect(self.table_model.refresh_vertical_header)
        self.ui.btnEditModulation.clicked.connect(self.show_modulation_dialog)
        self.ui.cBoxModulations.currentIndexChanged.connect(self.on_selected_modulation_changed)
        self.ui.tableMessages.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        self.ui.tableMessages.encodings_updated.connect(self.on_table_selection_changed)
        self.table_model.undo_stack.indexChanged.connect(self.on_undo_stack_index_changed)
        self.table_model.protocol.qt_signals.line_duplicated.connect(self.refresh_pause_list)
        self.table_model.protocol.qt_signals.fuzzing_started.connect(self.on_fuzzing_started)
        self.table_model.protocol.qt_signals.current_fuzzing_message_changed.connect(
            self.on_current_fuzzing_message_changed)
        self.table_model.protocol.qt_signals.fuzzing_finished.connect(self.on_fuzzing_finished)
        self.table_model.first_protocol_added.connect(self.on_first_protocol_added)
        self.label_list_model.protolabel_fuzzing_status_changed.connect(self.set_fuzzing_ui_status)
        self.ui.cbViewType.currentIndexChanged.connect(self.on_view_type_changed)
        self.ui.btnSend.clicked.connect(self.on_btn_send_clicked)
        self.ui.btnSave.clicked.connect(self.on_btn_save_clicked)
        self.ui.btnOpen.clicked.connect(self.on_btn_open_clicked)

        self.project_manager.project_updated.connect(self.on_project_updated)

        self.table_model.vertical_header_color_status_changed.connect(
            self.ui.tableMessages.on_vertical_header_color_status_changed)

        self.label_list_model.protolabel_removed.connect(self.handle_proto_label_removed)

        self.ui.lWPauses.item_edit_clicked.connect(self.edit_pause_item)
        self.ui.lWPauses.edit_all_items_clicked.connect(self.edit_all_pause_items)
        self.ui.lWPauses.itemSelectionChanged.connect(self.on_lWpauses_selection_changed)
        self.ui.lWPauses.lost_focus.connect(self.on_lWPauses_lost_focus)
        self.ui.lWPauses.doubleClicked.connect(self.on_lWPauses_double_clicked)
        self.ui.btnGenerate.clicked.connect(self.generate_file)
        self.label_list_model.protolabel_fuzzing_status_changed.connect(self.handle_plabel_fuzzing_state_changed)
        self.ui.btnFuzz.clicked.connect(self.on_btn_fuzzing_clicked)
        self.ui.tableMessages.create_fuzzing_label_clicked.connect(self.create_fuzzing_label)
        self.ui.tableMessages.edit_fuzzing_label_clicked.connect(self.show_fuzzing_dialog)
        self.ui.listViewProtoLabels.selection_changed.connect(self.handle_label_selection_changed)
        self.ui.listViewProtoLabels.edit_on_item_triggered.connect(self.show_fuzzing_dialog)

        self.ui.btnNetworkSDRSend.clicked.connect(self.on_btn_network_sdr_clicked)
        self.ui.btnRfCatSend.clicked.connect(self.on_btn_rfcat_clicked)

        self.network_sdr_plugin.sending_status_changed.connect(self.on_network_sdr_sending_status_changed)
        self.network_sdr_plugin.sending_stop_requested.connect(self.on_network_sdr_sending_stop_requested)
        self.network_sdr_plugin.current_send_message_changed.connect(self.on_send_message_changed)

    @pyqtSlot()
    def refresh_tree(self):
        self.tree_model.beginResetModel()
        self.tree_model.endResetModel()
        self.ui.treeProtocols.expandAll()

    @pyqtSlot()
    def refresh_table(self):
        self.table_model.update()
        self.ui.tableMessages.resize_columns()
        is_data_there = self.table_model.display_data is not None and len(self.table_model.display_data) > 0
        self.ui.btnSend.setEnabled(is_data_there)
        self.ui.btnGenerate.setEnabled(is_data_there)

    @pyqtSlot()
    def refresh_label_list(self):
        self.label_list_model.message = self.selected_message
        self.label_list_model.update()

    @property
    def generator_undo_stack(self) -> QUndoStack:
        return self.table_model.undo_stack

    @pyqtSlot()
    def on_selected_modulation_changed(self):
        cur_ind = self.ui.cBoxModulations.currentIndex()
        min_row, max_row, _, _ = self.ui.tableMessages.selection_range()
        if min_row > -1:
            # set modulation for selected messages
            for row in range(min_row, max_row + 1):
                try:
                    self.table_model.protocol.messages[row].modulator_index = cur_ind
                except IndexError:
                    continue

        self.show_modulation_info()

    def refresh_modulators(self):
        current_index = 0
        if type(self.sender()) == ModulatorDialog:
            current_index = self.sender().ui.comboBoxCustomModulations.currentIndex()
        self.ui.cBoxModulations.clear()
        for modulator in self.modulators:
            self.ui.cBoxModulations.addItem(modulator.name)

        self.ui.cBoxModulations.setCurrentIndex(current_index)

    def bootstrap_modulator(self, protocol: ProtocolAnalyzer):
        """
        Set initial parameters for default modulator if it was not edited by user previously
        :return:
        """
        if len(self.modulators) != 1 or len(self.table_model.protocol.messages) == 0:
            return

        modulator = self.modulators[0]
        modulator.samples_per_bit = protocol.messages[0].bit_len

        if protocol.signal:
            modulator.sample_rate = protocol.signal.sample_rate
            modulator.modulation_type = protocol.signal.modulation_type
            auto_freq = modulator.estimate_carrier_frequency(protocol.signal, protocol)
            if auto_freq is not None and auto_freq != 0:
                modulator.carrier_freq_hz = auto_freq

        self.show_modulation_info()

    def show_modulation_info(self):
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

    def prepare_modulation_dialog(self) -> (ModulatorDialog, Message):
        preselected_index = self.ui.cBoxModulations.currentIndex()

        min_row, max_row, start, end = self.ui.tableMessages.selection_range()
        if min_row > -1:
            try:
                selected_message = self.table_model.protocol.messages[min_row]
                preselected_index = selected_message.modulator_index
            except IndexError:
                selected_message = Message([1, 0, 1, 0, 1, 0, 1, 0], 0, [], MessageType("empty"))
        else:
            selected_message = Message([1, 0, 1, 0, 1, 0, 1, 0], 0, [], MessageType("empty"))
            if len(self.table_model.protocol.messages) > 0:
                selected_message.bit_len = self.table_model.protocol.messages[0].bit_len

        for m in self.modulators:
            m.default_sample_rate = self.project_manager.device_conf["sample_rate"]

        modulator_dialog = ModulatorDialog(self.modulators, tree_model=self.tree_model, parent=self.parent())
        modulator_dialog.ui.comboBoxCustomModulations.setCurrentIndex(preselected_index)

        modulator_dialog.finished.connect(self.refresh_modulators)
        modulator_dialog.finished.connect(self.refresh_pause_list)

        return modulator_dialog, selected_message

    def set_modulation_profile_status(self):
        visible = constants.SETTINGS.value("multiple_modulations", False, bool)
        self.ui.cBoxModulations.setVisible(visible)

    def init_rfcat_plugin(self):
        self.set_rfcat_button_visibility()
        self.rfcat_plugin = RfCatPlugin()
        self.rfcat_plugin.current_send_message_changed.connect(self.on_send_message_changed)
        self.ui.btnRfCatSend.setEnabled(self.rfcat_plugin.rfcat_is_found)

    @pyqtSlot()
    def on_undo_stack_index_changed(self):
        self.refresh_table()
        self.refresh_pause_list()
        self.refresh_label_list()
        self.refresh_estimated_time()
        self.set_fuzzing_ui_status()

    @pyqtSlot()
    def show_modulation_dialog(self):
        modulator_dialog, message = self.prepare_modulation_dialog()
        modulator_dialog.showMaximized()

        modulator_dialog.initialize(message.encoded_bits_str[0:10])
        self.project_manager.modulation_was_edited = True

    @pyqtSlot()
    def on_table_selection_changed(self):
        min_row, max_row, start, end = self.ui.tableMessages.selection_range()

        if min_row == -1:
            self.ui.lEncodingValue.setText("-")  #
            self.ui.lEncodingValue.setToolTip("")
            self.label_list_model.message = None
            return

        container = self.table_model.protocol
        message = container.messages[min_row]
        self.label_list_model.message = message
        decoder_name = message.decoder.name
        metrics = QFontMetrics(self.ui.lEncodingValue.font())
        elidedName = metrics.elidedText(decoder_name, Qt.ElideRight, self.ui.lEncodingValue.width())
        self.ui.lEncodingValue.setText(elidedName)
        self.ui.lEncodingValue.setToolTip(decoder_name)
        self.ui.cBoxModulations.blockSignals(True)
        self.ui.cBoxModulations.setCurrentIndex(message.modulator_index)
        self.show_modulation_info()
        self.ui.cBoxModulations.blockSignals(False)

    @pyqtSlot(int)
    def edit_pause_item(self, index: int):
        message = self.table_model.protocol.messages[index]
        cur_len = message.pause
        new_len, ok = QInputDialog.getInt(self, self.tr("Enter new Pause Length"),
                                          self.tr("Pause Length:"), cur_len, 0)
        if ok:
            message.pause = new_len
            self.refresh_pause_list()

    @pyqtSlot()
    def edit_all_pause_items(self):
        message = self.table_model.protocol.messages[0]
        cur_len = message.pause
        new_len, ok = QInputDialog.getInt(self, self.tr("Enter new Pause Length"),
                                          self.tr("Pause Length:"), cur_len, 0)
        if ok:
            for message in self.table_model.protocol.messages:
                message.pause = new_len

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
            sr = self.__get_modulator_of_message(self.table_model.protocol.messages[i]).sample_rate
            item = fmt_str.format(pause, i + 1, i + 2, Formatter.science_time(pause / sr))
            self.ui.lWPauses.addItem(item)

        self.refresh_estimated_time()

    @pyqtSlot()
    def on_lWpauses_selection_changed(self):
        rows = [index.row() for index in self.ui.lWPauses.selectedIndexes()]
        if len(rows) == 0:
            return
        self.ui.tableMessages.show_pause_active = True
        self.ui.tableMessages.pause_row = rows[0]
        self.ui.tableMessages.viewport().update()
        self.ui.tableMessages.scrollTo(self.table_model.index(rows[0], 0))

    @pyqtSlot()
    def on_lWPauses_lost_focus(self):
        self.ui.tableMessages.show_pause_active = False
        self.ui.tableMessages.viewport().update()

    @pyqtSlot()
    def generate_file(self):
        try:
            total_samples = self.total_modulated_samples
            buffer = self.prepare_modulation_buffer(total_samples, show_error=False)
            if buffer is None:
                Errors.generic_error(self.tr("File too big"), self.tr("This file would get too big to save."))
                self.unsetCursor()
                return
            modulated_samples = self.modulate_data(buffer)
            try:
                sample_rate = self.modulators[0].sample_rate
            except Exception as e:
                logger.exception(e)
                sample_rate = 1e6
            FileOperator.save_data_dialog("generated.complex", modulated_samples, sample_rate=sample_rate, parent=self)
        except Exception as e:
            Errors.generic_error(self.tr("Failed to generate data"), str(e), traceback.format_exc())
            self.unsetCursor()

    def prepare_modulation_buffer(self, total_samples: int, show_error=True) -> np.ndarray:
        memory_size_for_buffer = total_samples * 8
        logger.debug("Allocating {0:.2f}MB for modulated samples".format(memory_size_for_buffer / (1024 ** 2)))
        try:
            # allocate it three times as we need the same amount for the sending process
            np.zeros(3*total_samples, dtype=np.complex64)
        except MemoryError:
            # will go into continuous mode in this case
            if show_error:
                Errors.not_enough_ram_for_sending_precache(3*memory_size_for_buffer)
            return None

        return np.zeros(total_samples, dtype=np.complex64)

    def modulate_data(self, buffer: np.ndarray) -> np.ndarray:
        """
        
        :param buffer: Buffer in which the modulated data shall be written, initialized with zeros
        :return: 
        """
        self.ui.prBarGeneration.show()
        self.ui.prBarGeneration.setValue(0)
        self.ui.prBarGeneration.setMaximum(self.table_model.row_count)
        self.modulation_msg_indices.clear()

        pos = 0
        for i in range(0, self.table_model.row_count):
            message = self.table_model.protocol.messages[i]
            modulator = self.__get_modulator_of_message(message)
            # We do not need to modulate the pause extra, as result is already initialized with zeros
            modulated = modulator.modulate(start=0, data=message.encoded_bits, pause=0)
            buffer[pos:pos + len(modulated)] = modulated
            pos += len(modulated) + message.pause
            self.modulation_msg_indices.append(pos)
            self.ui.prBarGeneration.setValue(i + 1)
            QApplication.instance().processEvents()

        self.ui.prBarGeneration.hide()
        return buffer

    @pyqtSlot(int)
    def show_fuzzing_dialog(self, label_index: int):
        view = self.ui.cbViewType.currentIndex()

        if self.label_list_model.message is not None:
            msg_index = self.table_model.protocol.messages.index(self.label_list_model.message)
            fdc = FuzzingDialog(protocol=self.table_model.protocol, label_index=label_index,
                                msg_index=msg_index, proto_view=view, parent=self)
            fdc.show()
            fdc.finished.connect(self.refresh_label_list)
            fdc.finished.connect(self.refresh_table)
            fdc.finished.connect(self.set_fuzzing_ui_status)

    @pyqtSlot()
    def handle_plabel_fuzzing_state_changed(self):
        self.refresh_table()
        self.label_list_model.update()

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

        self.setCursor(Qt.WaitCursor)
        fuzz_action = Fuzz(self.table_model.protocol, fuz_mode)
        self.table_model.undo_stack.push(fuzz_action)
        for row in fuzz_action.added_message_indices:
            self.table_model.update_checksums_for_row(row)
        self.unsetCursor()
        self.ui.tableMessages.setFocus()

    @pyqtSlot()
    def set_fuzzing_ui_status(self):
        btn_was_enabled = self.ui.btnFuzz.isEnabled()
        fuzz_active = any(lbl.active_fuzzing for msg in self.table_model.protocol.messages for lbl in msg.message_type)
        self.ui.btnFuzz.setEnabled(fuzz_active)
        if self.ui.btnFuzz.isEnabled() and not btn_was_enabled:
            font = self.ui.btnFuzz.font()
            font.setBold(True)
            self.ui.btnFuzz.setFont(font)
        else:
            font = self.ui.btnFuzz.font()
            font.setBold(False)
            self.ui.btnFuzz.setFont(font)
            self.ui.btnFuzz.setStyleSheet("")

        has_same_message = self.table_model.protocol.multiple_fuzz_labels_per_message
        self.ui.rBSuccessive.setEnabled(has_same_message)
        self.ui.rBExhaustive.setEnabled(has_same_message)
        self.ui.rbConcurrent.setEnabled(has_same_message)

    def refresh_existing_encodings(self, encodings_from_file):
        """
        Refresh existing encodings for messages, when encoding was changed by user in dialog

        :return:
        """
        update = False

        for msg in self.table_model.protocol.messages:
            i = next((i for i, d in enumerate(encodings_from_file) if d.name == msg.decoder.name), 0)
            if msg.decoder != encodings_from_file[i]:
                update = True
                msg.decoder = encodings_from_file[i]
                msg.clear_decoded_bits()
                msg.clear_encoded_bits()

        if update:
            self.refresh_table()
            self.refresh_estimated_time()

    @pyqtSlot()
    def refresh_estimated_time(self):
        c = self.table_model.protocol
        if c.num_messages == 0:
            self.ui.lEstimatedTime.setText("Estimated Time: ")
            return

        avg_msg_len = numpy.mean([len(msg.encoded_bits) for msg in c.messages])
        avg_bit_len = numpy.mean([m.samples_per_bit for m in self.modulators])
        avg_sample_rate = numpy.mean([m.sample_rate for m in self.modulators])
        pause_samples = sum(c.pauses)
        nsamples = c.num_messages * avg_msg_len * avg_bit_len + pause_samples

        self.ui.lEstimatedTime.setText(
            locale.format_string("Estimated Time: %.04f seconds", nsamples / avg_sample_rate))

    @pyqtSlot(int, int, int)
    def create_fuzzing_label(self, msg_index: int, start: int, end: int):
        con = self.table_model.protocol
        start, end = con.convert_range(start, end - 1, self.ui.cbViewType.currentIndex(), 0, False, msg_index)
        lbl = con.create_fuzzing_label(start, end, msg_index)
        self.show_fuzzing_dialog(con.protocol_labels.index(lbl))

    @pyqtSlot()
    def handle_label_selection_changed(self):
        rows = [index.row() for index in self.ui.listViewProtoLabels.selectedIndexes()]
        if len(rows) == 0:
            return

        maxrow = numpy.max(rows)

        try:
            label = self.table_model.protocol.protocol_labels[maxrow]
        except IndexError:
            return
        if label.show and self.selected_message:
            start, end = self.selected_message.get_label_range(lbl=label, view=self.table_model.proto_view,
                                                               decode=False)
            indx = self.table_model.index(0, int((start + end) / 2))
            self.ui.tableMessages.scrollTo(indx)

    @pyqtSlot()
    def on_view_type_changed(self):
        self.setCursor(Qt.WaitCursor)
        self.table_model.proto_view = self.ui.cbViewType.currentIndex()
        self.ui.tableMessages.resize_columns()
        self.unsetCursor()

    @pyqtSlot()
    def on_btn_send_clicked(self):
        try:
            total_samples = self.total_modulated_samples
            buffer = self.prepare_modulation_buffer(total_samples)
            if buffer is not None:
                modulated_data = self.modulate_data(buffer)
            else:
                # Enter continuous mode
                modulated_data = None

            try:
                if modulated_data is not None:
                    try:
                        dialog = SendDialog(self.project_manager, modulated_data=modulated_data,
                                            modulation_msg_indices=self.modulation_msg_indices, parent=self)
                    except MemoryError:
                        # Not enough memory for device buffer so we need to create a continuous send dialog
                        del modulated_data
                        Errors.not_enough_ram_for_sending_precache(None)
                        dialog = ContinuousSendDialog(self.project_manager,
                                                      self.table_model.protocol.messages,
                                                      self.modulators, total_samples, parent=self)
                else:
                    dialog = ContinuousSendDialog(self.project_manager, self.table_model.protocol.messages,
                                                  self.modulators, total_samples, parent=self)
            except OSError as e:
                logger.exception(e)
                return
            if dialog.has_empty_device_list:
                Errors.no_device()
                dialog.close()
                return

            dialog.device_parameters_changed.connect(self.project_manager.set_device_parameters)
            dialog.show()
            dialog.graphics_view.show_full_scene(reinitialize=True)
        except Exception as e:
            Errors.generic_error(self.tr("Failed to generate data"), str(e), traceback.format_exc())
            self.unsetCursor()

    @pyqtSlot()
    def on_btn_save_clicked(self):
        filename = FileOperator.get_save_file_name("profile.fuzz.xml", caption="Save fuzz profile")
        if filename:
            self.table_model.protocol.to_xml_file(filename,
                                                  decoders=self.project_manager.decodings,
                                                  participants=self.project_manager.participants,
                                                  modulators=self.modulators)

    @pyqtSlot()
    def on_btn_open_clicked(self):
        dialog = FileOperator.get_open_dialog(directory_mode=False, parent=self, name_filter="fuzz")
        if dialog.exec_():
            for filename in dialog.selectedFiles():
                self.load_from_file(filename)

    def load_from_file(self, filename: str):
        try:
            self.modulators = ProjectManager.read_modulators_from_file(filename)
            self.table_model.protocol.from_xml_file(filename)
            self.refresh_pause_list()
            self.refresh_estimated_time()
            self.refresh_modulators()
            self.show_modulation_info()
            self.refresh_table()
            self.set_fuzzing_ui_status()
        except:
            logger.error("You done something wrong to the xml fuzzing profile.")

    @pyqtSlot()
    def on_project_updated(self):
        self.table_model.refresh_vertical_header()

    def set_network_sdr_send_button_visibility(self):
        is_plugin_enabled = PluginManager().is_plugin_enabled("NetworkSDRInterface")
        self.ui.btnNetworkSDRSend.setVisible(is_plugin_enabled)

    def set_rfcat_button_visibility(self):
        is_plugin_enabled = PluginManager().is_plugin_enabled("RfCat")
        self.ui.btnRfCatSend.setVisible(is_plugin_enabled)

    @pyqtSlot()
    def on_btn_network_sdr_clicked(self):
        if not self.network_sdr_plugin.is_sending:
            messages = self.table_model.protocol.messages
            sample_rates = [self.__get_modulator_of_message(msg).sample_rate for msg in messages]
            self.network_sdr_plugin.start_message_sending_thread(messages, sample_rates)
        else:
            self.network_sdr_plugin.stop_sending_thread()

    @pyqtSlot(bool)
    def on_network_sdr_sending_status_changed(self, is_sending: bool):
        self.ui.btnNetworkSDRSend.setChecked(is_sending)
        self.ui.btnNetworkSDRSend.setEnabled(True)
        self.ui.btnNetworkSDRSend.setToolTip(
            "Sending in progress" if is_sending else self.network_sdr_button_orig_tooltip)
        if not is_sending:
            self.ui.tableMessages.clearSelection()

    @pyqtSlot()
    def on_network_sdr_sending_stop_requested(self):
        self.ui.btnNetworkSDRSend.setToolTip("Stopping sending")
        self.ui.btnNetworkSDRSend.setEnabled(False)

    @pyqtSlot(int)
    def on_send_message_changed(self, message_index: int):
        self.ui.tableMessages.selectRow(message_index)

    @pyqtSlot()
    def on_btn_rfcat_clicked(self):
        if not self.rfcat_plugin.is_sending:
            messages = self.table_model.protocol.messages
            sample_rates = [self.__get_modulator_of_message(msg).sample_rate for msg in messages]
            self.rfcat_plugin.start_message_sending_thread(messages, sample_rates, self.modulators,
                                                           self.project_manager)
        else:
            self.rfcat_plugin.stop_sending_thread()

    @pyqtSlot(int)
    def on_fuzzing_started(self, num_values: int):
        self.ui.stackedWidgetFuzzing.setCurrentWidget(self.ui.pageFuzzingProgressBar)
        self.ui.progressBarFuzzing.setMaximum(num_values)
        self.ui.progressBarFuzzing.setValue(0)
        QApplication.instance().processEvents()

    @pyqtSlot()
    def on_fuzzing_finished(self):
        self.ui.stackedWidgetFuzzing.setCurrentWidget(self.ui.pageFuzzingUI)
        # Calculate Checksums for Fuzzed Messages
        self.setCursor(Qt.WaitCursor)

        self.unsetCursor()

    @pyqtSlot(int)
    def on_current_fuzzing_message_changed(self, current_message: int):
        self.ui.progressBarFuzzing.setValue(current_message)
        QApplication.instance().processEvents()

    @pyqtSlot(ProtocolAnalyzer)
    def on_first_protocol_added(self, protocol: ProtocolAnalyzer):
        if not self.project_manager.modulation_was_edited:
            self.bootstrap_modulator(protocol)
