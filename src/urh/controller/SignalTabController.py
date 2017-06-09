from PyQt5.QtCore import QPoint, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtWidgets import QSplitter, QWidget, QVBoxLayout, QSizePolicy, QUndoStack, QCheckBox, QMessageBox

from urh import constants

from urh.controller.SignalFrameController import SignalFrameController
from urh.signalprocessing.Signal import Signal
from urh.ui.ui_tab_interpretation import Ui_Interpretation


class SignalTabController(QWidget):
    frame_closed = pyqtSignal(SignalFrameController)
    not_show_again_changed = pyqtSignal()
    signal_created = pyqtSignal(Signal)
    files_dropped = pyqtSignal(list)
    frame_was_dropped = pyqtSignal(int, int)

    @property
    def num_frames(self):
        return self.splitter.count() - 1

    @property
    def signal_frames(self):
        """

        :rtype: list of SignalFrameController
        """
        return [self.splitter.widget(i) for i in range(self.num_frames)]

    @property
    def signal_undo_stack(self):
        return self.undo_stack

    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.ui = Ui_Interpretation()
        self.ui.setupUi(self)
        self.splitter = QSplitter()
        self.splitter.setStyleSheet("QSplitter::handle:vertical {\nmargin: 4px 0px; background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, \nstop:0 rgba(255, 255, 255, 0), \nstop:0.5 rgba(100, 100, 100, 100), \nstop:1 rgba(255, 255, 255, 0));\n	image: url(:/icons/data/icons/splitter_handle.png);\n}")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setChildrenCollapsible(True)
        self.splitter.setHandleWidth(6)

        placeholder_widget = QWidget()
        placeholder_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.undo_stack = QUndoStack()
        self.project_manager = project_manager

        self.splitter.addWidget(placeholder_widget)
        self.signal_vlay = QVBoxLayout()
        self.signal_vlay.setContentsMargins(0,0,0,0)
        self.signal_vlay.addWidget(self.splitter)
        self.ui.scrlAreaSignals.setLayout(self.signal_vlay)

        self.drag_pos = None

    def on_files_dropped(self, files):
        self.files_dropped.emit(files)

    def close_frame(self, frame:SignalFrameController):
        self.frame_closed.emit(frame)

    def add_signal_frame(self, proto_analyzer):
        sig_frame = SignalFrameController(proto_analyzer, self.undo_stack, self.project_manager, parent=self)
        sframes = self.signal_frames


        if len(proto_analyzer.signal.filename) == 0:
            # new signal from "create signal from selection"
            sig_frame.ui.btnSaveSignal.show()

        self.__create_connects_for_signal_frame(signal_frame=sig_frame)
        sig_frame.signal_created.connect(self.signal_created.emit)
        sig_frame.not_show_again_changed.connect(self.not_show_again_changed.emit)
        sig_frame.ui.gvSignal.shift_state_changed.connect(self.set_shift_statuslabel)
        sig_frame.ui.lineEditSignalName.setToolTip(self.tr("Sourcefile: ") + proto_analyzer.signal.filename)
        sig_frame.apply_to_all_clicked.connect(self.on_apply_to_all_clicked)

        prev_signal_frame = sframes[-1] if len(sframes) > 0 else None
        if prev_signal_frame is not None and hasattr(prev_signal_frame, "ui"):
            sig_frame.ui.cbProtoView.setCurrentIndex(prev_signal_frame.ui.cbProtoView.currentIndex())

        sig_frame.blockSignals(True)

        if proto_analyzer.signal.qad_demod_file_loaded:
            sig_frame.ui.cbSignalView.setCurrentIndex(1)
            sig_frame.ui.cbSignalView.setDisabled(True)

        self.splitter.insertWidget(self.num_frames, sig_frame)
        sig_frame.blockSignals(False)

        default_view = constants.SETTINGS.value('default_view', 0, int)
        sig_frame.ui.cbProtoView.setCurrentIndex(default_view)

        return sig_frame

    def __create_connects_for_signal_frame(self, signal_frame: SignalFrameController):
        signal_frame.hold_shift = constants.SETTINGS.value('hold_shift_to_drag', False, type=bool)
        signal_frame.drag_started.connect(self.frame_dragged)
        signal_frame.frame_dropped.connect(self.frame_dropped)
        signal_frame.files_dropped.connect(self.on_files_dropped)
        signal_frame.closed.connect(self.close_frame)

    def add_empty_frame(self, filename: str, proto):
        sig_frame = SignalFrameController(proto_analyzer=proto, undo_stack=self.undo_stack,
                                          project_manager=self.project_manager, proto_bits=proto.decoded_proto_bits_str,
                                          parent=self)

        sig_frame.ui.lineEditSignalName.setText(filename)
        sig_frame.setMinimumHeight(sig_frame.height())
        sig_frame.set_empty_frame_visibilities()
        self.__create_connects_for_signal_frame(signal_frame=sig_frame)

        self.splitter.insertWidget(self.num_frames, sig_frame)

        return sig_frame

    def set_frame_numbers(self):
        for i, f in enumerate(self.signal_frames):
            f.ui.lSignalNr.setText("{0:d}:".format(i + 1))

    @pyqtSlot()
    def save_all(self):
        if self.num_frames == 0:
            return

        settings = constants.SETTINGS
        try:
            not_show = settings.value('not_show_save_dialog', type=bool, defaultValue=False)
        except TypeError:
            not_show = False

        if not not_show:
            cb = QCheckBox("Don't ask me again.")
            msg_box = QMessageBox(QMessageBox.Question, self.tr("Confirm saving all signals"),
                                  self.tr("All changed signal files will be overwritten. OK?"))
            msg_box.addButton(QMessageBox.Yes)
            msg_box.addButton(QMessageBox.No)
            msg_box.setCheckBox(cb)

            reply = msg_box.exec()
            not_show_again = cb.isChecked()
            settings.setValue("not_show_save_dialog", not_show_again)
            self.not_show_again_changed.emit()

            if reply != QMessageBox.Yes:
                return

        for f in self.signal_frames:
            if f.signal is None or f.signal.filename == "":
                continue
            f.signal.save()

    @pyqtSlot()
    def close_all(self):
        for f in self.signal_frames:
            f.my_close()

    @pyqtSlot(Signal)
    def on_apply_to_all_clicked(self, signal: Signal):
        for frame in self.signal_frames:
            if frame.signal is not None:
                frame.signal.noise_min_plot = signal.noise_min_plot
                frame.signal.noise_max_plot = signal.noise_max_plot

                frame.signal.block_protocol_update = True
                proto_needs_update = False

                if frame.signal.modulation_type != signal.modulation_type:
                    frame.signal.modulation_type = signal.modulation_type
                    proto_needs_update = True

                if frame.signal.qad_center != signal.qad_center:
                    frame.signal.qad_center = signal.qad_center
                    proto_needs_update = True

                if frame.signal.tolerance != signal.tolerance:
                    frame.signal.tolerance = signal.tolerance
                    proto_needs_update = True

                if frame.signal.noise_threshold != signal.noise_threshold:
                    frame.signal.noise_threshold = signal.noise_threshold
                    proto_needs_update = True

                if frame.signal.bit_len != signal.bit_len:
                    frame.signal.bit_len = signal.bit_len
                    proto_needs_update = True

                frame.signal.block_protocol_update = False

                if proto_needs_update:
                    frame.signal.protocol_needs_update.emit()

    @pyqtSlot(QPoint)
    def frame_dragged(self, pos: QPoint):
        self.drag_pos = pos

    @pyqtSlot(QPoint)
    def frame_dropped(self, pos: QPoint):
        start = self.drag_pos
        if start is None:
            return

        end = pos
        start_index = -1
        end_index = -1
        if self.num_frames > 1:
            for i, w in enumerate(self.signal_frames):
                if w.geometry().contains(start):
                    start_index = i

                if w.geometry().contains(end):
                    end_index = i

        self.swap_frames(start_index, end_index)
        self.frame_was_dropped.emit(start_index, end_index)

    @pyqtSlot(int, int)
    def swap_frames(self, from_index: int, to_index: int):
        if from_index != to_index:
            start_sig_widget = self.splitter.widget(from_index)
            self.splitter.insertWidget(to_index, start_sig_widget)

    @pyqtSlot(bool)
    def set_shift_statuslabel(self, shift_pressed):
        if shift_pressed and constants.SETTINGS.value('hold_shift_to_drag', False, type=bool):
            self.ui.lShiftStatus.setText("[SHIFT] Use Mouse to scroll signal.")

        elif shift_pressed and not constants.SETTINGS.value('hold_shift_to_drag', False, type=bool):
            self.ui.lShiftStatus.setText("[SHIFT] Use mouse to create a selection.")
        else:
            self.ui.lShiftStatus.clear()

    @pyqtSlot()
    def on_participant_changed(self):
        for sframe in self.signal_frames:
            sframe.on_participant_changed()
