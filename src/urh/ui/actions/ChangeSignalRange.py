import copy

import numpy as np
import sys
from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal

from enum import Enum

from urh.util.Logger import logger


class RangeAction(Enum):
    crop = 1
    mute = 2
    delete = 3

class ChangeSignalRange(QUndoCommand):

    def __init__(self, signal: Signal, protocol: ProtocolAnalyzer, start: int, end: int, mode: RangeAction):
        super().__init__()

        self.mode = mode
        self.start = int(start)
        self.end = int(end)
        self.signal = signal

        if self.mode == RangeAction.crop:
            self.setText("Crop Signal {0}".format(signal.name))
            self.pre_crop_data = self.signal._fulldata[0:self.start]
            self.post_crop_data = self.signal._fulldata[self.end:]
            self.pre_crop_qad = self.signal._qad[0:self.start]
            self.post_crop_qad = self.signal._qad[self.end:]
        elif self.mode == RangeAction.mute:
            self.setText("Mute Range of Signal {0}".format(signal.name))
            self.orig_data_part = copy.copy(self.signal._fulldata[self.start:self.end])
            self.orig_qad_part = copy.copy(self.signal._qad[self.start:self.end])
        elif self.mode == RangeAction.delete:
            self.setText("Deleting Range from Signal {0}".format(signal.name))
            self.orig_data_part = self.signal._fulldata[self.start:self.end]
            self.orig_qad_part = self.signal._qad[self.start:self.end]

        self.orig_num_samples = self.signal.num_samples
        self.orig_parameter_cache = copy.deepcopy(self.signal.parameter_cache)
        self.signal_was_changed = self.signal.changed
        self.protocol = protocol
        self.orig_blocks = copy.deepcopy(self.protocol.blocks)

    def redo(self):
        if self.mode == RangeAction.delete:
            mask = np.ones(self.orig_num_samples, dtype=bool)
            mask[self.start:self.end] = False

            try:
                self.signal._fulldata = self.signal._fulldata[mask]
                self.signal._qad = self.signal._qad[mask]
                self.signal._num_samples = len(self.signal.data)
            except IndexError as e:
                logger.warning("Could not delete data: "+str(e))
                return
        elif self.mode == RangeAction.mute:
            self.signal._fulldata[self.start:self.end] = 0
            self.signal._qad[self.start:self.end] = 0
        elif self.mode == RangeAction.crop:
            self.signal._num_samples = self.end - self.start
            self.signal._fulldata = self.signal._fulldata[self.start:self.end]
            self.signal._qad = self.signal._qad[self.start:self.end]

        self.signal.clear_parameter_cache()
        self.signal.changed = True
        self.signal.data_edited.emit()
        self.signal.protocol_needs_update.emit()

    def undo(self):
        if self.mode == RangeAction.delete:
            self.signal._fulldata = np.insert(self.signal._fulldata, self.start, self.orig_data_part)
            self.signal._qad = np.insert(self.signal._qad, self.start, self.orig_qad_part)
        elif self.mode == RangeAction.mute:
            self.signal._fulldata[self.start:self.end] = self.orig_data_part
            self.signal._qad[self.start:self.end] = self.orig_qad_part
        elif self.mode == RangeAction.crop:
            self.signal._fulldata = np.concatenate((self.pre_crop_data, self.signal._fulldata, self.post_crop_data))
            self.signal._qad = np.concatenate((self.pre_crop_qad, self.signal._qad, self.post_crop_qad))

        self.signal._num_samples = self.orig_num_samples
        self.signal.parameter_cache = self.orig_parameter_cache

        self.protocol.blocks = self.orig_blocks
        self.protocol.qt_signals.protocol_updated.emit()

        self.signal.changed = self.signal_was_changed
        self.signal.data_edited.emit()

    def __find_block_indices_in_selection_range(self, start: int, end: int):
        result = []
        for i, block in enumerate(self.protocol.blocks):
            if block.bit_sample_pos[0] > start and block.bit_sample_pos[-2] < end:
                result.append(i)
            elif block.bit_sample_pos[-2] >= end:
                break