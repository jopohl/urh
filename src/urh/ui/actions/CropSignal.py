import copy

import numpy as np
from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class CropSignal(QUndoCommand):
    def __init__(self, signal: Signal, protocol: ProtocolAnalyzer, start: int, end: int):
        super().__init__()

        self.end = int(end)
        self.start = int(start)
        self.signal = signal
        self.setText("Crop Signal {0}".format(signal.name))
        self.pre_crop_data = self.signal._fulldata[0:self.start]
        self.post_crop_data = self.signal._fulldata[self.end:]
        self.pre_crop_qad = self.signal._qad[0:self.start]
        self.post_crop_qad = self.signal._qad[self.end:]
        self.orig_num_samples = self.signal._num_samples
        self.orig_parameter_cache = copy.deepcopy(self.signal.parameter_cache)
        self.signal_was_changed = self.signal.changed

        self.protocol = protocol
        self.orig_blocks, self.orig_labels = protocol.copy_data()


    def redo(self):
        self.signal._num_samples = self.end - self.start
        self.signal._fulldata = self.signal._fulldata[self.start:self.end]
        self.signal._qad = self.signal._qad[self.start:self.end]
        self.signal.clear_parameter_cache()

        self.signal.changed = True
        self.signal.data_edited.emit()
        self.signal.protocol_needs_update.emit()

    def undo(self):
        self.signal._num_samples = self.orig_num_samples
        self.signal._fulldata = np.concatenate((self.pre_crop_data, self.signal._fulldata, self.post_crop_data))
        self.signal._qad = np.concatenate((self.pre_crop_qad, self.signal._qad, self.post_crop_qad))
        self.signal.parameter_cache = self.orig_parameter_cache

        self.protocol.revert_to(self.orig_blocks, self.orig_labels)
        self.protocol.qt_signals.protocol_updated.emit()

        self.signal.changed = self.signal_was_changed
        self.signal.data_edited.emit()
