import locale
import math

from PyQt5.QtCore import pyqtSignal, QPoint, Qt, QMimeData, pyqtSlot, QRectF, QTimer
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QRegion, QDropEvent, QTextCursor, QContextMenuEvent
from PyQt5.QtWidgets import QFrame, QMessageBox, QHBoxLayout, QVBoxLayout, QGridLayout, QMenu, QWidget, QUndoStack, QApplication

from urh import constants
from urh.SignalSceneManager import SignalSceneManager
from urh.controller.SendRecvDialogController import SendRecvDialogController, Mode
from urh.controller.SignalDetailsController import SignalDetailsController
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.ui.CustomDialog import CustomDialog
from urh.ui.LegendScene import LegendScene
from urh.ui.actions.ChangeSignalParameter import ChangeSignalParameter
from urh.ui.actions.ChangeSignalRange import ChangeSignalRange, RangeAction
from urh.ui.ui_signal_frame import Ui_SignalFrame
from urh.util import FileOperator
from urh.util import FontHelper
from urh.util.Errors import Errors
from urh.util.Formatter import Formatter

locale.setlocale(locale.LC_ALL, '')

class SignalFrameController(QFrame):
    closed = pyqtSignal(QWidget)
    signal_created = pyqtSignal(Signal)
    drag_started = pyqtSignal(QPoint)
    frame_dropped = pyqtSignal(QPoint)
    files_dropped = pyqtSignal(list)
    not_show_again_changed = pyqtSignal()
    signal_drawing_finished = pyqtSignal()
    apply_to_all_clicked = pyqtSignal(Signal)
    sort_action_clicked = pyqtSignal()

    def __init__(self, proto_analyzer: ProtocolAnalyzer, undo_stack: QUndoStack,
                 project_manager, proto_bits=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_SignalFrame()
        self.ui.setupUi(self)

        self.ui.txtEdProto.setFont(FontHelper.getMonospaceFont())
        self.ui.txtEdProto.participants = project_manager.participants
        self.ui.txtEdProto.blocks  = proto_analyzer.blocks

        self.ui.gvSignal.participants = project_manager.participants

        self.ui.btnMinimize.setIcon(QIcon(":/icons/data/icons/downarrow.png"))
        self.is_minimized = False
        self.common_zoom = False
        self.undo_stack = undo_stack
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.project_manager = project_manager

        self.proto_analyzer = proto_analyzer
        self.signal = proto_analyzer.signal if self.proto_analyzer is not None else None
        """:type: Signal """

        self.redraw_timer = QTimer()
        self.redraw_timer.setSingleShot(True)
        self.redraw_timer.setInterval(100)

        self.proto_selection_timer = QTimer()  # For Update Proto Selection from ROI
        self.proto_selection_timer.setSingleShot(True)
        self.proto_selection_timer.setInterval(1)

        # Disabled because never used (see also set_protocol_visibilty())
        self.ui.chkBoxSyncSelection.hide()
        self.ui.btnMinimize.hide()

        if self.signal is not None:
            if self.signal.qad_demod_file_loaded:
                self.ui.lSignalTyp.setText("Quad-Demod Signal (*.wav)")
            elif self.signal.wav_mode:
                self.ui.lSignalTyp.setText("Realpart Signal (*.wav)")
            else:
                self.ui.lSignalTyp.setText("Complex Signal")

            self.ui.gvLegend.hide()
            self.ui.lineEditSignalName.setText(self.signal.name)
            self.ui.lSamplesInView.setText("{0:,}".format(self.signal.num_samples))
            self.ui.lSamplesTotal.setText("{0:,}".format(self.signal.num_samples))
            self.sync_protocol = self.ui.chkBoxSyncSelection.isChecked()
            self.ui.chkBoxSyncSelection.hide()

            self.ui.splitter.setSizes([self.ui.splitter.height(), 0])

            self.protocol_selection_is_updateable = True

            self.scene_creator = SignalSceneManager(self.signal, self)
            self.ui.gvSignal.setScene(self.scene_creator.scene)

            self.jump_sync = True
            self.handle_show_hide_start_end_clicked()

            self.refresh_signal_informations(block=True)
            self.create_connects()
            self.set_protocol_visibilty()

            self.ui.chkBoxShowProtocol.setChecked(True)
            self.set_qad_tooltip(self.signal.noise_treshold)
            self.ui.btnSaveSignal.hide()

            self.show_protocol(refresh=False)

        else:
            self.ui.lSignalTyp.setText("Protocol (*.txt)")

            scene, nsamples = SignalSceneManager.create_rectangle(proto_bits)

            self.ui.lSamplesInView.setText("{0:n}".format(int(nsamples)))
            self.ui.lSamplesTotal.setText("{0:n}".format(int(nsamples)))
            self.ui.gvSignal.setScene(scene)
            self.ui.spinBoxSelectionStart.setMaximum(nsamples)
            self.ui.spinBoxSelectionEnd.setMaximum(nsamples)
            self.ui.btnReplay.hide()

            self.create_connects()

            self.ui.gvSignal.sel_area_active = True

            self.ui.btnSaveSignal.hide()
            self.minimize_maximize()

    def create_connects(self):
        self.ui.spinBoxSelectionStart.valueChanged.connect(self.set_selection_start)
        self.ui.spinBoxSelectionEnd.valueChanged.connect(self.set_selection_end)
        self.ui.gvSignal.set_noise_clicked.connect(self.on_set_noise_in_graphic_view_clicked)
        self.ui.btnCloseSignal.clicked.connect(self.my_close)

        self.ui.btnAutoDetect.clicked.connect(self.on_btn_autodetect_clicked)

        if self.signal is not None:
            self.ui.gvSignal.save_clicked.connect(self.save_signal)

            self.signal.bit_len_changed.connect(self.ui.spinBoxInfoLen.setValue)
            self.signal.qad_center_changed.connect(self.update_qad_center_view)
            self.signal.qad_center_changed.connect(self.ui.spinBoxCenterOffset.setValue)
            self.signal.noise_treshold_changed.connect(self.redraw_noise)
            self.signal.modulation_type_changed.connect(self.show_modulation_type)
            self.signal.tolerance_changed.connect(self.ui.spinBoxTolerance.setValue)
            self.signal.protocol_needs_update.connect(self.refresh_protocol)
            self.signal.data_edited.connect(self.refresh_signal) # Crop/Delete Mute etc.
            self.signal.sample_rate_changed.connect(self.__set_duration)
            self.signal.sample_rate_changed.connect(self.show_protocol)  # Update times

            self.ui.gvSignal.horizontalScrollBar().valueChanged.connect(self.on_signal_scrolled)

            self.signal.saved_status_changed.connect(self.handle_signal_data_changed_before_save)
            self.ui.btnSaveSignal.clicked.connect(self.save_signal)
            self.signal.name_changed.connect(self.ui.lineEditSignalName.setText)
            self.ui.gvLegend.resized.connect(self.handle_gv_legend_resized)

            self.ui.gvSignal.sel_area_width_changed.connect(self.start_proto_selection_timer)
            self.ui.gvSignal.sel_area_start_end_changed.connect(self.start_proto_selection_timer)
            self.proto_selection_timer.timeout.connect(self.update_protocol_selection_from_roi)

            self.ui.lineEditSignalName.editingFinished.connect(self.change_signal_name)
            self.proto_analyzer.qt_signals.protocol_updated.connect(self.on_protocol_updated)
            self.redraw_timer.timeout.connect(self.redraw_signal)

        self.ui.btnReplay.clicked.connect(self.on_btn_replay_clicked)
        self.ui.gvSignal.save_as_clicked.connect(self.save_signal_as)
        self.ui.gvSignal.create_clicked.connect(self.create_new_signal)
        self.ui.gvSignal.show_crop_range_clicked.connect(self.show_autocrop_range)
        self.ui.gvSignal.crop_clicked.connect(self.crop_signal)
        self.ui.gvSignal.zoomed.connect(self.handle_signal_zoomed)
        self.ui.sliderYScale.valueChanged.connect(self.handle_slideryscale_value_changed)
        self.ui.spinBoxXZoom.valueChanged.connect(self.handle_spinbox_xzoom_value_changed)

        self.project_manager.project_updated.connect(self.on_participant_changed)
        self.ui.txtEdProto.participant_changed.connect(self.on_participant_changed)
        self.ui.gvSignal.participant_changed.connect(self.on_participant_changed)

        self.ui.btnInfo.clicked.connect(self.on_info_btn_clicked)

        self.proto_selection_timer.timeout.connect(self.update_nselected_samples)
        self.ui.gvSignal.sel_area_start_end_changed.connect(self.update_selection_area)
        self.ui.cbSignalView.currentIndexChanged.connect(self.on_cb_signal_view_index_changed)

        self.ui.cbModulationType.currentIndexChanged.connect(self.on_cbmodulationtype_index_changed)

        self.ui.chkBoxShowProtocol.stateChanged.connect(self.set_protocol_visibilty)
        self.ui.gvSignal.sep_area_changed.connect(self.set_qad_center)
        self.ui.txtEdProto.proto_view_changed.connect(self.show_protocol)
        self.ui.txtEdProto.show_proto_clicked.connect(self.update_roi_from_protocol_selection)
        self.ui.txtEdProto.show_proto_clicked.connect(self.zoom_to_roi)
        self.ui.gvSignal.sep_area_moving.connect(self.update_legend)
        self.ui.txtEdProto.selectionChanged.connect(self.update_roi_from_protocol_selection)
        self.ui.chkBoxSyncSelection.stateChanged.connect(self.handle_protocol_sync_changed)
        self.ui.gvSignal.deletion_wanted.connect(self.delete_selection)
        self.ui.gvSignal.mute_wanted.connect(self.mute_selection)

        self.ui.spinBoxCenterOffset.editingFinished.connect(self.on_spinBoxCenter_editingFinished)
        self.ui.spinBoxTolerance.editingFinished.connect(self.on_spinBoxTolerance_editingFinished)
        self.ui.spinBoxNoiseTreshold.editingFinished.connect(self.on_spinBoxNoiseTreshold_editingFinished)
        self.ui.spinBoxInfoLen.editingFinished.connect(self.on_spinBoxInfoLen_editingFinished)

        self.ui.btnShowHideStartEnd.clicked.connect(self.handle_show_hide_start_end_clicked)
        self.ui.cbProtoView.currentIndexChanged.connect(self.handle_proto_infos_index_changed)
        self.ui.txtEdProto.deletion_wanted.connect(self.delete_from_protocol_selection)

        self.ui.btnMinimize.clicked.connect(self.minimize_maximize)

    @property
    def proto_view(self):
        return self.ui.txtEdProto.cur_view

    @property
    def signal_widgets(self):
        splitter = self.parent()
        for i in range(splitter.count() - 1):
            yield (splitter.widget(i))

    def refresh_signal_informations(self, block=True):
        self.ui.spinBoxTolerance.blockSignals(block)
        self.ui.spinBoxCenterOffset.blockSignals(block)
        self.ui.spinBoxInfoLen.blockSignals(block)
        self.ui.spinBoxNoiseTreshold.blockSignals(block)
        self.ui.btnAutoDetect.blockSignals(block)

        self.ui.spinBoxTolerance.setValue(self.signal.tolerance)
        self.ui.spinBoxCenterOffset.setValue(self.signal.qad_center)
        self.ui.spinBoxInfoLen.setValue(self.signal.bit_len)
        self.ui.spinBoxNoiseTreshold.setValue(self.signal.noise_treshold)
        self.ui.btnAutoDetect.setChecked(self.signal.auto_detect_on_modulation_changed)
        self.show_modulation_type()

        self.ui.spinBoxTolerance.blockSignals(False)
        self.ui.spinBoxCenterOffset.blockSignals(False)
        self.ui.spinBoxInfoLen.blockSignals(False)
        self.ui.spinBoxNoiseTreshold.blockSignals(False)
        self.ui.btnAutoDetect.blockSignals(False)

    def set_empty_frame_visibilities(self):
        self.ui.lInfoLenText.hide()
        self.ui.spinBoxInfoLen.hide()
        self.ui.spinBoxCenterOffset.hide()
        self.ui.spinBoxTolerance.hide()
        self.ui.chkBoxShowProtocol.hide()
        self.ui.cbProtoView.hide()
        self.ui.lErrorTolerance.hide()
        self.ui.lSignalViewText.hide()
        self.ui.chkBoxSyncSelection.hide()
        self.ui.txtEdProto.hide()
        self.ui.gvLegend.hide()
        self.ui.cbSignalView.hide()
        self.ui.cbModulationType.hide()
        #self.ui.btnCloseSignal.hide()
        self.ui.btnSaveSignal.hide()
        self.ui.btnMinimize.hide()

    @pyqtSlot(float)
    def update_legend(self, y_sep):
        if self.ui.gvLegend.isVisible():
            self.ui.gvLegend.ysep = y_sep
            self.ui.gvLegend.refresh()
        self.ui.spinBoxCenterOffset.blockSignals(True)
        self.ui.spinBoxCenterOffset.setValue(-y_sep)
        self.ui.spinBoxCenterOffset.blockSignals(False)

    def emit_signal_drawing_finished(self):
        self.signal_drawing_finished.emit()

    @pyqtSlot()
    def handle_protocol_sync_changed(self):
        self.sync_protocol = self.ui.chkBoxSyncSelection.isChecked()

    @pyqtSlot()
    def set_protocol_visibilty(self):
        checked = self.ui.chkBoxShowProtocol.isChecked()

        if checked:
            self.show_protocol()
            self.ui.cbProtoView.setEnabled(True)
            # Disabled because never used
            #self.ui.chkBoxSyncSelection.show()
            self.ui.txtEdProto.show()
        else:
            self.ui.txtEdProto.hide()
            self.ui.chkBoxSyncSelection.hide()
            self.ui.cbProtoView.setEnabled(False)

    @pyqtSlot()
    def on_cb_signal_view_index_changed(self):
        self.setCursor(Qt.WaitCursor)

        ind = self.ui.cbSignalView.currentIndex()
        self.scene_creator.scene_type = ind
        gvs = self.ui.gvSignal

        vr = self.ui.gvSignal.view_rect()
        self.scene_creator.init_scene()
        start, end = vr.x(), vr.x() + vr.width()
        self.scene_creator.show_scene_section(start, end, *self.__get_subpath_ranges_and_colors(start, end))

        if ind > 0:
            self.ui.gvLegend.y_scene = self.scene_creator.scene.sceneRect().y()
            self.ui.gvLegend.scene_height = self.scene_creator.scene.sceneRect().height()
            self.ui.gvLegend.refresh()
        else:
            self.ui.gvLegend.hide()

        QApplication.processEvents()
        gvs.autofit_view()
        self.handle_slideryscale_value_changed()  # YScale auf neue Sicht übertragen
        self.unsetCursor()

    @pyqtSlot()
    def on_btn_autodetect_clicked(self):
        self.signal.auto_detect_on_modulation_changed = bool(self.ui.btnAutoDetect.isChecked())
        if self.ui.btnAutoDetect.isChecked():
            self.signal.auto_detect()

    @pyqtSlot()
    def on_btn_replay_clicked(self):
        pmngr = self.project_manager
        dialog = SendRecvDialogController(pmngr.frequency, pmngr.sample_rate,
                                          pmngr.bandwidth, pmngr.gain, pmngr.device,
                                          Mode.send, modulated_data=self.signal.data, parent=self)
        if dialog.has_empty_device_list:
            Errors.no_device()
            dialog.close()
            return

        dialog.recording_parameters.connect(pmngr.set_recording_parameters)
        dialog.show()

    def update_nselected_samples(self):
        self.ui.lNumSelectedSamples.setText(str(abs(int(self.ui.gvSignal.selection_area.width))))
        self.__set_duration()


    @pyqtSlot(int, int)
    def update_selection_area(self, start, end):
        # if start > end:
        #     start, end = end, start

        self.ui.lNumSelectedSamples.setText(str(end - start))
        self.__set_duration()
        self.ui.spinBoxSelectionStart.blockSignals(True)
        self.ui.spinBoxSelectionStart.setValue(start)
        self.ui.spinBoxSelectionStart.blockSignals(False)
        self.ui.spinBoxSelectionEnd.blockSignals(True)
        self.ui.spinBoxSelectionEnd.setValue(end)
        self.ui.spinBoxSelectionEnd.blockSignals(False)

    def change_signal_name(self):
        self.signal.name = self.ui.lineEditSignalName.text()

    def __set_duration(self):  # On Signal Sample Rate changed
        try:
            nsamples = int(self.ui.lNumSelectedSamples.text())
        except ValueError:
            return

        if self.signal:
            t = nsamples / self.signal.sample_rate
            self.ui.lDuration.setText(Formatter.science_time(t))


    @pyqtSlot()
    def handle_signal_zoomed(self):
        gvs = self.ui.gvSignal
        self.ui.lSamplesInView.setText("{0:n}".format(int(gvs.view_rect().width())))
        self.ui.spinBoxXZoom.blockSignals(True)
        self.ui.spinBoxXZoom.setValue(int(gvs.sceneRect().width() / gvs.view_rect().width() * 100))
        self.ui.spinBoxXZoom.blockSignals(False)
        self.redraw_timer.start()

    def handle_spinbox_xzoom_value_changed(self):
        gvs = self.ui.gvSignal
        zoom_factor = self.ui.spinBoxXZoom.value() / 100
        current_factor = gvs.sceneRect().width() / gvs.view_rect().width()
        gvs.zoom(zoom_factor / current_factor)

    def handle_slideryscale_value_changed(self):
        try:
            gvs = self.ui.gvSignal
            yscale = self.ui.sliderYScale.value()
            current_factor = gvs.sceneRect().height() / gvs.view_rect().height()
            gvs.scale(1, yscale / current_factor)
            x, w = self.ui.gvSignal.view_rect().x(), self.ui.gvSignal.view_rect().width()
            gvs.centerOn(x + w / 2, gvs.y_center)
        except ZeroDivisionError:
            pass

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
        if start < end:
            new_signal = self.signal.create_new(start, end)
            self.signal_created.emit(new_signal)
        else:
            Errors.empty_selection()



    def my_close(self):
        settings = constants.SETTINGS
        try:
            not_show = settings.value('not_show_close_dialog', type=bool)
        except TypeError:
            not_show = False

        if not not_show:
            #ok, notshowagain = CloseDialog.dialog(self)
            ok, notshowagain = CustomDialog.dialog(self, "Do you want to close?", "close")
            settings.setValue("not_show_close_dialog", notshowagain)
            self.not_show_again_changed.emit()
            if not ok:
                return

        self.closed.emit(self)
        #self.signal.deleteLater()
        #self.scene_creator.deleteLater()
        #

    @pyqtSlot()
    def on_set_noise_in_graphic_view_clicked(self):
        self.setCursor(Qt.WaitCursor)
        start = self.ui.gvSignal.selection_area.x
        end = start + self.ui.gvSignal.selection_area.width

        new_tresh = self.signal.calc_noise_treshold(start, end)
        self.ui.spinBoxNoiseTreshold.setValue(new_tresh)
        self.ui.spinBoxNoiseTreshold.editingFinished.emit()
        self.unsetCursor()

    def redraw_noise(self):
        self.ui.spinBoxNoiseTreshold.setValue(self.signal.noise_treshold)
        minimum = self.signal.noise_min_plot
        maximum = self.signal.noise_max_plot
        if self.ui.cbSignalView.currentIndex() == 0:
            # Draw Noise only in Analog View
            self.ui.gvSignal.scene().draw_noise_area(minimum, maximum - minimum)

    @pyqtSlot()
    def set_selection_start(self):
        if self.ui.gvSignal.sel_area_active:
            self.ui.gvSignal.set_selection_area(x=self.ui.spinBoxSelectionStart.value())
            self.ui.gvSignal.selection_area.finished = True
            self.ui.gvSignal.emit_sel_area_width_changed()

    @pyqtSlot()
    def set_selection_end(self):
        if self.ui.gvSignal.sel_area_active:
            self.ui.gvSignal.set_selection_area(
                w=self.ui.spinBoxSelectionEnd.value() - self.ui.spinBoxSelectionStart.value())
            self.ui.gvSignal.selection_area.finished = True
            self.ui.gvSignal.emit_sel_area_width_changed()

    def save_signal(self):
        if len(self.signal.filename) > 0:
            self.signal.save()
        else:
            self.save_signal_as()

    def save_signal_as(self):
        filename = FileOperator.get_save_file_name(self.signal.filename, wav_only=self.signal.wav_mode, parent=self)
        if filename:
            try:
                self.signal.save_as(filename)
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error saving signal"), e.args[0])

    def crop_signal(self):
        gvs = self.ui.gvSignal
        if not gvs.selection_area.is_empty:
            w = gvs.sceneRect().width()
            start = gvs.selection_area.x
            end = start + gvs.selection_area.width
            if end < start:
                start, end = end, start

            crop_action = ChangeSignalRange(signal=self.signal, protocol=self.proto_analyzer, start=start, end=end, mode=RangeAction.crop)
            self.undo_stack.push(crop_action)
            # self.signal.crop(start, end)
            gvs.zoom((end-start)/w, supress_signal=True) # Zoomlevel von VorCrop auf NachCrop übertragen

    def show_autocrop_range(self):
        start = self.signal.get_signal_start()
        end = self.signal.get_signal_end()

        self.ui.gvSignal.set_selection_area(start, end - start)
        self.ui.gvSignal.selection_area.finished = True
        self.ui.gvSignal.emit_sel_area_width_changed()

    def draw_signal(self, full_signal=False):
        gvs = self.ui.gvSignal
        gv_legend = self.ui.gvLegend
        gv_legend.ysep = -self.signal.qad_center

        # Save current visible region for restoring it after drawing
        y, h = gvs.sceneRect().y(), gvs.sceneRect().height()
        x, w = gvs.view_rect().x(), gvs.view_rect().width()

        self.scene_creator.scene_type = self.ui.cbSignalView.currentIndex()
        self.scene_creator.init_scene()
        if full_signal:
            gvs.draw_full_signal()
        else:
            self.display_scene()

        legend = LegendScene()
        legend.setBackgroundBrush(constants.BGCOLOR)
        legend.setSceneRect(0, self.scene_creator.scene.sceneRect().y(), gv_legend.width(),
                            self.scene_creator.scene.sceneRect().height())
        legend.draw_one_zero_arrows(-self.signal.qad_center)
        gv_legend.setScene(legend)

        num_samples = self.signal.num_samples
        self.ui.spinBoxSelectionStart.setMaximum(num_samples)
        self.ui.spinBoxSelectionEnd.setMaximum(num_samples)
        gvs.nsamples = num_samples

        gvs.sel_area_active = True
        gvs.y_sep = -self.signal.qad_center

        if not full_signal:
            # Restore Zoom
            w = w if w < self.signal.num_samples else self.signal.num_samples
            gvs.fitInView(QRectF(x, y, w, h))
            gvs.centerOn(x + w / 2, gvs.y_center)

    def restore_protocol_selection(self, sel_start, sel_end, start_block, end_block, old_protoview):
        if old_protoview == self.proto_view:
            return

        self.protocol_selection_is_updateable = False
        sel_start = int(self.proto_analyzer.convert_index(sel_start, old_protoview, self.proto_view, True)[0])
        sel_end = int(math.ceil(self.proto_analyzer.convert_index(sel_end, old_protoview, self.proto_view, True)[1]))


        c = self.ui.txtEdProto.textCursor()

        c.setPosition(0)
        cur_block = 0
        i = 0
        text = self.ui.txtEdProto.toPlainText()
        while cur_block < start_block:
            if text[i] == "\n":
                cur_block += 1
            i += 1

        c.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, i)
        c.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, sel_start)
        text = text[i:]
        i = 0
        while cur_block < end_block:
            if text[i] == "\n":
                cur_block += 1
            i += 1

        c.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, i)
        c.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, sel_end)

        self.ui.txtEdProto.setTextCursor(c)

        self.protocol_selection_is_updateable = True

    def update_protocol(self):
        self.ui.txtEdProto.setPlainText("Loading..")
        self.ui.txtEdProto.setEnabled(False)
        QApplication.processEvents()

        self.proto_analyzer.get_protocol_from_signal()

    def on_protocol_updated(self):
        self.redraw_signal() # Participants may have changed
        self.ui.txtEdProto.setEnabled(True)
        cur_scroll = self.ui.txtEdProto.verticalScrollBar().value()
        self.ui.txtEdProto.setHtml(self.proto_analyzer.plain_to_html(self.proto_view))
        self.ui.txtEdProto.verticalScrollBar().setValue(cur_scroll)

    def show_protocol(self, old_view=-1, refresh=False):
        if not self.proto_analyzer:
            return

        chkd = self.ui.chkBoxShowProtocol.isChecked()
        if not chkd:
            return

        if old_view == -1:
            old_view = self.ui.cbProtoView.currentIndex()

        if self.proto_analyzer.blocks is None or refresh:
            self.update_protocol()
        else:
            # Keep things synchronized and restore selection
            self.ui.txtEdProto.blockSignals(True)
            self.ui.cbProtoView.blockSignals(True)
            self.ui.cbProtoView.setCurrentIndex(self.proto_view)
            self.ui.cbProtoView.blockSignals(False)

            start_block = 0
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
                    start_block += 1
                    read_pause = False

            sel_end = self.ui.txtEdProto.textCursor().selectionEnd()
            text = self.ui.txtEdProto.toPlainText()[self.ui.txtEdProto.textCursor().selectionStart():sel_end]
            end_block = 0
            sel_end = 0
            read_pause = False
            for t in text:
                if t == "\t":
                    read_pause = True

                if not read_pause:
                    sel_end += 1

                if t == "\n":
                    sel_end = 0
                    end_block += 1
                    read_pause = False

            self.ui.txtEdProto.setHtml(self.proto_analyzer.plain_to_html(self.proto_view))
            #self.ui.txtEdProto.setPlainText(self.proto_analyzer.plain_to_string(self.proto_view))
            self.restore_protocol_selection(sel_start, sel_end, start_block, end_block, old_view)

            self.ui.txtEdProto.blockSignals(False)

    @pyqtSlot()
    def refresh_protocol(self):
        self.show_protocol(refresh=True)

    @pyqtSlot()
    def handle_proto_infos_index_changed(self):
        old_view = self.ui.txtEdProto.cur_view
        self.ui.txtEdProto.cur_view = self.ui.cbProtoView.currentIndex()
        self.show_protocol(old_view=old_view)

    @pyqtSlot(float)
    def set_qad_center(self, th):
        self.ui.spinBoxCenterOffset.setValue(th)
        self.ui.spinBoxCenterOffset.editingFinished.emit()

    def set_roi_from_protocol_analysis(self, start_block, start_pos, end_block, end_pos, view_type):
        if not self.proto_analyzer:
            return

        if not self.ui.chkBoxShowProtocol.isChecked():
            self.ui.chkBoxShowProtocol.setChecked(True)
            self.set_protocol_visibilty()

        self.ui.cbProtoView.setCurrentIndex(view_type)

        if view_type == 1:
            # Hex View
            start_pos *= 4
            end_pos *= 4
        elif view_type == 2:
            # ASCII View
            start_pos *= 8
            end_pos *= 8

        samplepos, nsamples = self.proto_analyzer.get_samplepos_of_bitseq(start_block, start_pos,
                                                                          end_block, end_pos,
                                                                          True)
        self.protocol_selection_is_updateable = False
        if samplepos != -1:
            if self.jump_sync and self.sync_protocol:
                self.ui.gvSignal.centerOn(samplepos, self.ui.gvSignal.y_center)
                self.ui.gvSignal.set_selection_area(samplepos, nsamples)
                self.ui.gvSignal.centerOn(samplepos + nsamples, self.ui.gvSignal.y_center)
            else:
                self.ui.gvSignal.set_selection_area(samplepos, nsamples)

            self.ui.gvSignal.zoom_to_selection(samplepos, samplepos + nsamples)
        else:
            self.ui.gvSignal.set_selection_area(0, 0)

        self.protocol_selection_is_updateable = True
        self.update_protocol_selection_from_roi()

    @pyqtSlot()
    def update_roi_from_protocol_selection(self):
        txtEdit = self.ui.txtEdProto
        end_pos = txtEdit.textCursor().selectionEnd()
        start_pos = txtEdit.textCursor().selectionStart()
        forward_selection = txtEdit.textCursor().anchor() <= txtEdit.textCursor().position()

        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos

        start_block = txtEdit.toPlainText()[:start_pos].count("\n")
        end_block = start_block + txtEdit.toPlainText()[start_pos:end_pos].count("\n")
        newline_pos = txtEdit.toPlainText()[:start_pos].rfind("\n")

        if newline_pos != -1:
            start_pos -= (newline_pos + 1)

        newline_pos = txtEdit.toPlainText()[:end_pos].rfind("\n")
        if newline_pos != -1:
            end_pos -= (newline_pos + 1)

        if txtEdit.cur_view == 1:
            # Hex View
            start_pos *= 4
            end_pos *= 4
        elif txtEdit.cur_view == 2:
            # ASCII View
            start_pos *= 8
            end_pos *= 8

        try:
            include_last_pause = False
            s = txtEdit.textCursor().selectionStart()
            e = txtEdit.textCursor().selectionEnd()
            if s > e:
                s,e = e,s

            selected_text = txtEdit.toPlainText()[s:e]

            last_newline = selected_text.rfind("\n")
            if last_newline == -1:
                last_newline = 0

            if selected_text.endswith(" "):
               end_pos -= 1
            elif selected_text.endswith(" \t"):
                end_pos -= 2

            if "[" in selected_text[last_newline:]:
                include_last_pause = True

            samplepos, nsamples = self.proto_analyzer.get_samplepos_of_bitseq(start_block, start_pos, end_block,
                                                                              end_pos, include_last_pause)

        except IndexError:
            return

        self.ui.gvSignal.blockSignals(True)
        if samplepos != -1:
            if self.jump_sync and self.sync_protocol:
                self.ui.gvSignal.centerOn(samplepos, self.ui.gvSignal.y_center)
                self.ui.gvSignal.set_selection_area(samplepos, nsamples)
                if forward_selection: # Forward Selection --> Center ROI to End of Selection
                    self.ui.gvSignal.centerOn(samplepos + nsamples, self.ui.gvSignal.y_center)
                else: # Backward Selection --> Center ROI to Start of Selection
                    self.ui.gvSignal.centerOn(samplepos, self.ui.gvSignal.y_center)
            else:
                self.ui.gvSignal.set_selection_area(samplepos, nsamples)
        else:
            self.ui.gvSignal.set_selection_area(0, 0)
        self.ui.gvSignal.blockSignals(False)

        self.update_nselected_samples()

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

        if protocol.blocks is None or not self.ui.chkBoxShowProtocol.isChecked():
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
            startblock, startindex, endblock, endindex = protocol.get_bitseq_from_selection(
                start, w,
                self.signal.bit_len)
        except IndexError:
            c.clearSelection()
            self.ui.txtEdProto.setTextCursor(c)
            self.jump_sync = True
            self.ui.txtEdProto.blockSignals(False)
            return

        if startblock == -1 or endindex == -1 or startindex == -1 or endblock == -1:
            c.clearSelection()
            self.ui.txtEdProto.setTextCursor(c)
            self.jump_sync = True
            self.ui.txtEdProto.blockSignals(False)
            return

        startindex = int(
            protocol.convert_index(startindex, 0, self.proto_view, True)[0])
        endindex = int(math.ceil(
            protocol.convert_index(endindex, 0, self.proto_view, True)[1]))
        text = self.ui.txtEdProto.toPlainText()
        n = 0
        blockpos = 0
        c.setPosition(0)

        for i, t in enumerate(text):
            blockpos += 1
            if t == "\n":
                n += 1
                blockpos = 0

            if n == startblock and blockpos == startindex:
                c.setPosition(i+1, QTextCursor.MoveAnchor)

            if n == endblock and blockpos == endindex:
                c.setPosition(i, QTextCursor.KeepAnchor)
                break

        self.ui.txtEdProto.setTextCursor(c)
        self.ui.txtEdProto.blockSignals(False)
        self.jump_sync = True

    def refresh_signal(self, draw_full_signal=False):
        gvs = self.ui.gvSignal
        gvs.sel_area_active = False
        self.draw_signal(draw_full_signal)

        self.ui.lSamplesInView.setText("{0:n}".format(int(gvs.view_rect().width())))
        self.ui.lSamplesTotal.setText("{0:n}".format(self.signal.num_samples))

        selected = 0
        if not self.ui.gvSignal.selection_area.is_empty:
            selected = self.ui.gvSignal.selection_area.width

        self.ui.lNumSelectedSamples.setText(str(selected))
        self.__set_duration()

        self.set_qad_tooltip(self.signal.noise_treshold)
        gvs.sel_area_active = True

    @pyqtSlot()
    def refresh(self, draw_full_signal=False):
        self.refresh_signal(draw_full_signal=draw_full_signal)
        self.refresh_signal_informations(block=True)
        self.show_protocol(refresh=True)


    def delete_selection(self, start, end):
        self.ui.gvSignal.clear_selection()
        del_action = ChangeSignalRange(signal=self.signal, protocol=self.proto_analyzer, start=start, end=end, mode=RangeAction.delete)
        self.undo_stack.push(del_action)
        self.ui.gvSignal.centerOn(start, self.ui.gvSignal.y_center)

    def mute_selection(self, start: int, end: int):
        mute_action = ChangeSignalRange(signal=self.signal, protocol=self.proto_analyzer, start=start, end=end, mode=RangeAction.mute)
        self.undo_stack.push(mute_action)

    @pyqtSlot()
    def on_spinBoxCenter_editingFinished(self):
        if self.signal.qad_center != self.ui.spinBoxCenterOffset.value():
            self.ui.spinBoxCenterOffset.blockSignals(True)
            center_action = ChangeSignalParameter(signal=self.signal, protocol=self.proto_analyzer,
                                                  parameter_name="qad_center", parameter_value=self.ui.spinBoxCenterOffset.value())
            self.undo_stack.push(center_action)
            self.disable_auto_detection()

    def update_qad_center_view(self):
        self.ui.gvSignal.y_sep = -self.signal.qad_center
        self.ui.gvLegend.ysep = -self.signal.qad_center

        if self.ui.cbSignalView.currentIndex() > 0:
            self.scene_creator.scene.draw_sep_area(-self.signal.qad_center)
            self.ui.gvLegend.refresh()
        self.ui.spinBoxCenterOffset.blockSignals(False)

    @pyqtSlot()
    def on_spinBoxTolerance_editingFinished(self):
        if self.signal.tolerance != self.ui.spinBoxTolerance.value():
            self.ui.spinBoxTolerance.blockSignals(True)
            tolerance_action = ChangeSignalParameter(signal=self.signal, protocol=self.proto_analyzer,
                                                  parameter_name="tolerance",
                                                  parameter_value=self.ui.spinBoxTolerance.value())
            self.undo_stack.push(tolerance_action)
            self.ui.spinBoxTolerance.blockSignals(False)
            self.disable_auto_detection()

    @pyqtSlot()
    def on_spinBoxInfoLen_editingFinished(self):
        if self.signal.bit_len != self.ui.spinBoxInfoLen.value():
            self.ui.spinBoxInfoLen.blockSignals(True)
            bitlen_action = ChangeSignalParameter(signal=self.signal, protocol=self.proto_analyzer,
                                                     parameter_name="bit_len",
                                                     parameter_value=self.ui.spinBoxInfoLen.value())
            self.undo_stack.push(bitlen_action)
            self.ui.spinBoxInfoLen.blockSignals(False)
            self.disable_auto_detection()

    def on_spinBoxNoiseTreshold_editingFinished(self):
        if self.signal is not None and self.signal.noise_treshold != self.ui.spinBoxNoiseTreshold.value():
            noise_action = ChangeSignalParameter(signal=self.signal, protocol=self.proto_analyzer,
                                                  parameter_name="noise_treshold",
                                                  parameter_value=self.ui.spinBoxNoiseTreshold.value())
            self.undo_stack.push(noise_action)
            self.disable_auto_detection()


    @pyqtSlot()
    def handle_show_hide_start_end_clicked(self):
        if self.ui.btnShowHideStartEnd.text() == "+":
            self.ui.btnShowHideStartEnd.setText("-")
            self.ui.verticalLayout.insertItem(2, self.ui.additionalInfos)
            self.ui.lStart.show()
            self.ui.lEnd.show()
            self.ui.lSamplesInView.show()
            self.ui.lStrich.show()
            self.ui.lSamplesTotal.show()
            self.ui.lSamplesViewText.show()
            self.ui.spinBoxSelectionStart.show()
            self.ui.spinBoxSelectionEnd.show()

        else:
            self.ui.btnShowHideStartEnd.setText("+")
            self.ui.lStart.hide()
            self.ui.lEnd.hide()
            self.ui.lSamplesInView.hide()
            self.ui.lStrich.hide()
            self.ui.lSamplesTotal.hide()
            self.ui.lSamplesViewText.hide()
            self.ui.spinBoxSelectionStart.hide()
            self.ui.spinBoxSelectionEnd.hide()
            self.ui.verticalLayout.removeItem(self.ui.additionalInfos)

    def display_scene(self):
        self.scene_creator.scene_type = self.ui.cbSignalView.currentIndex()
        vr = self.ui.gvSignal.view_rect()
        start, end = vr.x(), vr.x() + vr.width()
        self.scene_creator.show_scene_section(start, end, *self.__get_subpath_ranges_and_colors(start, end))

    def delete_from_protocol_selection(self):
        if not self.ui.gvSignal.selection_area.is_empty:
            start = self.ui.gvSignal.selection_area.x
            end = self.ui.gvSignal.selection_area.end
            self.delete_selection(start, end)

    @pyqtSlot()
    def handle_gv_legend_resized(self):
        if self.ui.gvLegend.isVisible():
            self.ui.gvLegend.y_zoom_factor = self.ui.gvSignal.transform().m22()
            self.ui.gvLegend.refresh()
            self.ui.gvLegend.translate(0, 1) # Resize verschiebt sonst Pfeile


    def minimize_maximize(self):
        elems = vars(self.ui)

        if not self.is_minimized:
            for name, widget in elems.items():
                if name != "btnMinimize" and type(widget) not in (QHBoxLayout, QVBoxLayout, QGridLayout)\
                        and name not in ("lSignalNr", "lineEditSignalName", "btnCloseSignal", "lSignalTyp", "btnSaveSignal"):
                    widget.hide()

            self.ui.btnMinimize.setIcon(QIcon(":/icons/data/icons/uparrow.png"))
            self.is_minimized = True
            self.setFixedHeight(65)
        else:
            show_start_end = self.ui.btnShowHideStartEnd.text() == "-"
            for name, widget in elems.items():
                if type(widget) in (QHBoxLayout, QVBoxLayout, QGridLayout):
                    continue
                if not self.ui.chkBoxShowProtocol.isChecked() and name in ("txtEdProto", "chkBoxSyncSelection"):
                    continue
                if not show_start_end and name in ("lStart", "spinBoxSelectionStart", "lEnd", "spinBoxSelectionEnd", "lSamplesInView",
                "lStrich", "lSamplesTotal", "lSamplesViewText", "btnSaveSignal"):
                    continue

                if not self.signal.changed and name == "btnSaveSignal":
                    continue

                if name == "gvLegend":
                    continue

                widget.show()

            self.ui.btnMinimize.setIcon(QIcon(":/icons/data/icons/downarrow.png"))
            self.is_minimized = False
            self.setMinimumHeight(0)
            self.setMaximumHeight(20000)

            if self.ui.cbSignalView.currentIndex() > 0:
                self.ui.gvLegend.refresh()
            if self.signal is None:
                self.set_empty_frame_visibilities()

    def set_qad_tooltip(self, noise_threshold):
        self.ui.cbSignalView.setToolTip(
            "<html><head/><body><p>Choose the view of your signal.</p><p>The quadrature demodulation uses a <span style=\" text-decoration: underline;\">threshold of magnitude,</span> to <span style=\" font-weight:600;\">supress noise</span>. All samples with a magnitude lower than this threshold will be eliminated (set to <span style=\" font-style:italic;\">-127</span>) after demod.</p><p>Tune this value by selecting a <span style=\" font-style:italic;\">noisy area</span> and mark it as noise using <span style=\" text-decoration: underline;\">context menu</span>.</p><p>Current noise threshold is: <b>" + str(
                noise_threshold) + "</b></p></body></html>")

    @pyqtSlot()
    def handle_signal_data_changed_before_save(self):
        font = self.ui.lineEditSignalName.font()
        """:type: QFont """
        if self.signal.changed:
            font.setBold(True)
            self.ui.btnSaveSignal.show()
        else:
            font.setBold(False)
            self.ui.btnSaveSignal.hide()
        self.ui.lineEditSignalName.setFont(font)

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self.signal is None:
            return

        menu = QMenu()
        applyToAllAction = menu.addAction(self.tr("Apply values (BitLen, 0/1-Threshold, Tolerance) to all signals"))
        menu.addSeparator()
        autoDetectAction = menu.addAction(self.tr("Auto-Detect signal parameters"))
        #sortAction = menu.addAction("Sort Frames by name")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == applyToAllAction:
            self.setCursor(Qt.WaitCursor)
            self.apply_to_all_clicked.emit(self.signal)
            self.unsetCursor()
        elif action == autoDetectAction:
            self.setCursor(Qt.WaitCursor)
            self.signal.auto_detect()
            self.unsetCursor()
        #elif action == sortAction:
        #    self.sort_action_clicked.emit()

    def zoom_all_signals(self, factor):
        """
        This method is used, when 'common Zoom' is enabled
        :param factor:
        :return:
        """
        for sWidget in self.signal_widgets:
            gvs = sWidget.ui.gvSignal
            gvs.zoom(factor)

        for sWidget in self.signal_widgets:
            if sWidget == self:
                continue

    def on_signal_scrolled(self):
        self.redraw_timer.start(0)

    def redraw_signal(self):
        vr = self.ui.gvSignal.view_rect()
        start, end = vr.x(), vr.x() + vr.width()
        self.scene_creator.show_scene_section(start, end, *self.__get_subpath_ranges_and_colors(start, end))

    def __get_subpath_ranges_and_colors(self, start: float, end: float):
        subpath_ranges = []
        colors = []
        start = int(start)
        end = int(end) if end == int(end) else int(end) + 1

        if not self.proto_analyzer.blocks:
            return None, None

        for block in self.proto_analyzer.blocks:
            if block.bit_sample_pos[-2] < start:
                continue

            color = None if block.participant is None else constants.PARTICIPANT_COLORS[block.participant.color_index]

            # Append the pause until first bit of block
            subpath_ranges.append((start, block.bit_sample_pos[0]))
            if start < block.bit_sample_pos[0]:
                colors.append(None)
            else:
                colors.append(color) # Zoomed inside a block

            if block.bit_sample_pos[-2] > end:
                subpath_ranges.append((block.bit_sample_pos[0], end))
                colors.append(color)
                break

            # Data part of the block
            subpath_ranges.append((block.bit_sample_pos[0], block.bit_sample_pos[-2]))
            colors.append(color)

            start = block.bit_sample_pos[-2] + 1

        subpath_ranges = subpath_ranges if subpath_ranges else None
        colors = colors if colors else None
        return subpath_ranges, colors

    def on_info_btn_clicked(self):
        sdc = SignalDetailsController(self.signal, self)
        sdc.exec_()

    def show_modulation_type(self):
        self.ui.cbModulationType.blockSignals(True)
        self.ui.cbModulationType.setCurrentIndex(self.signal.modulation_type)
        self.ui.cbModulationType.blockSignals(False)

    def disable_auto_detection(self):
        """
        Disable auto detection when user manually edited a value

        :return:
        """
        if self.signal.auto_detect_on_modulation_changed:
            self.signal.auto_detect_on_modulation_changed = False
            self.ui.btnAutoDetect.setChecked(False)

    def on_participant_changed(self):
        if self.proto_analyzer:
            self.proto_analyzer.qt_signals.protocol_updated.emit()

    def on_cbmodulationtype_index_changed(self):
        modulation_action = ChangeSignalParameter(signal=self.signal, protocol=self.proto_analyzer,
                                              parameter_name="modulation_type",
                                              parameter_value=self.ui.cbModulationType.currentIndex())

        self.undo_stack.push(modulation_action)