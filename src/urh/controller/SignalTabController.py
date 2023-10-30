from PyQt5.QtCore import QPoint, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QSizePolicy, QUndoStack, QCheckBox, QMessageBox

from urh import settings
from urh.controller.widgets.SignalFrame import SignalFrame
from urh.signalprocessing.Signal import Signal
from urh.ui.ui_tab_interpretation import Ui_Interpretation
from urh.util import util


class SignalTabController(QWidget):
    frame_closed = pyqtSignal(SignalFrame)
    not_show_again_changed = pyqtSignal()
    signal_created = pyqtSignal(int, Signal)
    files_dropped = pyqtSignal(list)
    frame_was_dropped = pyqtSignal(int, int)

    @property
    def num_frames(self):
        return len(self.signal_frames)

    @property
    def signal_frames(self):
        """

        :rtype: list of SignalFrame
        """
        splitter = self.ui.splitter
        return [
            splitter.widget(i)
            for i in range(splitter.count())
            if isinstance(splitter.widget(i), SignalFrame)
        ]

    @property
    def signal_undo_stack(self):
        return self.undo_stack

    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.ui = Ui_Interpretation()
        self.ui.setupUi(self)

        util.set_splitter_stylesheet(self.ui.splitter)

        self.ui.placeholderLabel.setVisible(False)
        self.getting_started_status = None
        self.__set_getting_started_status(True)

        self.undo_stack = QUndoStack()
        self.project_manager = project_manager

        self.drag_pos = None

    def on_files_dropped(self, files):
        self.files_dropped.emit(files)

    def close_frame(self, frame: SignalFrame):
        self.frame_closed.emit(frame)

    def add_signal_frame(self, proto_analyzer, index=-1):
        self.__set_getting_started_status(False)
        sig_frame = SignalFrame(
            proto_analyzer, self.undo_stack, self.project_manager, parent=self
        )
        sframes = self.signal_frames

        if len(proto_analyzer.signal.filename) == 0:
            # new signal from "create signal from selection"
            sig_frame.ui.btnSaveSignal.show()

        self.__create_connects_for_signal_frame(signal_frame=sig_frame)
        sig_frame.signal_created.connect(self.emit_signal_created)
        sig_frame.not_show_again_changed.connect(self.not_show_again_changed.emit)
        sig_frame.ui.lineEditSignalName.setToolTip(
            self.tr("Sourcefile: ") + proto_analyzer.signal.filename
        )
        sig_frame.apply_to_all_clicked.connect(self.on_apply_to_all_clicked)

        prev_signal_frame = sframes[-1] if len(sframes) > 0 else None
        if prev_signal_frame is not None and hasattr(prev_signal_frame, "ui"):
            sig_frame.ui.cbProtoView.setCurrentIndex(
                prev_signal_frame.ui.cbProtoView.currentIndex()
            )

        sig_frame.blockSignals(True)

        index = self.num_frames if index == -1 else index
        self.ui.splitter.insertWidget(index, sig_frame)
        sig_frame.blockSignals(False)

        default_view = settings.read("default_view", 0, int)
        sig_frame.ui.cbProtoView.setCurrentIndex(default_view)

        return sig_frame

    def add_empty_frame(self, filename: str, proto):
        self.__set_getting_started_status(False)
        sig_frame = SignalFrame(
            proto_analyzer=proto,
            undo_stack=self.undo_stack,
            project_manager=self.project_manager,
            parent=self,
        )

        sig_frame.ui.lineEditSignalName.setText(filename)
        self.__create_connects_for_signal_frame(signal_frame=sig_frame)

        self.ui.splitter.insertWidget(self.num_frames, sig_frame)

        return sig_frame

    def __set_getting_started_status(self, getting_started: bool):
        if getting_started == self.getting_started_status:
            return

        self.getting_started_status = getting_started
        self.ui.labelGettingStarted.setVisible(getting_started)

        if not getting_started:
            w = QWidget()
            w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            self.ui.splitter.addWidget(w)

    def __create_connects_for_signal_frame(self, signal_frame: SignalFrame):
        signal_frame.hold_shift = settings.read("hold_shift_to_drag", True, type=bool)
        signal_frame.drag_started.connect(self.frame_dragged)
        signal_frame.frame_dropped.connect(self.frame_dropped)
        signal_frame.files_dropped.connect(self.on_files_dropped)
        signal_frame.closed.connect(self.close_frame)

    def set_frame_numbers(self):
        for i, f in enumerate(self.signal_frames):
            f.ui.lSignalNr.setText("{0:d}:".format(i + 1))

    @pyqtSlot()
    def save_all(self):
        if self.num_frames == 0:
            return

        try:
            not_show = settings.read("not_show_save_dialog", False, type=bool)
        except TypeError:
            not_show = False

        if not not_show:
            cb = QCheckBox("Don't ask me again.")
            msg_box = QMessageBox(
                QMessageBox.Question,
                self.tr("Confirm saving all signals"),
                self.tr("All changed signal files will be overwritten. OK?"),
            )
            msg_box.addButton(QMessageBox.Yes)
            msg_box.addButton(QMessageBox.No)
            msg_box.setCheckBox(cb)

            reply = msg_box.exec()
            not_show_again = cb.isChecked()
            settings.write("not_show_save_dialog", not_show_again)
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

                if frame.signal.center != signal.center:
                    frame.signal.center = signal.center
                    proto_needs_update = True

                if frame.signal.tolerance != signal.tolerance:
                    frame.signal.tolerance = signal.tolerance
                    proto_needs_update = True

                if frame.signal.noise_threshold != signal.noise_threshold:
                    frame.signal.noise_threshold_relative = (
                        signal.noise_threshold_relative
                    )
                    proto_needs_update = True

                if frame.signal.samples_per_symbol != signal.samples_per_symbol:
                    frame.signal.samples_per_symbol = signal.samples_per_symbol
                    proto_needs_update = True

                if frame.signal.pause_threshold != signal.pause_threshold:
                    frame.signal.pause_threshold = signal.pause_threshold
                    proto_needs_update = True

                if frame.signal.message_length_divisor != signal.message_length_divisor:
                    frame.signal.message_length_divisor = signal.message_length_divisor
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
            start_sig_widget = self.ui.splitter.widget(from_index)
            self.ui.splitter.insertWidget(to_index, start_sig_widget)

    @pyqtSlot()
    def on_participant_changed(self):
        for sframe in self.signal_frames:
            sframe.on_participant_changed()

    def redraw_spectrograms(self):
        for frame in self.signal_frames:
            if frame.ui.gvSpectrogram.width_spectrogram > 0:
                frame.draw_spectrogram(force_redraw=True)

    @pyqtSlot(Signal)
    def emit_signal_created(self, signal):
        try:
            index = self.signal_frames.index(self.sender()) + 1
        except ValueError:
            index = -1

        self.signal_created.emit(index, signal)
