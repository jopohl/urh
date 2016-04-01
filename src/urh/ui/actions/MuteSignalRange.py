import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.Signal import Signal


class MuteSignalRange(QUndoCommand):
    def __init__(self, signal: Signal, start: int, end: int):
        super().__init__()

        self.end = end
        self.start = start
        self.signal = signal
        self.setText("Mute Range of Signal {0}".format(signal.name))
        self.muted_data = copy.copy(self.signal._fulldata[self.start:self.end])
        self.muted_qad = copy.copy(self.signal._qad[self.start:self.end])
        self.orig_parameter_cache = copy.deepcopy(self.signal.parameter_cache)
        self.signal_was_changed = self.signal.changed


    def redo(self):
        self.signal._fulldata[self.start:self.end] = 0
        self.signal._qad[self.start:self.end] = 0
        self.signal.clear_parameter_cache()

        self.signal.changed = True
        self.signal.full_refresh_needed.emit()

    def undo(self):
        self.signal._fulldata[self.start:self.end] = self.muted_data
        self.signal._qad[self.start:self.end] = self.muted_qad
        self.signal.parameter_cache = self.orig_parameter_cache

        self.signal.changed = self.signal_was_changed
        self.signal.full_refresh_needed.emit()
