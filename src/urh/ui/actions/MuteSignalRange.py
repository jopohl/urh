import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class MuteSignalRange(QUndoCommand):
    def __init__(self, signal: Signal, protocol: ProtocolAnalyzer, start: int, end: int):
        super().__init__()

        self.end = end
        self.start = start
        self.signal = signal
        self.setText("Mute Range of Signal {0}".format(signal.name))
        self.muted_data = copy.copy(self.signal._fulldata[self.start:self.end])
        self.muted_qad = copy.copy(self.signal._qad[self.start:self.end])
        self.orig_parameter_cache = copy.deepcopy(self.signal.parameter_cache)
        self.signal_was_changed = self.signal.changed

        self.protocol = protocol
        self.orig_blocks, self.orig_labels = protocol.copy_data()


    def redo(self):
        self.signal._fulldata[self.start:self.end] = 0
        self.signal._qad[self.start:self.end] = 0
        self.signal.clear_parameter_cache()

        self.signal.changed = True
        self.signal.data_edited.emit()
        self.signal.protocol_needs_update.emit()

    def undo(self):
        self.signal._fulldata[self.start:self.end] = self.muted_data
        self.signal._qad[self.start:self.end] = self.muted_qad
        self.signal.parameter_cache = self.orig_parameter_cache

        self.protocol.revert_to(self.orig_blocks, self.orig_labels)
        self.protocol.qt_signals.protocol_updated.emit()

        self.signal.changed = self.signal_was_changed
        self.signal.data_edited.emit()
