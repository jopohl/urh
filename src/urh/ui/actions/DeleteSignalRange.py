import copy

import numpy as np
import sys
from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class DeleteSignalRange(QUndoCommand):
    def __init__(self, signal: Signal, protocol: ProtocolAnalyzer, start: int, end: int):
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
        self.protocol = protocol
        self.orig_blocks, self.orig_labels = protocol.copy_data()

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
        self.signal.data_edited.emit()
        self.signal.protocol_needs_update.emit()

    def undo(self):
        self.signal._num_samples = self.orig_num_samples
        self.signal._fulldata = np.insert(self.signal._fulldata, self.start, self.deleted_data)
        self.signal._qad = np.insert(self.signal._qad, self.start, self.deleted_qad)
        self.signal.parameter_cache = self.orig_parameter_cache

        self.protocol.revert_to(self.orig_blocks, self.orig_labels)
        self.protocol.qt_signals.protocol_updated.emit()

        self.signal.changed = self.signal_was_changed
        self.signal.data_edited.emit()

