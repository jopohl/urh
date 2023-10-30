from array import array

import numpy
from PyQt5.QtCore import Qt, pyqtSlot, QRegExp, QTimer
from PyQt5.QtGui import QCloseEvent, QResizeEvent, QKeyEvent, QIcon, QRegExpValidator
from PyQt5.QtWidgets import QDialog, QMessageBox, QLineEdit

from urh import settings
from urh.controller.dialogs.ModulationParametersDialog import ModulationParametersDialog
from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.ui.ui_modulation import Ui_DialogModulation
from urh.util.Logger import logger


class ModulatorDialog(QDialog):
    def __init__(self, modulators, tree_model=None, parent=None):
        """
        :type modulators: list of Modulator
        """
        super().__init__(parent)

        self.ui = Ui_DialogModulation()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window)

        self.lock_samples_in_view = False

        if tree_model is not None:
            self.ui.treeViewSignals.setModel(tree_model)
            self.ui.treeViewSignals.expandAll()
            self.ui.gVOriginalSignal.signal_tree_root = tree_model.rootItem

        self.ui.comboBoxCustomModulations.clear()
        for modulator in modulators:
            self.ui.comboBoxCustomModulations.addItem(modulator.name)
        if len(modulators) == 1:
            self.ui.btnRemoveModulation.setDisabled(True)

        self.modulators = modulators

        self.set_ui_for_current_modulator()

        self.ui.cbShowDataBitsOnly.setText(self.tr("Show Only Data Sequence\n"))
        self.ui.cbShowDataBitsOnly.setEnabled(False)
        self.protocol = None  # type: ProtocolAnalyzer
        self.search_results = []
        self.ui.cbShowDataBitsOnly.setEnabled(False)
        self.ui.btnSearchNext.setEnabled(False)
        self.ui.btnSearchPrev.setEnabled(False)

        self.ui.chkBoxLockSIV.setDisabled(True)

        self.original_bits = ""

        self.restore_bits_action = self.ui.linEdDataBits.addAction(
            QIcon.fromTheme("edit-undo"), QLineEdit.TrailingPosition
        )
        self.restore_bits_action.setEnabled(False)

        self.configure_parameters_action = self.ui.lineEditParameters.addAction(
            QIcon.fromTheme("configure"), QLineEdit.TrailingPosition
        )

        self.create_connects()
        self.restoreGeometry(
            settings.read("{}/geometry".format(self.__class__.__name__), type=bytes)
        )

        self.set_bits_per_symbol_enabled_status()
        self.set_modulation_profile_status()

        # Ensure full screen is shown after resize
        QTimer.singleShot(100, self.show_full_scene)

    def __cur_selected_mod_type(self):
        s = self.ui.comboBoxModulationType.currentText()
        return s[s.rindex("(") + 1 : s.rindex(")")]

    @staticmethod
    def __trim_number(number):
        if abs(number) >= 1e9:  # giga
            return numpy.round(number / 1e9) * 1e9
        elif abs(number) >= 1e6:  # mega
            return numpy.round(number / 1e6) * 1e6
        elif abs(number) >= 1e3:  # Kilo
            return numpy.round(number / 1e3) * 1e3
        else:
            return number

    @staticmethod
    def __ensure_multitude(num1, num2):
        try:
            if abs(num1) > abs(num2):
                num1 = abs(int(num1 / num2)) * num2
            else:
                num2 = abs(int(num2 / num1)) * num1
            return num1, num2
        except Exception:
            return num1, num2

    def __set_gauss_ui_visibility(self, show: bool):
        self.ui.lGaussBT.setVisible(show)
        self.ui.lGaussWidth.setVisible(show)
        self.ui.spinBoxGaussBT.setVisible(show)
        self.ui.spinBoxGaussFilterWidth.setVisible(show)

        self.ui.spinBoxGaussFilterWidth.setValue(
            self.current_modulator.gauss_filter_width
        )
        self.ui.spinBoxGaussBT.setValue(self.current_modulator.gauss_bt)

    def closeEvent(self, event: QCloseEvent):
        self.ui.lineEditParameters.editingFinished.emit()
        settings.write(
            "{}/geometry".format(self.__class__.__name__), self.saveGeometry()
        )

        for gv in (
            self.ui.gVCarrier,
            self.ui.gVData,
            self.ui.gVModulated,
            self.ui.gVOriginalSignal,
        ):
            # Eliminate graphic views to prevent segfaults
            gv.eliminate()

        super().closeEvent(event)

    @property
    def current_modulator(self):
        return self.modulators[self.ui.comboBoxCustomModulations.currentIndex()]

    def set_ui_for_current_modulator(self):
        index = self.ui.comboBoxModulationType.findText(
            "*(" + self.current_modulator.modulation_type + ")", Qt.MatchWildcard
        )
        self.ui.comboBoxModulationType.setCurrentIndex(index)
        self.ui.doubleSpinBoxCarrierFreq.setValue(
            self.current_modulator.carrier_freq_hz
        )
        self.ui.doubleSpinBoxCarrierPhase.setValue(
            self.current_modulator.carrier_phase_deg
        )
        self.ui.spinBoxSamplesPerSymbol.setValue(
            self.current_modulator.samples_per_symbol
        )
        self.ui.spinBoxSampleRate.setValue(self.current_modulator.sample_rate)
        self.ui.spinBoxBitsPerSymbol.setValue(self.current_modulator.bits_per_symbol)

        self.update_modulation_parameters()

    def create_connects(self):
        self.ui.doubleSpinBoxCarrierFreq.valueChanged.connect(
            self.on_carrier_freq_changed
        )
        self.ui.doubleSpinBoxCarrierPhase.valueChanged.connect(
            self.on_carrier_phase_changed
        )
        self.ui.spinBoxSamplesPerSymbol.valueChanged.connect(
            self.on_samples_per_symbol_changed
        )
        self.ui.spinBoxSampleRate.valueChanged.connect(self.on_sample_rate_changed)
        self.ui.linEdDataBits.textChanged.connect(self.on_data_bits_changed)
        self.ui.spinBoxBitsPerSymbol.valueChanged.connect(
            self.on_bits_per_symbol_changed
        )
        self.ui.comboBoxModulationType.currentIndexChanged.connect(
            self.on_modulation_type_changed
        )
        self.ui.gVOriginalSignal.zoomed.connect(self.on_orig_signal_zoomed)
        self.ui.cbShowDataBitsOnly.stateChanged.connect(
            self.on_show_data_bits_only_changed
        )
        self.ui.btnSearchNext.clicked.connect(self.on_btn_next_search_result_clicked)
        self.ui.btnSearchPrev.clicked.connect(self.on_btn_prev_search_result_clicked)
        self.ui.comboBoxCustomModulations.editTextChanged.connect(
            self.on_custom_modulation_name_edited
        )
        self.ui.comboBoxCustomModulations.currentIndexChanged.connect(
            self.on_custom_modulation_index_changed
        )
        self.ui.btnAddModulation.clicked.connect(self.add_modulator)
        self.ui.btnRemoveModulation.clicked.connect(self.on_remove_modulator_clicked)
        self.ui.gVModulated.zoomed.connect(self.on_carrier_data_modulated_zoomed)
        self.ui.gVCarrier.zoomed.connect(self.on_carrier_data_modulated_zoomed)
        self.ui.gVData.zoomed.connect(self.on_carrier_data_modulated_zoomed)
        self.ui.gVModulated.selection_width_changed.connect(
            self.on_modulated_selection_changed
        )
        self.ui.gVOriginalSignal.selection_width_changed.connect(
            self.on_original_selection_changed
        )
        self.ui.spinBoxGaussBT.valueChanged.connect(self.on_gauss_bt_changed)
        self.ui.spinBoxGaussFilterWidth.valueChanged.connect(
            self.on_gauss_filter_width_changed
        )

        self.ui.chkBoxLockSIV.stateChanged.connect(self.on_lock_siv_changed)

        self.ui.gVOriginalSignal.signal_loaded.connect(self.handle_signal_loaded)
        self.ui.btnAutoDetect.clicked.connect(self.on_btn_autodetect_clicked)

        self.restore_bits_action.triggered.connect(
            self.on_restore_bits_action_triggered
        )
        self.configure_parameters_action.triggered.connect(
            self.on_configure_parameters_action_triggered
        )
        self.ui.lineEditParameters.editingFinished.connect(
            self.on_line_edit_parameters_editing_finished
        )

    def draw_carrier(self):
        self.ui.gVCarrier.plot_data(self.current_modulator.carrier_data)

    def draw_data_bits(self):
        self.ui.gVData.setScene(self.current_modulator.data_scene)
        self.ui.gVData.update()

    def draw_modulated(self):
        self.ui.gVModulated.plot_data(self.current_modulator.modulate(pause=0).imag)
        if self.lock_samples_in_view:
            siv = self.ui.gVOriginalSignal.view_rect().width()
            self.adjust_samples_in_view(siv)
        else:
            self.mark_samples_in_view()

    def draw_original_signal(self, start=0, end=-1):
        scene_manager = self.ui.gVOriginalSignal.scene_manager
        if scene_manager is None:
            return

        if end == -1:
            end = scene_manager.signal.num_samples

        y = self.ui.gVOriginalSignal.view_rect().y()
        h = self.ui.gVOriginalSignal.view_rect().height()
        self.ui.gVOriginalSignal.setSceneRect(start, y, end - start, h)
        self.ui.gVOriginalSignal.fitInView(self.ui.gVOriginalSignal.sceneRect())
        scene_manager.show_scene_section(start, end)
        self.ui.gVOriginalSignal.update()

        if self.lock_samples_in_view:
            self.adjust_samples_in_view(self.ui.gVModulated.view_rect().width())
        else:
            self.mark_samples_in_view()

    def update_views(self):
        self.ui.gVCarrier.update()
        self.ui.gVData.update()
        self.ui.gVModulated.update()
        self.ui.gVOriginalSignal.update()

    def search_data_sequence(self):
        if (
            not self.ui.cbShowDataBitsOnly.isEnabled()
            or not self.ui.cbShowDataBitsOnly.isChecked()
        ):
            return

        search_seq = self.ui.linEdDataBits.text()
        if len(search_seq) == 0 or self.protocol is None:
            return

        self.search_results[:] = []
        proto_bits = self.protocol.plain_bits_str
        len_seq = len(search_seq)

        for i, message in enumerate(proto_bits):
            j = message.find(search_seq)
            while j != -1:
                self.search_results.append((i, j, j + len_seq))
                j = message.find(search_seq, j + 1)

        self.ui.lTotalSearchresults.setText(str(len(self.search_results)))
        self.show_search_result(0)

    def show_search_result(self, i: int):
        if len(self.search_results) == 0:
            self.ui.lCurrentSearchResult.setText("0")
            self.ui.gVOriginalSignal.scene_manager.clear_path()
            return

        message, start_index, end_index = self.search_results[i]

        start, nsamples = self.protocol.get_samplepos_of_bitseq(
            message, start_index, message, end_index, False
        )
        self.draw_original_signal(start=start, end=start + nsamples)

        self.ui.lCurrentSearchResult.setText(str(i + 1))
        self.ui.btnSearchNext.setEnabled(i != len(self.search_results) - 1)
        self.ui.btnSearchPrev.setEnabled(i > 0)

    def add_modulator(self):
        names = [m.name for m in self.modulators]
        name = "Modulation"
        number = 1
        while name in names:
            name = "Modulation " + str(number)
            number += 1
        self.modulators.append(Modulator(name))
        self.ui.comboBoxCustomModulations.addItem(name)
        self.ui.comboBoxCustomModulations.setCurrentIndex(len(self.modulators) - 1)
        self.ui.btnRemoveModulation.setEnabled(True)

    def adjust_samples_in_view(self, target_siv: float):
        self.ui.gVOriginalSignal.scale(
            self.ui.gVOriginalSignal.view_rect().width() / target_siv, 1
        )
        mod_zoom_factor = self.ui.gVModulated.view_rect().width() / target_siv
        self.ui.gVModulated.scale(mod_zoom_factor, 1)
        self.ui.gVCarrier.scale(mod_zoom_factor, 1)
        self.ui.gVData.scale(mod_zoom_factor, 1)
        self.mark_samples_in_view()

    def detect_fsk_frequencies(self):
        if not self.current_modulator.is_frequency_based:
            return

        frequencies = []
        try:
            if not self.current_modulator.is_binary_modulation:
                raise NotImplementedError()

            zero_freq = self.protocol.estimate_frequency_for_zero(
                self.current_modulator.sample_rate
            )
            one_freq = self.protocol.estimate_frequency_for_one(
                self.current_modulator.sample_rate
            )
            zero_freq = self.__trim_number(zero_freq)
            one_freq = self.__trim_number(one_freq)
            zero_freq, one_freq = self.__ensure_multitude(zero_freq, one_freq)

            if zero_freq == one_freq:
                # If frequencies are equal, it is very likely the zero freq is negative
                zero_freq = -one_freq

            frequencies = [zero_freq, one_freq]

        except (AttributeError, NotImplementedError):
            frequencies = self.current_modulator.get_default_parameters()

        self.current_modulator.parameters = array("f", frequencies)
        self.update_modulation_parameters()

    def handle_signal_loaded(self, protocol):
        self.setCursor(Qt.WaitCursor)
        self.ui.cbShowDataBitsOnly.setEnabled(True)
        self.ui.chkBoxLockSIV.setEnabled(True)
        self.ui.btnAutoDetect.setEnabled(True)
        self.protocol = protocol

        # Apply bit length of original signal to current modulator
        self.ui.spinBoxSamplesPerSymbol.setValue(
            self.ui.gVOriginalSignal.signal.samples_per_symbol
        )

        # https://github.com/jopohl/urh/issues/130
        self.ui.gVModulated.show_full_scene(reinitialize=True)
        self.ui.gVCarrier.show_full_scene(reinitialize=True)
        self.ui.gVData.show_full_scene(reinitialize=True)

        self.unsetCursor()

    def mark_samples_in_view(self):
        self.ui.lSamplesInViewModulated.setText(
            str(int(self.ui.gVModulated.view_rect().width()))
        )

        if self.ui.gVOriginalSignal.scene_manager is not None:
            self.ui.lSamplesInViewOrigSignal.setText(
                str(int(self.ui.gVOriginalSignal.view_rect().width()))
            )
        else:
            self.ui.lSamplesInViewOrigSignal.setText("-")
            return

        if int(self.ui.gVOriginalSignal.view_rect().width()) != int(
            self.ui.gVModulated.view_rect().width()
        ):
            font = self.ui.lSamplesInViewModulated.font()
            font.setBold(False)
            self.ui.lSamplesInViewModulated.setFont(font)
            self.ui.lSamplesInViewOrigSignal.setFont(font)

            self.ui.lSamplesInViewOrigSignal.setStyleSheet("QLabel { color : red; }")
            self.ui.lSamplesInViewModulated.setStyleSheet("QLabel { color : red; }")
        else:
            font = self.ui.lSamplesInViewModulated.font()
            font.setBold(True)
            self.ui.lSamplesInViewModulated.setFont(font)
            self.ui.lSamplesInViewOrigSignal.setFont(font)

            self.ui.lSamplesInViewOrigSignal.setStyleSheet("")
            self.ui.lSamplesInViewModulated.setStyleSheet("")

    def set_default_modulation_parameters(self):
        self.current_modulator.parameters = (
            self.current_modulator.get_default_parameters()
        )
        self.update_modulation_parameters()

    def set_modulation_profile_status(self):
        visible = settings.read("multiple_modulations", False, bool)
        self.ui.btnAddModulation.setVisible(visible)
        self.ui.btnRemoveModulation.setVisible(visible)
        self.ui.comboBoxCustomModulations.setVisible(visible)

    def resizeEvent(self, event: QResizeEvent):
        self.update_views()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            return
        else:
            super().keyPressEvent(event)

    def initialize(self, bits: str):
        self.on_modulation_type_changed()  # for drawing modulated signal initially
        self.original_bits = bits
        self.ui.linEdDataBits.setText(bits)
        self.draw_original_signal()
        self.ui.gVModulated.show_full_scene(reinitialize=True)
        self.ui.gVModulated.auto_fit_view()
        self.ui.gVData.show_full_scene(reinitialize=True)
        self.ui.gVData.auto_fit_view()
        self.ui.gVCarrier.show_full_scene(reinitialize=True)
        self.ui.gVCarrier.auto_fit_view()

        self.mark_samples_in_view()

    def update_modulation_parameters(self):
        n = len(self.current_modulator.parameters) - 1
        if self.current_modulator.is_amplitude_based:
            regex = r"(100|[0-9]{1,2})"
        elif self.current_modulator.is_frequency_based:
            regex = r"((-?[0-9]+)[.,]?[0-9]*[kKmMgG]?)"
        elif self.current_modulator.is_phase_based:
            regex = r"(-?(36[0]|3[0-5][0-9]|[12][0-9][0-9]|[1-9]?[0-9]))"
        else:
            raise ValueError("Unknown modulation type")

        full_regex = r"^(" + regex + r"/){" + str(n) + "}" + regex + r"$"
        self.ui.lineEditParameters.setValidator(QRegExpValidator(QRegExp(full_regex)))
        self.ui.lineEditParameters.setText(self.current_modulator.parameters_string)

    def set_bits_per_symbol_enabled_status(self):
        if self.current_modulator.modulation_type == "OQPSK":
            self.ui.spinBoxBitsPerSymbol.setEnabled(False)
            self.ui.spinBoxBitsPerSymbol.setValue(2)
        else:
            self.ui.spinBoxBitsPerSymbol.setEnabled(True)

    def show_full_scene(self):
        for graphic_view in (self.ui.gVModulated, self.ui.gVData, self.ui.gVCarrier):
            graphic_view.show_full_scene(reinitialize=True)

    @pyqtSlot()
    def on_carrier_freq_changed(self):
        self.current_modulator.carrier_freq_hz = (
            self.ui.doubleSpinBoxCarrierFreq.value()
        )
        self.draw_carrier()
        self.draw_modulated()

    @pyqtSlot()
    def on_carrier_phase_changed(self):
        self.current_modulator.carrier_phase_deg = (
            self.ui.doubleSpinBoxCarrierPhase.value()
        )
        self.draw_carrier()
        self.draw_modulated()

    @pyqtSlot()
    def on_samples_per_symbol_changed(self):
        self.current_modulator.samples_per_symbol = (
            self.ui.spinBoxSamplesPerSymbol.value()
        )
        self.draw_carrier()
        self.draw_data_bits()
        self.draw_modulated()
        self.show_full_scene()

    @pyqtSlot()
    def on_data_bits_changed(self):
        text = self.ui.linEdDataBits.text()
        text = "".join(c for c in text if c == "1" or c == "0")
        self.ui.linEdDataBits.blockSignals(True)
        self.ui.linEdDataBits.setText(text)
        self.ui.linEdDataBits.blockSignals(False)
        self.current_modulator.display_bits = text
        self.draw_carrier()
        self.draw_data_bits()
        self.draw_modulated()
        if len(text) > 0:
            if len(text) > 24:
                display_text = text[0:24] + "..."
            else:
                display_text = text
            self.ui.cbShowDataBitsOnly.setToolTip(text)
            self.ui.cbShowDataBitsOnly.setText(
                self.tr("Show Only Data Sequence\n") + "(" + display_text + ")"
            )
        else:
            self.ui.cbShowDataBitsOnly.setToolTip("")
            self.ui.cbShowDataBitsOnly.setText(self.tr("Show Only Data Sequence\n"))

        self.search_data_sequence()
        self.restore_bits_action.setEnabled(text != self.original_bits)
        self.show_full_scene()

    @pyqtSlot()
    def on_sample_rate_changed(self):
        if int(self.ui.spinBoxSampleRate.value()) > 0:
            self.current_modulator.sample_rate = int(self.ui.spinBoxSampleRate.value())
            self.draw_carrier()
            self.draw_modulated()

    @pyqtSlot()
    def on_gauss_bt_changed(self):
        self.current_modulator.gauss_bt = self.ui.spinBoxGaussBT.value()
        self.draw_modulated()

    @pyqtSlot()
    def on_gauss_filter_width_changed(self):
        self.current_modulator.gauss_filter_width = (
            self.ui.spinBoxGaussFilterWidth.value()
        )
        self.draw_modulated()

    @pyqtSlot()
    def on_bits_per_symbol_changed(self):
        if (
            self.current_modulator.bits_per_symbol
            == self.ui.spinBoxBitsPerSymbol.value()
        ):
            return
        self.current_modulator.bits_per_symbol = self.ui.spinBoxBitsPerSymbol.value()
        self.set_default_modulation_parameters()
        self.draw_modulated()
        self.show_full_scene()

    @pyqtSlot()
    def on_modulation_type_changed(self):
        write_default_parameters = (
            self.current_modulator.modulation_type != self.__cur_selected_mod_type()
        )
        self.current_modulator.modulation_type = self.__cur_selected_mod_type()

        self.__set_gauss_ui_visibility(self.__cur_selected_mod_type() == "GFSK")

        self.ui.labelParameters.setText(self.current_modulator.parameter_type_str)
        if write_default_parameters:
            self.set_default_modulation_parameters()
        else:
            self.update_modulation_parameters()

        self.set_bits_per_symbol_enabled_status()
        self.draw_modulated()
        self.show_full_scene()

    @pyqtSlot()
    def on_orig_signal_zoomed(self):
        start = self.ui.gVOriginalSignal.view_rect().x()
        end = start + self.ui.gVOriginalSignal.view_rect().width()

        self.ui.gVOriginalSignal.centerOn(start + (end - start) / 2, 0)
        if self.lock_samples_in_view:
            self.adjust_samples_in_view(self.ui.gVOriginalSignal.view_rect().width())

            x = (
                self.ui.gVOriginalSignal.view_rect().x()
                + self.ui.gVOriginalSignal.view_rect().width() / 2
            )
            y = 0

            self.ui.gVModulated.centerOn(x, y)
            self.ui.gVCarrier.centerOn(x, y)
            self.ui.gVData.centerOn(x, y)
        else:
            self.mark_samples_in_view()

    @pyqtSlot(float)
    def on_carrier_data_modulated_zoomed(self, factor: float):
        x = self.sender().view_rect().x() + self.sender().view_rect().width() / 2
        y = 0
        for gv in (self.ui.gVCarrier, self.ui.gVData, self.ui.gVModulated):
            if gv == self.sender():
                continue
            if factor == -1:
                gv.show_full_scene()
            else:
                gv.scale(factor, 1)
                gv.centerOn(x, y)

        if self.lock_samples_in_view:
            self.adjust_samples_in_view(self.ui.gVModulated.view_rect().width())
            self.ui.gVOriginalSignal.centerOn(x, y)
        else:
            self.mark_samples_in_view()

    @pyqtSlot()
    def on_custom_modulation_name_edited(self):
        self.current_modulator.name = self.ui.comboBoxCustomModulations.currentText()

    @pyqtSlot()
    def on_custom_modulation_index_changed(self):
        self.set_ui_for_current_modulator()
        self.draw_carrier()
        self.draw_data_bits()
        self.draw_modulated()

    @pyqtSlot()
    def on_btn_next_search_result_clicked(self):
        cur_search_result = int(self.ui.lCurrentSearchResult.text()) - 1
        self.show_search_result(cur_search_result + 1)

    @pyqtSlot()
    def on_btn_prev_search_result_clicked(self):
        cur_search_result = int(self.ui.lCurrentSearchResult.text()) - 1
        self.show_search_result(cur_search_result - 1)

    @pyqtSlot()
    def on_show_data_bits_only_changed(self, redraw=True):
        show_data_bits_only = self.ui.cbShowDataBitsOnly.isChecked()
        if not self.ui.cbShowDataBitsOnly.isEnabled() or not show_data_bits_only:
            self.ui.btnSearchPrev.setEnabled(False)
            self.ui.btnSearchNext.setEnabled(False)
            self.ui.lCurrentSearchResult.setText("-")
            self.ui.lTotalSearchresults.setText("-")
        else:
            self.search_data_sequence()

        if not redraw:
            return

        if self.ui.cbShowDataBitsOnly.isEnabled() and not show_data_bits_only:
            self.draw_original_signal()

    @pyqtSlot()
    def on_remove_modulator_clicked(self):
        index = self.ui.comboBoxCustomModulations.currentIndex()
        self.ui.comboBoxCustomModulations.removeItem(index)
        self.modulators.remove(self.modulators[index])

        if len(self.modulators) == 1:
            self.ui.btnRemoveModulation.setDisabled(True)

    @pyqtSlot()
    def on_lock_siv_changed(self):
        self.lock_samples_in_view = self.ui.chkBoxLockSIV.isChecked()
        if self.lock_samples_in_view:
            self.adjust_samples_in_view(self.ui.gVModulated.view_rect().width())

    @pyqtSlot()
    def on_restore_bits_action_triggered(self):
        self.ui.linEdDataBits.setText(self.original_bits)

    @pyqtSlot()
    def on_btn_autodetect_clicked(self):
        signal = self.ui.gVOriginalSignal.scene_manager.signal
        freq = self.current_modulator.estimate_carrier_frequency(signal, self.protocol)

        if freq is None or freq == 0:
            QMessageBox.information(
                self,
                self.tr("No results"),
                self.tr("Unable to detect parameters from current signal"),
            )
            return

        self.ui.doubleSpinBoxCarrierFreq.setValue(freq)
        self.detect_fsk_frequencies()

    @pyqtSlot(int)
    def on_modulated_selection_changed(self, new_width: int):
        self.ui.lModulatedSelectedSamples.setText(str(abs(new_width)))

    @pyqtSlot(int)
    def on_original_selection_changed(self, new_width: int):
        self.ui.lOriginalSignalSamplesSelected.setText(str(abs(new_width)))

    @pyqtSlot()
    def on_configure_parameters_action_triggered(self):
        self.ui.lineEditParameters.editingFinished.emit()
        dialog = ModulationParametersDialog(
            self.current_modulator.parameters,
            self.current_modulator.modulation_type,
            self,
        )
        dialog.accepted.connect(self.update_modulation_parameters)
        dialog.show()

    @pyqtSlot()
    def on_line_edit_parameters_editing_finished(self):
        if not self.ui.lineEditParameters.hasAcceptableInput():
            return

        text = self.ui.lineEditParameters.text()
        parameters = []
        for param in text.split("/"):
            param = param.upper().replace(",", ".")
            factor = 1
            if param.endswith("G"):
                factor = 10**9
                param = param[:-1]
            elif param.endswith("M"):
                factor = 10**6
                param = param[:-1]
            elif param.endswith("K"):
                factor = 10**3
                param = param[:-1]

            try:
                parameters.append(factor * float(param))
            except ValueError:
                logger.warning("Could not convert {} to number".format(param))
                return

        self.current_modulator.parameters[:] = array("f", parameters)
        self.draw_modulated()
        self.show_full_scene()
