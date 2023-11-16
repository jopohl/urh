import math
import time
from multiprocessing import Process, Array

import numpy as np
from PyQt5.QtCore import pyqtSignal, QPoint, Qt, QMimeData, pyqtSlot, QTimer
from PyQt5.QtGui import (
    QIcon,
    QDrag,
    QPixmap,
    QRegion,
    QDropEvent,
    QTextCursor,
    QContextMenuEvent,
    QResizeEvent,
)
from PyQt5.QtWidgets import (
    QFrame,
    QMessageBox,
    QMenu,
    QWidget,
    QUndoStack,
    QCheckBox,
    QApplication,
    qApp,
)

from urh import settings
from urh.controller.dialogs.AdvancedModulationOptionsDialog import (
    AdvancedModulationOptionsDialog,
)
from urh.controller.dialogs.CostaOptionsDialog import CostaOptionsDialog
from urh.controller.dialogs.FilterDialog import FilterDialog
from urh.controller.dialogs.SendDialog import SendDialog
from urh.controller.dialogs.SignalDetailsDialog import SignalDetailsDialog
from urh.signalprocessing.Filter import Filter, FilterType
from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.signalprocessing.Spectrogram import Spectrogram
from urh.ui.actions.ChangeSignalParameter import ChangeSignalParameter
from urh.ui.actions.EditSignalAction import EditSignalAction, EditAction
from urh.ui.painting.SignalSceneManager import SignalSceneManager
from urh.ui.ui_signal_frame import Ui_SignalFrame
from urh.util import FileOperator, util
from urh.util.Errors import Errors
from urh.util.Formatter import Formatter
from urh.util.Logger import logger


def perform_filter(result_array: Array, data, f_low, f_high, filter_bw):
    result_array = np.frombuffer(result_array.get_obj(), dtype=np.complex64)
    result_array[:] = Filter.apply_bandpass_filter(
        data, f_low, f_high, filter_bw=filter_bw
    )


class SignalFrame(QFrame):
    closed = pyqtSignal(QWidget)
    signal_created = pyqtSignal(Signal)
    drag_started = pyqtSignal(QPoint)
    frame_dropped = pyqtSignal(QPoint)
    files_dropped = pyqtSignal(list)
    not_show_again_changed = pyqtSignal()
    signal_drawing_finished = pyqtSignal()
    apply_to_all_clicked = pyqtSignal(Signal)
    sort_action_clicked = pyqtSignal()

    @property
    def proto_view(self):
        return self.ui.txtEdProto.cur_view

    def __init__(
        self,
        proto_analyzer: ProtocolAnalyzer,
        undo_stack: QUndoStack,
        project_manager,
        parent=None,
    ):
        super().__init__(parent)

        self.undo_stack = undo_stack

        self.ui = Ui_SignalFrame()
        self.ui.setupUi(self)

        util.set_splitter_stylesheet(self.ui.splitter)

        self.__set_spectrogram_adjust_widgets_visibility()
        self.ui.gvSignal.init_undo_stack(self.undo_stack)

        self.ui.txtEdProto.setFont(util.get_monospace_font())
        self.ui.txtEdProto.participants = project_manager.participants
        self.ui.txtEdProto.messages = proto_analyzer.messages

        self.ui.gvSignal.participants = project_manager.participants

        self.filter_abort_wanted = False

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.project_manager = project_manager

        self.proto_analyzer = proto_analyzer
        self.signal = (
            proto_analyzer.signal if self.proto_analyzer is not None else None
        )  # type: Signal
        self.ui.gvSignal.protocol = self.proto_analyzer
        self.ui.gvSignal.set_signal(self.signal)
        self.ui.sliderFFTWindowSize.setValue(
            int(math.log2(Spectrogram.DEFAULT_FFT_WINDOW_SIZE))
        )
        self.ui.sliderSpectrogramMin.setValue(
            self.ui.gvSpectrogram.scene_manager.spectrogram.data_min
        )
        self.ui.sliderSpectrogramMax.setValue(
            self.ui.gvSpectrogram.scene_manager.spectrogram.data_max
        )

        self.dsp_filter = Filter([0.1] * 10, FilterType.moving_average)
        self.set_filter_button_caption()
        self.filter_dialog = FilterDialog(self.dsp_filter, parent=self)

        self.proto_selection_timer = QTimer(self)  # For Update Proto Selection from ROI
        self.proto_selection_timer.setSingleShot(True)
        self.proto_selection_timer.setInterval(1)

        self.spectrogram_update_timer = QTimer(self)
        self.spectrogram_update_timer.setSingleShot(True)
        self.spectrogram_update_timer.setInterval(500)

        # Disabled because never used (see also set_protocol_visibilty())
        self.ui.chkBoxSyncSelection.hide()

        if self.signal is not None:
            self.filter_menu = QMenu()
            self.apply_filter_to_selection_only = self.filter_menu.addAction(
                self.tr("Apply only to selection")
            )
            self.apply_filter_to_selection_only.setCheckable(True)
            self.apply_filter_to_selection_only.setChecked(False)
            self.configure_filter_action = self.filter_menu.addAction(
                "Configure filter..."
            )
            self.configure_filter_action.setIcon(QIcon.fromTheme("configure"))
            self.configure_filter_action.triggered.connect(
                self.on_configure_filter_action_triggered
            )
            self.ui.btnFilter.setMenu(self.filter_menu)

            if not self.signal.already_demodulated:
                self.auto_detect_menu = QMenu()
                self.detect_noise_action = self.auto_detect_menu.addAction(
                    self.tr("Additionally detect noise")
                )
                self.detect_noise_action.setCheckable(True)
                self.detect_noise_action.setChecked(False)
                self.detect_modulation_action = self.auto_detect_menu.addAction(
                    self.tr("Additionally detect modulation")
                )
                self.detect_modulation_action.setCheckable(True)
                self.detect_modulation_action.setChecked(False)
                self.ui.btnAutoDetect.setMenu(self.auto_detect_menu)

            if self.signal.wav_mode:
                if self.signal.already_demodulated:
                    self.ui.lSignalTyp.setText("Demodulated (1-channel *.wav)")
                else:
                    self.ui.lSignalTyp.setText("Signal (*.wav)")
            else:
                self.ui.lSignalTyp.setText("Complex Signal")

            self.ui.lineEditSignalName.setText(self.signal.name)
            self.ui.lSamplesInView.setText("{0:,}".format(self.signal.num_samples))
            self.ui.lSamplesTotal.setText("{0:,}".format(self.signal.num_samples))
            self.sync_protocol = self.ui.chkBoxSyncSelection.isChecked()
            self.ui.chkBoxSyncSelection.hide()

            self.ui.splitter.setSizes([self.ui.splitter.height(), 0])

            self.protocol_selection_is_updateable = True

            self.scene_manager = SignalSceneManager(self.signal, self)
            self.ui.gvSignal.scene_manager = self.scene_manager
            self.scene_manager.scene.setParent(self.ui.gvSignal)
            self.ui.gvSignal.setScene(self.scene_manager.scene)

            self.ui.spinBoxCenterSpacing.setValue(self.signal.center_spacing)
            self.ui.spinBoxBitsPerSymbol.setValue(self.signal.bits_per_symbol)

            self.jump_sync = True
            self.on_btn_show_hide_start_end_clicked()

            self.refresh_signal_information(block=True)
            self.create_connects()
            self.set_protocol_visibility()

            self.ui.chkBoxShowProtocol.setChecked(True)
            self.ui.btnSaveSignal.hide()

            self.show_protocol(refresh=False)

            if self.signal.already_demodulated:
                self.ui.cbModulationType.hide()
                self.ui.labelModulation.hide()
                self.ui.labelNoise.hide()
                self.ui.spinBoxNoiseTreshold.hide()
                self.ui.btnAutoDetect.hide()
                self.ui.cbSignalView.setCurrentIndex(1)
                self.ui.cbSignalView.hide()
                self.ui.lSignalViewText.hide()

        else:
            self.ui.lSignalTyp.setText("Protocol")
            self.set_empty_frame_visibilities()
            self.create_connects()

        self.set_center_spacing_visibility()

    @property
    def spectrogram_is_active(self) -> bool:
        return self.ui.stackedWidget.currentWidget() == self.ui.pageSpectrogram

    def create_connects(self):
        self.ui.btnCloseSignal.clicked.connect(self.on_btn_close_signal_clicked)
        self.ui.btnReplay.clicked.connect(self.on_btn_replay_clicked)
        self.ui.btnAutoDetect.clicked.connect(self.on_btn_autodetect_clicked)
        self.ui.btnInfo.clicked.connect(self.on_info_btn_clicked)
        self.ui.btnShowHideStartEnd.clicked.connect(
            self.on_btn_show_hide_start_end_clicked
        )
        self.filter_dialog.filter_accepted.connect(
            self.on_filter_dialog_filter_accepted
        )
        self.ui.sliderFFTWindowSize.valueChanged.connect(
            self.on_slider_fft_window_size_value_changed
        )
        self.ui.sliderSpectrogramMin.valueChanged.connect(
            self.on_slider_spectrogram_min_value_changed
        )
        self.ui.sliderSpectrogramMax.valueChanged.connect(
            self.on_slider_spectrogram_max_value_changed
        )
        self.ui.gvSpectrogram.y_scale_changed.connect(
            self.on_gv_spectrogram_y_scale_changed
        )
        self.ui.gvSpectrogram.bandpass_filter_triggered.connect(
            self.on_bandpass_filter_triggered
        )
        self.ui.gvSpectrogram.export_fta_wanted.connect(self.on_export_fta_wanted)
        self.ui.btnAdvancedModulationSettings.clicked.connect(
            self.on_btn_advanced_modulation_settings_clicked
        )

        if self.signal is not None:
            self.ui.gvSignal.save_clicked.connect(self.save_signal)

            self.signal.samples_per_symbol_changed.connect(
                self.ui.spinBoxSamplesPerSymbol.setValue
            )
            self.signal.center_changed.connect(self.on_signal_center_changed)
            self.signal.noise_threshold_changed.connect(self.on_noise_threshold_changed)
            self.signal.modulation_type_changed.connect(
                self.ui.cbModulationType.setCurrentText
            )
            self.signal.tolerance_changed.connect(self.ui.spinBoxTolerance.setValue)
            self.signal.protocol_needs_update.connect(self.refresh_protocol)
            self.signal.data_edited.connect(
                self.on_signal_data_edited
            )  # Crop/Delete Mute etc.
            self.signal.bits_per_symbol_changed.connect(
                self.ui.spinBoxBitsPerSymbol.setValue
            )
            self.signal.center_spacing_changed.connect(
                self.on_signal_center_spacing_changed
            )

            self.signal.sample_rate_changed.connect(self.on_signal_sample_rate_changed)

            self.signal.saved_status_changed.connect(
                self.on_signal_data_changed_before_save
            )
            self.ui.btnSaveSignal.clicked.connect(self.save_signal)
            self.signal.name_changed.connect(self.ui.lineEditSignalName.setText)

            self.ui.gvSignal.selection_width_changed.connect(
                self.start_proto_selection_timer
            )
            self.ui.gvSignal.sel_area_start_end_changed.connect(
                self.start_proto_selection_timer
            )
            self.proto_selection_timer.timeout.connect(
                self.update_protocol_selection_from_roi
            )
            self.spectrogram_update_timer.timeout.connect(
                self.on_spectrogram_update_timer_timeout
            )

            self.ui.lineEditSignalName.editingFinished.connect(self.change_signal_name)
            self.proto_analyzer.qt_signals.protocol_updated.connect(
                self.on_protocol_updated
            )

            self.ui.btnFilter.clicked.connect(self.on_btn_filter_clicked)

        self.ui.gvSignal.set_noise_clicked.connect(
            self.on_set_noise_in_graphic_view_clicked
        )
        self.ui.gvSignal.save_as_clicked.connect(self.save_signal_as)
        self.ui.gvSignal.export_demodulated_clicked.connect(self.export_demodulated)

        self.ui.gvSignal.create_clicked.connect(self.create_new_signal)
        self.ui.gvSignal.zoomed.connect(self.on_signal_zoomed)
        self.ui.gvSpectrogram.zoomed.connect(self.on_spectrum_zoomed)
        self.ui.gvSignal.sel_area_start_end_changed.connect(self.update_selection_area)
        self.ui.gvSpectrogram.sel_area_start_end_changed.connect(
            self.update_selection_area
        )
        self.ui.gvSpectrogram.selection_height_changed.connect(
            self.update_number_selected_samples
        )
        self.ui.gvSignal.sep_area_changed.connect(self.set_center)

        self.ui.sliderYScale.valueChanged.connect(self.on_slider_y_scale_value_changed)
        self.ui.spinBoxXZoom.valueChanged.connect(self.on_spinbox_x_zoom_value_changed)

        self.project_manager.project_updated.connect(self.on_participant_changed)
        self.ui.txtEdProto.participant_changed.connect(self.on_participant_changed)
        self.ui.gvSignal.participant_changed.connect(self.on_participant_changed)

        self.proto_selection_timer.timeout.connect(self.update_number_selected_samples)

        self.ui.cbSignalView.currentIndexChanged.connect(
            self.on_cb_signal_view_index_changed
        )
        self.ui.cbModulationType.currentTextChanged.connect(
            self.on_combobox_modulation_type_text_changed
        )
        self.ui.cbProtoView.currentIndexChanged.connect(
            self.on_combo_box_proto_view_index_changed
        )

        self.ui.chkBoxShowProtocol.stateChanged.connect(self.set_protocol_visibility)
        self.ui.chkBoxSyncSelection.stateChanged.connect(
            self.handle_protocol_sync_changed
        )

        self.ui.txtEdProto.proto_view_changed.connect(self.show_protocol)
        self.ui.txtEdProto.show_proto_clicked.connect(
            self.update_roi_from_protocol_selection
        )
        self.ui.txtEdProto.show_proto_clicked.connect(self.zoom_to_roi)
        self.ui.txtEdProto.selectionChanged.connect(
            self.update_roi_from_protocol_selection
        )
        self.ui.txtEdProto.deletion_wanted.connect(
            self.ui.gvSignal.on_delete_action_triggered
        )

        self.ui.spinBoxSelectionStart.valueChanged.connect(
            self.on_spinbox_selection_start_value_changed
        )
        self.ui.spinBoxSelectionEnd.valueChanged.connect(
            self.on_spinbox_selection_end_value_changed
        )
        self.ui.spinBoxCenterOffset.editingFinished.connect(
            self.on_spinbox_center_editing_finished
        )
        self.ui.spinBoxCenterSpacing.valueChanged.connect(
            self.on_spinbox_spacing_value_changed
        )
        self.ui.spinBoxCenterSpacing.editingFinished.connect(
            self.on_spinbox_spacing_editing_finished
        )
        self.ui.spinBoxTolerance.editingFinished.connect(
            self.on_spinbox_tolerance_editing_finished
        )
        self.ui.spinBoxNoiseTreshold.editingFinished.connect(
            self.on_spinbox_noise_threshold_editing_finished
        )
        self.ui.spinBoxSamplesPerSymbol.editingFinished.connect(
            self.on_spinbox_samples_per_symbol_editing_finished
        )
        self.ui.spinBoxBitsPerSymbol.editingFinished.connect(
            self.on_spinbox_bits_per_symbol_editing_finished
        )

    def refresh_signal_information(self, block=True):
        self.ui.spinBoxTolerance.blockSignals(block)
        self.ui.spinBoxCenterOffset.blockSignals(block)
        self.ui.spinBoxSamplesPerSymbol.blockSignals(block)
        self.ui.spinBoxNoiseTreshold.blockSignals(block)
        self.ui.spinBoxBitsPerSymbol.blockSignals(block)
        self.ui.spinBoxCenterSpacing.blockSignals(block)

        self.ui.spinBoxTolerance.setValue(self.signal.tolerance)
        self.ui.spinBoxCenterOffset.setValue(self.signal.center)
        self.ui.spinBoxSamplesPerSymbol.setValue(self.signal.samples_per_symbol)
        self.ui.spinBoxNoiseTreshold.setValue(self.signal.noise_threshold_relative)
        self.ui.cbModulationType.setCurrentText(self.signal.modulation_type)
        self.ui.btnAdvancedModulationSettings.setVisible(
            self.ui.cbModulationType.currentText() in ("ASK", "PSK")
        )
        self.ui.spinBoxCenterSpacing.setValue(self.signal.center_spacing)
        self.ui.spinBoxBitsPerSymbol.setValue(self.signal.bits_per_symbol)

        self.ui.spinBoxTolerance.blockSignals(False)
        self.ui.spinBoxCenterOffset.blockSignals(False)
        self.ui.spinBoxSamplesPerSymbol.blockSignals(False)
        self.ui.spinBoxNoiseTreshold.blockSignals(False)
        self.ui.spinBoxCenterSpacing.blockSignals(False)
        self.ui.spinBoxBitsPerSymbol.blockSignals(False)

        self.set_center_spacing_visibility()

    def set_empty_frame_visibilities(self):
        for widget in dir(self.ui):
            w = getattr(self.ui, widget)
            if hasattr(w, "hide") and w not in (
                self.ui.lSignalNr,
                self.ui.lSignalTyp,
                self.ui.btnCloseSignal,
                self.ui.lineEditSignalName,
            ):
                w.hide()

        self.adjustSize()

    def cancel_filtering(self):
        self.filter_abort_wanted = True

    def update_number_selected_samples(self):
        if self.spectrogram_is_active:
            self.ui.lNumSelectedSamples.setText(
                str(abs(int(self.ui.gvSpectrogram.selection_area.length)))
            )
            self.__set_selected_bandwidth()
            return
        else:
            self.ui.lNumSelectedSamples.setText(
                str(abs(int(self.ui.gvSignal.selection_area.length)))
            )
            self.__set_duration()

        try:
            start, end = int(self.ui.gvSignal.selection_area.start), int(
                self.ui.gvSignal.selection_area.end
            )
            power_str = "-\u221e"  # minus infinity
            if start < end:
                max_window_size = 10**5
                step_size = int(math.ceil((end - start) / max_window_size))
                power = np.mean(
                    self.signal.iq_array.subarray(
                        start, end, step_size
                    ).magnitudes_normalized
                )
                if power > 0:
                    power_str = Formatter.big_value_with_suffix(10 * np.log10(power), 2)

            self.ui.labelRSSI.setText("{} dBm".format(power_str))

        except Exception as e:
            logger.exception(e)
            self.ui.labelRSSI.setText("")

    def change_signal_name(self):
        if self.signal is not None:
            self.signal.name = self.ui.lineEditSignalName.text()

    def __set_spectrogram_adjust_widgets_visibility(self):
        self.ui.labelFFTWindowSize.setVisible(self.ui.cbSignalView.currentIndex() == 2)
        self.ui.sliderFFTWindowSize.setVisible(self.ui.cbSignalView.currentIndex() == 2)
        self.ui.labelSpectrogramMin.setVisible(self.ui.cbSignalView.currentIndex() == 2)
        self.ui.labelSpectrogramMax.setVisible(self.ui.cbSignalView.currentIndex() == 2)
        self.ui.sliderSpectrogramMin.setVisible(
            self.ui.cbSignalView.currentIndex() == 2
        )
        self.ui.sliderSpectrogramMax.setVisible(
            self.ui.cbSignalView.currentIndex() == 2
        )

    def __set_selected_bandwidth(self):
        try:
            num_samples = int(self.ui.lNumSelectedSamples.text())
        except ValueError:
            return

        if self.ui.gvSpectrogram.height_spectrogram and self.signal:
            bw = (
                num_samples / self.ui.gvSpectrogram.height_spectrogram
            ) * self.signal.sample_rate
            self.ui.lDuration.setText(Formatter.big_value_with_suffix(bw) + "Hz")

    def __set_duration(self):  # On Signal Sample Rate changed
        try:
            num_samples = int(self.ui.lNumSelectedSamples.text())
        except ValueError:
            return

        if self.signal:
            t = num_samples / self.signal.sample_rate
            self.ui.lDuration.setText(Formatter.science_time(t))

    def on_slider_y_scale_value_changed(self):
        try:
            gv = (
                self.ui.gvSignal
                if self.ui.stackedWidget.currentIndex() == 0
                else self.ui.gvSpectrogram
            )
            yscale = self.ui.sliderYScale.value()
            current_factor = gv.sceneRect().height() / gv.view_rect().height()
            gv.scale(1, yscale / current_factor)
            x, w = gv.view_rect().x(), gv.view_rect().width()
            gv.centerOn(x + w / 2, gv.y_center)
            if gv.scene_type == 1:
                gv.scene().redraw_legend()
        except ZeroDivisionError:
            pass

    @pyqtSlot()
    def on_slider_fft_window_size_value_changed(self):
        self.spectrogram_update_timer.start()

    @pyqtSlot()
    def on_slider_spectrogram_min_value_changed(self):
        self.spectrogram_update_timer.start()

    @pyqtSlot()
    def on_slider_spectrogram_max_value_changed(self):
        self.spectrogram_update_timer.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_started.emit(self.mapToParent(event.pos()))
            drag = QDrag(self)
            mimeData = QMimeData()
            mimeData.setText("Move Signal")
            pixmap = QPixmap(self.rect().size())
            self.render(pixmap, QPoint(), QRegion(self.rect()))
            drag.setPixmap(pixmap)

            drag.setMimeData(mimeData)

            drag.exec_()

    def set_filter_button_caption(self):
        self.ui.btnFilter.setText(
            "Filter ({0})".format(self.dsp_filter.filter_type.value)
        )

    def dragMoveEvent(self, event):
        event.accept()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if len(event.mimeData().urls()) == 0:
            self.frame_dropped.emit(self.mapToParent(event.pos()))
        else:
            self.files_dropped.emit(event.mimeData().urls())

    def create_new_signal(self, start, end):
        if start != end:
            new_signal = self.signal.create_new(start=start, end=end)
            self.signal_created.emit(new_signal)
        else:
            Errors.empty_selection()

    def my_close(self):
        not_show = settings.read("not_show_close_dialog", False, type=bool)

        if not not_show:
            cb = QCheckBox("Do not show this again.")
            msgbox = QMessageBox(
                QMessageBox.Question, "Confirm close", "Are you sure you want to close?"
            )
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            msgbox.setCheckBox(cb)

            reply = msgbox.exec()

            not_show_again = bool(cb.isChecked())
            settings.write("not_show_close_dialog", not_show_again)
            self.not_show_again_changed.emit()
            if reply != QMessageBox.Yes:
                return

        self.closed.emit(self)

    def save_signal(self):
        if len(self.signal.filename) > 0:
            self.signal.save()
        else:
            self.save_signal_as()

    def save_signal_as(self):
        try:
            FileOperator.ask_signal_file_name_and_save(
                self.signal.name,
                self.signal.iq_array,
                self.signal.sample_rate,
                self.signal.wav_mode,
            )
        except Exception as e:
            Errors.exception(e)

    def export_demodulated(self):
        try:
            initial_name = self.signal.name + "-demodulated.wav"
        except Exception as e:
            logger.exception(e)
            initial_name = "demodulated.wav"

        filename = FileOperator.ask_save_file_name(
            initial_name, caption="Export demodulated"
        )
        if filename:
            try:
                self.setCursor(Qt.WaitCursor)
                data = self.signal.qad
                if filename.endswith(".wav") or filename.endswith(".sub"):
                    data = self.signal.qad.astype(np.float32)
                    data /= np.max(np.abs(data))
                FileOperator.save_data(
                    IQArray(data, skip_conversion=True),
                    filename,
                    self.signal.sample_rate,
                    num_channels=1,
                )
                self.unsetCursor()
            except Exception as e:
                QMessageBox.critical(
                    self, self.tr("Error exporting demodulated data"), e.args[0]
                )

    def draw_signal(self, full_signal=False):
        self.scene_manager.scene_type = self.ui.cbSignalView.currentIndex()
        self.scene_manager.init_scene()
        if full_signal:
            self.ui.gvSignal.show_full_scene()
        else:
            self.ui.gvSignal.redraw_view()

        self.ui.gvSignal.y_sep = -self.signal.center

    def restore_protocol_selection(
        self, sel_start, sel_end, start_message, end_message, old_protoview
    ):
        if old_protoview == self.proto_view:
            return

        self.protocol_selection_is_updateable = False
        sel_start = int(
            self.proto_analyzer.convert_index(
                sel_start, old_protoview, self.proto_view, True
            )[0]
        )
        sel_end = int(
            math.ceil(
                self.proto_analyzer.convert_index(
                    sel_end, old_protoview, self.proto_view, True
                )[1]
            )
        )

        c = self.ui.txtEdProto.textCursor()

        c.setPosition(0)
        cur_message = 0
        i = 0
        text = self.ui.txtEdProto.toPlainText()
        while cur_message < start_message:
            if text[i] == "\n":
                cur_message += 1
            i += 1

        c.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, i)
        c.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, sel_start)
        text = text[i:]
        i = 0
        while cur_message < end_message:
            if text[i] == "\n":
                cur_message += 1
            i += 1

        c.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, i)
        c.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, sel_end)

        self.ui.txtEdProto.setTextCursor(c)

        self.protocol_selection_is_updateable = True

    def update_protocol(self):
        self.ui.txtEdProto.setEnabled(False)
        self.ui.txtEdProto.setText("Demodulating...")
        qApp.processEvents()

        try:
            self.proto_analyzer.get_protocol_from_signal()
        except Exception as e:
            Errors.exception(e)

    def show_protocol(self, old_view=-1, refresh=False):
        if not self.proto_analyzer:
            return

        if not self.ui.chkBoxShowProtocol.isChecked():
            if refresh:
                self.update_protocol()
            return

        if old_view == -1:
            old_view = self.ui.cbProtoView.currentIndex()

        if self.proto_analyzer.messages is None or refresh:
            self.update_protocol()
        else:
            # Keep things synchronized and restore selection
            self.ui.txtEdProto.blockSignals(True)
            self.ui.cbProtoView.blockSignals(True)
            self.ui.cbProtoView.setCurrentIndex(self.proto_view)
            self.ui.cbProtoView.blockSignals(False)

            start_message = 0
            sel_start = self.ui.txtEdProto.textCursor().selectionStart()
            text = self.ui.txtEdProto.toPlainText()[:sel_start]
            sel_start = 0
            read_pause = False
            for t in text:
                if t == "\t":
                    read_pause = True

                if not read_pause:
                    sel_start += 1

                if t == "\n":
                    sel_start = 0
                    start_message += 1
                    read_pause = False

            sel_end = self.ui.txtEdProto.textCursor().selectionEnd()
            text = self.ui.txtEdProto.toPlainText()[
                self.ui.txtEdProto.textCursor().selectionStart() : sel_end
            ]
            end_message = 0
            sel_end = 0
            read_pause = False
            for t in text:
                if t == "\t":
                    read_pause = True

                if not read_pause:
                    sel_end += 1

                if t == "\n":
                    sel_end = 0
                    end_message += 1
                    read_pause = False

            self.ui.txtEdProto.setHtml(
                self.proto_analyzer.plain_to_html(self.proto_view)
            )
            try:
                self.restore_protocol_selection(
                    sel_start, sel_end, start_message, end_message, old_view
                )
            except TypeError:
                # Without try/except: segfault (TypeError) when changing sample_rate in info dialog of signal
                pass

            self.ui.txtEdProto.blockSignals(False)

    def draw_spectrogram(self, show_full_scene=False, force_redraw=False):
        self.setCursor(Qt.WaitCursor)
        window_size = 2 ** self.ui.sliderFFTWindowSize.value()
        data_min, data_max = (
            self.ui.sliderSpectrogramMin.value(),
            self.ui.sliderSpectrogramMax.value(),
        )

        redraw_needed = self.ui.gvSpectrogram.scene_manager.set_parameters(
            self.signal.iq_array.data,
            window_size=window_size,
            data_min=data_min,
            data_max=data_max,
        )
        self.ui.gvSpectrogram.scene_manager.update_scene_rect()

        if show_full_scene:
            self.ui.gvSpectrogram.show_full_scene()

        if redraw_needed or force_redraw:
            self.ui.gvSpectrogram.scene_manager.show_full_scene()
            self.ui.gvSpectrogram.show_full_scene()

        self.on_slider_y_scale_value_changed()

        self.__set_samples_in_view()
        self.unsetCursor()

    def eliminate(self):
        self.proto_selection_timer.stop()
        self.ui.verticalLayout.removeItem(self.ui.additionalInfos)

        if self.signal is not None:
            # Avoid memory leaks
            self.scene_manager.eliminate()
            self.signal.eliminate()
            self.proto_analyzer.eliminate()
            self.ui.gvSignal.scene_manager.eliminate()

        self.ui.gvSignal.eliminate()
        self.ui.gvSpectrogram.eliminate()

        self.scene_manager = None
        self.signal = None
        self.proto_analyzer = None

        self.ui.layoutWidget.setParent(None)
        self.ui.layoutWidget.deleteLater()

        self.setParent(None)
        self.deleteLater()

    def __handle_graphic_view_zoomed(self, graphic_view):
        self.ui.lSamplesInView.setText(
            "{0:n}".format(int(graphic_view.view_rect().width()))
        )
        self.ui.spinBoxXZoom.blockSignals(True)
        self.ui.spinBoxXZoom.setValue(
            int(
                graphic_view.sceneRect().width()
                / graphic_view.view_rect().width()
                * 100
            )
        )
        self.ui.spinBoxXZoom.blockSignals(False)

    @pyqtSlot()
    def on_signal_zoomed(self):
        self.__handle_graphic_view_zoomed(self.ui.gvSignal)

    @pyqtSlot()
    def on_spectrum_zoomed(self):
        self.__handle_graphic_view_zoomed(self.ui.gvSpectrogram)

    @pyqtSlot(int)
    def on_spinbox_x_zoom_value_changed(self, value: int):
        graphic_view = (
            self.ui.gvSpectrogram if self.spectrogram_is_active else self.ui.gvSignal
        )
        zoom_factor = value / 100
        current_factor = (
            graphic_view.sceneRect().width() / graphic_view.view_rect().width()
        )
        graphic_view.zoom(zoom_factor / current_factor)

    @pyqtSlot()
    def on_btn_close_signal_clicked(self):
        self.my_close()

    @pyqtSlot()
    def on_set_noise_in_graphic_view_clicked(self):
        self.setCursor(Qt.WaitCursor)
        start = self.ui.gvSignal.selection_area.x
        end = start + self.ui.gvSignal.selection_area.width

        new_thresh = self.signal.calc_relative_noise_threshold_from_range(start, end)
        self.ui.spinBoxNoiseTreshold.setValue(new_thresh)
        self.ui.spinBoxNoiseTreshold.editingFinished.emit()
        self.unsetCursor()

    @pyqtSlot(float)
    def on_signal_center_spacing_changed(self, value: float):
        self.ui.spinBoxCenterSpacing.setValue(value)
        if self.ui.gvSignal.scene_type == 1:
            self.ui.gvSignal.scene().redraw_legend()

    @pyqtSlot()
    def on_noise_threshold_changed(self):
        self.ui.spinBoxNoiseTreshold.setValue(self.signal.noise_threshold_relative)
        minimum = self.signal.noise_min_plot
        maximum = self.signal.noise_max_plot
        if (
            self.ui.cbSignalView.currentIndex() == 0
            or self.ui.cbSignalView.currentIndex() == 3
        ):
            # Draw Noise only in analog and I/Q view
            self.ui.gvSignal.scene().draw_noise_area(minimum, maximum - minimum)

    @pyqtSlot(int)
    def on_spinbox_selection_start_value_changed(self, value: int):
        if self.spectrogram_is_active:
            self.ui.gvSpectrogram.set_vertical_selection(
                y=self.ui.gvSpectrogram.sceneRect().height() - value
            )
            self.ui.gvSpectrogram.emit_selection_size_changed()
            self.ui.gvSpectrogram.selection_area.finished = True
        else:
            self.ui.gvSignal.set_horizontal_selection(x=value)
            self.ui.gvSignal.selection_area.finished = True
            self.ui.gvSignal.emit_selection_size_changed()

    @pyqtSlot(int)
    def on_spinbox_selection_end_value_changed(self, value: int):
        if self.spectrogram_is_active:
            self.ui.gvSpectrogram.set_vertical_selection(
                h=self.ui.spinBoxSelectionStart.value() - value
            )
            self.ui.gvSpectrogram.emit_selection_size_changed()
            self.ui.gvSpectrogram.selection_area.finished = True
        else:
            self.ui.gvSignal.set_horizontal_selection(
                w=value - self.ui.spinBoxSelectionStart.value()
            )
            self.ui.gvSignal.selection_area.finished = True
            self.ui.gvSignal.emit_selection_size_changed()

    @pyqtSlot()
    def on_protocol_updated(self):
        self.ui.gvSignal.redraw_view()  # Participants may have changed
        self.ui.txtEdProto.setEnabled(True)
        self.ui.txtEdProto.setHtml(self.proto_analyzer.plain_to_html(self.proto_view))

    @pyqtSlot()
    def handle_protocol_sync_changed(self):
        self.sync_protocol = self.ui.chkBoxSyncSelection.isChecked()

    @pyqtSlot()
    def set_protocol_visibility(self):
        checked = self.ui.chkBoxShowProtocol.isChecked()

        if checked:
            self.show_protocol()
            self.ui.cbProtoView.setEnabled(True)
            # Disabled because never used
            # self.ui.chkBoxSyncSelection.show()
            self.ui.txtEdProto.show()
        else:
            self.ui.txtEdProto.hide()
            self.ui.chkBoxSyncSelection.hide()
            self.ui.cbProtoView.setEnabled(False)

        qApp.processEvents()
        self.on_slider_y_scale_value_changed()

    @pyqtSlot()
    def on_cb_signal_view_index_changed(self):
        self.setCursor(Qt.WaitCursor)

        self.__set_spectrogram_adjust_widgets_visibility()

        if self.ui.cbSignalView.currentText().lower() == "spectrogram":
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageSpectrogram)
            self.draw_spectrogram(show_full_scene=True)
            self.__set_selected_bandwidth()
            self.ui.labelRSSI.hide()
        else:
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageSignal)
            self.ui.gvSignal.scene_type = self.ui.cbSignalView.currentIndex()
            self.scene_manager.mod_type = self.signal.modulation_type
            self.ui.gvSignal.redraw_view(reinitialize=True)
            self.ui.labelRSSI.show()

            self.ui.gvSignal.auto_fit_view()
            self.ui.gvSignal.refresh_selection_area()
            qApp.processEvents()
            self.on_slider_y_scale_value_changed()  # apply YScale to new view
            self.__set_samples_in_view()
            self.__set_duration()

        self.unsetCursor()

    @pyqtSlot()
    def on_btn_autodetect_clicked(self):
        self.ui.btnAutoDetect.setEnabled(False)
        self.setCursor(Qt.WaitCursor)

        try:
            detect_modulation = self.detect_modulation_action.isChecked()
        except AttributeError:
            detect_modulation = False

        try:
            detect_noise = self.detect_noise_action.isChecked()
        except AttributeError:
            detect_noise = False
        success = self.signal.auto_detect(
            detect_modulation=detect_modulation, detect_noise=detect_noise
        )

        self.ui.btnAutoDetect.setEnabled(True)
        self.unsetCursor()
        if not success:
            Errors.generic_error(
                self.tr("Autodetection failed"),
                self.tr("Failed to autodetect parameters for this signal."),
            )

    @pyqtSlot()
    def on_btn_replay_clicked(self):
        project_manager = self.project_manager
        try:
            dialog = SendDialog(
                project_manager, modulated_data=self.signal.iq_array, parent=self
            )
        except OSError as e:
            logger.error(repr(e))
            return

        if dialog.has_empty_device_list:
            Errors.no_device()
            dialog.close()
            return

        dialog.device_parameters_changed.connect(project_manager.set_device_parameters)
        dialog.show()
        dialog.graphics_view.show_full_scene(reinitialize=True)

    @pyqtSlot(int, int)
    def update_selection_area(self, start, end):
        self.update_number_selected_samples()
        self.ui.spinBoxSelectionStart.blockSignals(True)
        self.ui.spinBoxSelectionStart.setValue(start)
        self.ui.spinBoxSelectionStart.blockSignals(False)
        self.ui.spinBoxSelectionEnd.blockSignals(True)
        self.ui.spinBoxSelectionEnd.setValue(end)
        self.ui.spinBoxSelectionEnd.blockSignals(False)

    @pyqtSlot()
    def refresh_protocol(self):
        self.show_protocol(refresh=True)

    @pyqtSlot(int)
    def on_combo_box_proto_view_index_changed(self, index: int):
        old_view = self.ui.txtEdProto.cur_view
        self.ui.txtEdProto.cur_view = index
        self.show_protocol(old_view=old_view)

    @pyqtSlot(float)
    def set_center(self, th):
        self.ui.spinBoxCenterOffset.setValue(th)
        self.ui.spinBoxCenterOffset.editingFinished.emit()

    def set_roi_from_protocol_analysis(
        self, start_message, start_pos, end_message, end_pos, view_type
    ):
        if not self.proto_analyzer:
            return

        if not self.ui.chkBoxShowProtocol.isChecked():
            self.ui.chkBoxShowProtocol.setChecked(True)
            self.set_protocol_visibility()

        self.ui.cbProtoView.setCurrentIndex(view_type)

        if view_type == 1:
            # Hex View
            start_pos *= 4
            end_pos *= 4
        elif view_type == 2:
            # ASCII View
            start_pos *= 8
            end_pos *= 8

        sample_pos, num_samples = self.proto_analyzer.get_samplepos_of_bitseq(
            start_message, start_pos, end_message, end_pos, True
        )
        self.protocol_selection_is_updateable = False
        if sample_pos != -1:
            if self.jump_sync and self.sync_protocol:
                self.ui.gvSignal.centerOn(sample_pos, self.ui.gvSignal.y_center)
                self.ui.gvSignal.set_horizontal_selection(sample_pos, num_samples)
                self.ui.gvSignal.centerOn(
                    sample_pos + num_samples, self.ui.gvSignal.y_center
                )
            else:
                self.ui.gvSignal.set_horizontal_selection(sample_pos, num_samples)

            self.ui.gvSignal.zoom_to_selection(sample_pos, sample_pos + num_samples)
        else:
            self.ui.gvSignal.clear_horizontal_selection()

        self.protocol_selection_is_updateable = True
        self.update_protocol_selection_from_roi()

    @pyqtSlot()
    def update_roi_from_protocol_selection(self):
        text_edit = self.ui.txtEdProto
        start_pos, end_pos = (
            text_edit.textCursor().selectionStart(),
            text_edit.textCursor().selectionEnd(),
        )
        if start_pos == end_pos == -1:
            return

        forward_selection = (
            text_edit.textCursor().anchor() <= text_edit.textCursor().position()
        )

        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos

        text = text_edit.toPlainText()

        start_message = text[:start_pos].count("\n")
        end_message = start_message + text[start_pos:end_pos].count("\n")
        newline_pos = text[:start_pos].rfind("\n")

        if newline_pos != -1:
            start_pos -= newline_pos + 1

        newline_pos = text[:end_pos].rfind("\n")
        if newline_pos != -1:
            end_pos -= newline_pos + 1

        factor = 1 if text_edit.cur_view == 0 else 4 if text_edit.cur_view == 1 else 8
        start_pos *= factor
        end_pos *= factor

        try:
            include_last_pause = False
            s = text_edit.textCursor().selectionStart()
            e = text_edit.textCursor().selectionEnd()
            if s > e:
                s, e = e, s

            selected_text = text[s:e]

            last_newline = selected_text.rfind("\n")
            if last_newline == -1:
                last_newline = 0

            if selected_text.endswith(" "):
                end_pos -= 1
            elif selected_text.endswith(" \t"):
                end_pos -= 2

            if "[" in selected_text[last_newline:]:
                include_last_pause = True

            sample_pos, num_samples = self.proto_analyzer.get_samplepos_of_bitseq(
                start_message, start_pos, end_message, end_pos, include_last_pause
            )

        except IndexError:
            return

        self.ui.gvSignal.blockSignals(True)
        if sample_pos != -1:
            if self.jump_sync and self.sync_protocol:
                self.ui.gvSignal.centerOn(sample_pos, self.ui.gvSignal.y_center)
                self.ui.gvSignal.set_horizontal_selection(sample_pos, num_samples)
                if (
                    forward_selection
                ):  # Forward Selection --> Center ROI to End of Selection
                    self.ui.gvSignal.centerOn(
                        sample_pos + num_samples, self.ui.gvSignal.y_center
                    )
                else:  # Backward Selection --> Center ROI to Start of Selection
                    self.ui.gvSignal.centerOn(sample_pos, self.ui.gvSignal.y_center)
            else:
                self.ui.gvSignal.set_horizontal_selection(sample_pos, num_samples)
        else:
            self.ui.gvSignal.clear_horizontal_selection()
        self.ui.gvSignal.blockSignals(False)

        self.update_number_selected_samples()

    def zoom_to_roi(self):
        roi = self.ui.gvSignal.selection_area
        start, end = roi.x, roi.x + roi.width
        self.ui.gvSignal.zoom_to_selection(start, end)

    @pyqtSlot()
    def start_proto_selection_timer(self):
        self.proto_selection_timer.start()

    @pyqtSlot()
    def update_protocol_selection_from_roi(self):
        protocol = self.proto_analyzer

        if (
            protocol is None
            or protocol.messages is None
            or not self.ui.chkBoxShowProtocol.isChecked()
        ):
            return

        start = self.ui.gvSignal.selection_area.x
        w = self.ui.gvSignal.selection_area.width

        if w < 0:
            start += w
            w = -w

        c = self.ui.txtEdProto.textCursor()
        self.jump_sync = False
        self.ui.txtEdProto.blockSignals(True)

        try:
            (
                start_message,
                start_index,
                end_message,
                end_index,
            ) = protocol.get_bitseq_from_selection(start, w)
        except IndexError:
            c.clearSelection()
            self.ui.txtEdProto.setTextCursor(c)
            self.jump_sync = True
            self.ui.txtEdProto.blockSignals(False)
            return

        if (
            start_message == -1
            or end_index == -1
            or start_index == -1
            or end_message == -1
        ):
            c.clearSelection()
            self.ui.txtEdProto.setTextCursor(c)
            self.jump_sync = True
            self.ui.txtEdProto.blockSignals(False)
            return

        start_index = int(
            protocol.convert_index(start_index, 0, self.proto_view, True)[0]
        )
        end_index = (
            int(
                math.ceil(
                    protocol.convert_index(end_index, 0, self.proto_view, True)[1]
                )
            )
            + 1
        )
        text = self.ui.txtEdProto.toPlainText()
        n = 0
        message_pos = 0
        c.setPosition(0)

        for i, t in enumerate(text):
            message_pos += 1
            if t == "\n":
                n += 1
                message_pos = 0

            if n == start_message and message_pos == start_index:
                c.setPosition(i + 1, QTextCursor.MoveAnchor)

            if n == end_message and message_pos == end_index:
                c.setPosition(i, QTextCursor.KeepAnchor)
                break

        self.ui.txtEdProto.setTextCursor(c)
        self.ui.txtEdProto.blockSignals(False)
        self.jump_sync = True

    def __set_samples_in_view(self):
        if self.spectrogram_is_active:
            self.ui.lSamplesInView.setText(
                "{0:n}".format(int(self.ui.gvSpectrogram.view_rect().width()))
            )
            self.ui.lSamplesTotal.setText(
                "{0:n}".format(self.ui.gvSpectrogram.width_spectrogram)
            )
        else:
            self.ui.lSamplesInView.setText(
                "{0:n}".format(int(self.ui.gvSignal.view_rect().width()))
            )
            self.ui.lSamplesTotal.setText("{0:n}".format(self.signal.num_samples))

    def refresh_signal(self, draw_full_signal=False):
        self.draw_signal(draw_full_signal)

        self.__set_samples_in_view()
        self.update_number_selected_samples()
        self.on_slider_y_scale_value_changed()

    @pyqtSlot(float)
    def on_signal_center_changed(self, center):
        self.ui.gvSignal.y_sep = -center

        if self.ui.cbSignalView.currentIndex() > 0:
            self.scene_manager.scene.draw_sep_area(-self.signal.center_thresholds)
        self.ui.spinBoxCenterOffset.blockSignals(False)
        self.ui.spinBoxCenterOffset.setValue(center)

    def on_spinbox_noise_threshold_editing_finished(self):
        if (
            self.signal is not None
            and self.signal.noise_threshold_relative
            != self.ui.spinBoxNoiseTreshold.value()
        ):
            noise_action = ChangeSignalParameter(
                signal=self.signal,
                protocol=self.proto_analyzer,
                parameter_name="noise_threshold_relative",
                parameter_value=self.ui.spinBoxNoiseTreshold.value(),
            )
            self.undo_stack.push(noise_action)

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self.signal is None:
            return

        menu = QMenu()
        apply_to_all_action = menu.addAction(
            self.tr("Apply values (BitLen, 0/1-Threshold, Tolerance) to all signals")
        )
        menu.addSeparator()
        auto_detect_action = menu.addAction(self.tr("Auto-Detect signal parameters"))
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == apply_to_all_action:
            self.setCursor(Qt.WaitCursor)
            self.apply_to_all_clicked.emit(self.signal)
            self.unsetCursor()
        elif action == auto_detect_action:
            self.setCursor(Qt.WaitCursor)
            self.signal.auto_detect(detect_modulation=False, detect_noise=False)
            self.unsetCursor()

    def show_modulation_type(self):
        self.ui.cbModulationType.blockSignals(True)
        self.ui.cbModulationType.setCurrentText(self.signal.modulation_type)
        self.ui.cbModulationType.blockSignals(False)

    def on_participant_changed(self):
        if hasattr(self, "proto_analyzer") and self.proto_analyzer:
            self.proto_analyzer.qt_signals.protocol_updated.emit()

    def resizeEvent(self, event: QResizeEvent):
        old_width, new_width = max(1, event.oldSize().width()), max(
            1, event.size().width()
        )
        super().resizeEvent(event)
        self.on_slider_y_scale_value_changed()

        # Force update of GVS, when size changed e.g. when Project Tree is opened
        if not self.spectrogram_is_active:
            self.ui.gvSignal.zoom(new_width / old_width, zoom_to_mouse_cursor=False)

    def set_center_spacing_visibility(self):
        visible = self.ui.spinBoxBitsPerSymbol.value() > 1
        self.ui.spinBoxCenterSpacing.setVisible(visible)
        self.ui.lCenterSpacing.setVisible(visible)

    @pyqtSlot()
    def on_info_btn_clicked(self):
        sdc = SignalDetailsDialog(self.signal, self)
        sdc.show()

    @pyqtSlot(str)
    def on_combobox_modulation_type_text_changed(self, txt: str):
        if txt != self.signal.modulation_type:
            modulation_action = ChangeSignalParameter(
                signal=self.signal,
                protocol=self.proto_analyzer,
                parameter_name="modulation_type",
                parameter_value=txt,
            )

            self.undo_stack.push(modulation_action)

            self.scene_manager.mod_type = txt
            if self.ui.cbSignalView.currentIndex() == 1:
                self.scene_manager.init_scene()
                self.on_slider_y_scale_value_changed()

        self.ui.btnAdvancedModulationSettings.setVisible(
            self.ui.cbModulationType.currentText() in ("ASK", "PSK")
        )

    @pyqtSlot()
    def on_signal_data_changed_before_save(self):
        font = self.ui.lineEditSignalName.font()
        self.ui.gvSignal.auto_fit_on_resize_is_blocked = True

        if self.signal.changed:
            font.setBold(True)
            self.ui.btnSaveSignal.show()
        else:
            font.setBold(False)
            self.ui.btnSaveSignal.hide()
            for i in range(self.undo_stack.count()):
                cmd = self.undo_stack.command(i)
                if isinstance(cmd, EditSignalAction):
                    # https://github.com/jopohl/urh/issues/570
                    cmd.signal_was_changed = True

        qApp.processEvents()
        self.ui.gvSignal.auto_fit_on_resize_is_blocked = False

        self.ui.lineEditSignalName.setFont(font)

    @pyqtSlot()
    def on_btn_show_hide_start_end_clicked(self):
        show = self.ui.btnShowHideStartEnd.isChecked()
        if show:
            self.ui.btnShowHideStartEnd.setIcon(QIcon.fromTheme("arrow-down-double"))
            self.ui.verticalLayout.insertItem(2, self.ui.additionalInfos)
        else:
            self.ui.btnShowHideStartEnd.setIcon(QIcon.fromTheme("arrow-up-double"))
            self.ui.verticalLayout.removeItem(self.ui.additionalInfos)

        for i in range(self.ui.additionalInfos.count()):
            try:
                self.ui.additionalInfos.itemAt(i).widget().setVisible(show)
            except AttributeError:
                pass

    @pyqtSlot()
    def on_spinbox_tolerance_editing_finished(self):
        if self.signal.tolerance != self.ui.spinBoxTolerance.value():
            self.ui.spinBoxTolerance.blockSignals(True)
            tolerance_action = ChangeSignalParameter(
                signal=self.signal,
                protocol=self.proto_analyzer,
                parameter_name="tolerance",
                parameter_value=self.ui.spinBoxTolerance.value(),
            )
            self.undo_stack.push(tolerance_action)
            self.ui.spinBoxTolerance.blockSignals(False)

    @pyqtSlot()
    def on_spinbox_samples_per_symbol_editing_finished(self):
        if self.signal.samples_per_symbol != self.ui.spinBoxSamplesPerSymbol.value():
            self.ui.spinBoxSamplesPerSymbol.blockSignals(True)
            action = ChangeSignalParameter(
                signal=self.signal,
                protocol=self.proto_analyzer,
                parameter_name="samples_per_symbol",
                parameter_value=self.ui.spinBoxSamplesPerSymbol.value(),
            )
            self.undo_stack.push(action)
            self.ui.spinBoxSamplesPerSymbol.blockSignals(False)

    @pyqtSlot()
    def on_spinbox_bits_per_symbol_editing_finished(self):
        if self.signal.bits_per_symbol != self.ui.spinBoxBitsPerSymbol.value():
            self.ui.spinBoxBitsPerSymbol.blockSignals(True)
            bits_per_symbol_action = ChangeSignalParameter(
                signal=self.signal,
                protocol=self.proto_analyzer,
                parameter_name="bits_per_symbol",
                parameter_value=self.ui.spinBoxBitsPerSymbol.value(),
            )
            self.undo_stack.push(bits_per_symbol_action)
            self.ui.spinBoxBitsPerSymbol.blockSignals(False)

            if self.ui.gvSignal.scene_type == 1:
                self.ui.gvSignal.scene().draw_sep_area(-self.signal.center_thresholds)

            self.set_center_spacing_visibility()

    @pyqtSlot()
    def on_spinbox_center_editing_finished(self):
        if self.signal.center != self.ui.spinBoxCenterOffset.value():
            self.ui.spinBoxCenterOffset.blockSignals(True)
            center_action = ChangeSignalParameter(
                signal=self.signal,
                protocol=self.proto_analyzer,
                parameter_name="center",
                parameter_value=self.ui.spinBoxCenterOffset.value(),
            )
            self.undo_stack.push(center_action)
            self.ui.spinBoxCenterOffset.blockSignals(False)

    @pyqtSlot()
    def on_spinbox_spacing_value_changed(self):
        if self.ui.gvSignal.scene_type == 1:
            thresholds = self.signal.get_thresholds_for_center(
                self.signal.center, self.ui.spinBoxCenterSpacing.value()
            )
            self.ui.gvSignal.scene().draw_sep_area(-thresholds)

    @pyqtSlot()
    def on_spinbox_spacing_editing_finished(self):
        if self.signal.center_spacing != self.ui.spinBoxCenterSpacing.value():
            self.ui.spinBoxCenterSpacing.blockSignals(True)
            center_spacing_action = ChangeSignalParameter(
                signal=self.signal,
                protocol=self.proto_analyzer,
                parameter_name="center_spacing",
                parameter_value=self.ui.spinBoxCenterSpacing.value(),
            )
            self.undo_stack.push(center_spacing_action)
            self.ui.spinBoxCenterSpacing.blockSignals(False)

            if self.ui.gvSignal.scene_type == 1:
                self.ui.gvSignal.scene().draw_sep_area(-self.signal.center_thresholds)

    @pyqtSlot()
    def refresh(self, draw_full_signal=False):
        self.refresh_signal(draw_full_signal=draw_full_signal)
        self.refresh_signal_information(block=True)
        self.show_protocol(refresh=True)

    @pyqtSlot()
    def on_btn_filter_clicked(self):
        if self.apply_filter_to_selection_only.isChecked():
            start, end = (
                self.ui.gvSignal.selection_area.start,
                self.ui.gvSignal.selection_area.end,
            )
        else:
            start, end = 0, self.signal.num_samples

        filter_action = EditSignalAction(
            signal=self.signal,
            mode=EditAction.filter,
            start=start,
            end=end,
            dsp_filter=self.dsp_filter,
            protocol=self.proto_analyzer,
        )
        self.undo_stack.push(filter_action)

    @pyqtSlot()
    def on_configure_filter_action_triggered(self):
        self.filter_dialog.set_dsp_filter_status(self.dsp_filter.filter_type)
        self.filter_dialog.exec()

    @pyqtSlot(Filter)
    def on_filter_dialog_filter_accepted(self, dsp_filter: Filter):
        if dsp_filter is not None:
            self.dsp_filter = dsp_filter
            self.set_filter_button_caption()

    @pyqtSlot()
    def on_spectrogram_update_timer_timeout(self):
        self.draw_spectrogram(show_full_scene=True)

    @pyqtSlot(float)
    def on_gv_spectrogram_y_scale_changed(self, scale: float):
        self.ui.sliderYScale.blockSignals(True)
        self.ui.sliderYScale.setValue(self.ui.sliderYScale.value() * scale)
        self.ui.sliderYScale.blockSignals(False)

    @pyqtSlot(float, float)
    def on_bandpass_filter_triggered(self, f_low: float, f_high: float):
        self.filter_abort_wanted = False

        QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        filter_bw = Filter.read_configured_filter_bw()
        filtered = Array("f", 2 * self.signal.num_samples)
        p = Process(
            target=perform_filter,
            args=(
                filtered,
                self.signal.iq_array.as_complex64(),
                f_low,
                f_high,
                filter_bw,
            ),
        )
        p.daemon = True
        p.start()

        while p.is_alive():
            QApplication.instance().processEvents()

            if self.filter_abort_wanted:
                p.terminate()
                p.join()
                QApplication.instance().restoreOverrideCursor()
                return

            time.sleep(0.1)

        filtered = np.frombuffer(filtered.get_obj(), dtype=np.complex64)
        signal = self.signal.create_new(
            new_data=filtered.astype(np.complex64), new_timestamp=self.signal.timestamp
        )
        signal.name = (
            self.signal.name
            + " filtered with f_low={0:.4n} f_high={1:.4n} bw={2:.4n}".format(
                f_low, f_high, filter_bw
            )
        )
        self.signal_created.emit(signal)
        QApplication.instance().restoreOverrideCursor()

    def on_signal_data_edited(self):
        self.refresh_signal()
        self.ui.gvSpectrogram.scene_manager.samples_need_update = True

    @pyqtSlot()
    def on_signal_sample_rate_changed(self):
        if self.spectrogram_is_active:
            self.__set_selected_bandwidth()
        else:
            self.__set_duration()

        self.show_protocol()  # update times

    @pyqtSlot(int)
    def on_pause_threshold_edited(self, pause_threshold: int):
        if self.signal.pause_threshold != pause_threshold:
            pause_threshold_action = ChangeSignalParameter(
                signal=self.signal,
                protocol=self.proto_analyzer,
                parameter_name="pause_threshold",
                parameter_value=pause_threshold,
            )
            self.undo_stack.push(pause_threshold_action)

    @pyqtSlot(int)
    def on_message_length_divisor_edited(self, message_length_divisor: int):
        if self.signal.message_length_divisor != message_length_divisor:
            message_length_divisor_action = ChangeSignalParameter(
                signal=self.signal,
                protocol=self.proto_analyzer,
                parameter_name="message_length_divisor",
                parameter_value=message_length_divisor,
            )
            self.undo_stack.push(message_length_divisor_action)

    def get_advanced_modulation_settings_dialog(self):
        dialog = AdvancedModulationOptionsDialog(
            self.signal.pause_threshold, self.signal.message_length_divisor, parent=self
        )
        dialog.pause_threshold_edited.connect(self.on_pause_threshold_edited)
        dialog.message_length_divisor_edited.connect(
            self.on_message_length_divisor_edited
        )
        return dialog

    def get_costas_dialog(self):
        dialog = CostaOptionsDialog(self.signal.costas_loop_bandwidth, parent=self)
        dialog.accepted.connect(self.on_costas_dialog_accepted)
        return dialog

    @pyqtSlot()
    def on_costas_dialog_accepted(self):
        sender = self.sender()
        assert isinstance(sender, CostaOptionsDialog)
        self.signal.costas_loop_bandwidth = sender.costas_loop_bandwidth

    @pyqtSlot()
    def on_btn_advanced_modulation_settings_clicked(self):
        if self.ui.cbModulationType.currentText() == "ASK":
            dialog = self.get_advanced_modulation_settings_dialog()
        elif self.ui.cbModulationType.currentText() == "PSK":
            dialog = self.get_costas_dialog()
        else:
            raise ValueError("No additional settings available")
        dialog.exec_()

    @pyqtSlot()
    def on_export_fta_wanted(self):
        try:
            initial_name = self.signal.name + "-spectrogram.ft"
        except Exception as e:
            logger.exception(e)
            initial_name = "spectrogram.ft"

        filename = FileOperator.ask_save_file_name(
            initial_name, caption="Export spectrogram"
        )
        if not filename:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.ui.gvSpectrogram.scene_manager.spectrogram.export_to_fta(
                sample_rate=self.signal.sample_rate,
                filename=filename,
                include_amplitude=filename.endswith(".fta"),
            )
        except Exception as e:
            Errors.exception(e)
        finally:
            QApplication.restoreOverrideCursor()
