import copy

import numpy as np
import sys
from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.Signal import Signal


class DeleteSignalRange(QUndoCommand):
    def __init__(self, signal: Signal, start: int, end: int):
        super().__init__()

        self.end = end
        self.start = start
        self.signal = signal
        self.setText("Deleting Range from Signal {0}".format(signal.name))
        self.deleted_data = self.signal._fulldata[self.start:self.end]
        self.deleted_qad = self.signal._qad[self.start:self.end]
        self.orig_num_samples = self.signal.num_samples
        self.orig_parameter_cache = copy.deepcopy(self.signal.parameter_cache)
        self.signal_was_changed = self.signal.changed

    def redo(self):

        mask = np.ones(self.orig_num_samples, dtype=bool)
        mask[self.start:self.end] = False

        try:
            self.signal._fulldata = self.signal._fulldata[mask]
            self.signal._qad = self.signal._qad[mask]
            self.signal._num_samples = len(self.signal.data)
        except IndexError as e:
            print("Warning: Could not delete data: "+str(e), file=sys.stderr)
            return

        self.signal.clear_parameter_cache()

        self.signal.changed = True
        self.signal.full_refresh_needed.emit()

    def undo(self):
        self.signal._num_samples = self.orig_num_samples
        self.signal._fulldata = np.insert(self.signal._fulldata, self.start, self.deleted_data)
        self.signal._qad = np.insert(self.signal._qad, self.start, self.deleted_qad)
        self.signal.parameter_cache = self.orig_parameter_cache

        self.signal.changed = self.signal_was_changed
        self.signal.full_refresh_needed.emit()
