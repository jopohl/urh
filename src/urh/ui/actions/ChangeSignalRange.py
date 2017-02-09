import copy

import numpy as np
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
    def __init__(self, signal: Signal, protocol: ProtocolAnalyzer, start: int, end: int, mode: RangeAction,
                 cache_qad=True):
        super().__init__()

        self.mode = mode
        self.start = int(start)
        self.end = int(end)
        self.signal = signal
        self.cache_qad = cache_qad

        if self.mode == RangeAction.crop:
            self.setText("Crop Signal {0}".format(signal.name))
            self.pre_crop_data = self.signal._fulldata[0:self.start]
            self.post_crop_data = self.signal._fulldata[self.end:]
            if self.cache_qad:
                self.pre_crop_qad = self.signal._qad[0:self.start]
                self.post_crop_qad = self.signal._qad[self.end:]
        elif self.mode == RangeAction.mute:
            self.setText("Mute Range of Signal {0}".format(signal.name))
            self.orig_data_part = copy.copy(self.signal._fulldata[self.start:self.end])
            if self.cache_qad:
                self.orig_qad_part = copy.copy(self.signal._qad[self.start:self.end])
        elif self.mode == RangeAction.delete:
            self.setText("Deleting Range from Signal {0}".format(signal.name))
            self.orig_data_part = self.signal._fulldata[self.start:self.end]
            if self.cache_qad:
                self.orig_qad_part = self.signal._qad[self.start:self.end]

        self.orig_num_samples = self.signal.num_samples
        self.orig_parameter_cache = copy.deepcopy(self.signal.parameter_cache)
        self.signal_was_changed = self.signal.changed
        self.protocol = protocol
        if self.protocol:
            self.orig_messages = copy.deepcopy(self.protocol.messages)

    def redo(self):
        keep_bock_indices = {}
        if self.mode in (RangeAction.delete, RangeAction.mute) and self.protocol:
            removed_msg_indices = self.__find_message_indices_in_sample_range(self.start, self.end)
            if removed_msg_indices:
                for i in range(self.protocol.num_messages):
                    if i < removed_msg_indices[0]:
                        keep_bock_indices[i] = i
                    elif i > removed_msg_indices[-1]:
                        keep_bock_indices[i] = i - len(removed_msg_indices)
            else:
                keep_bock_indices = {i: i for i in range(self.protocol.num_messages)}
        elif self.mode == RangeAction.crop and self.protocol:
            removed_left = self.__find_message_indices_in_sample_range(0, self.start)
            removed_right = self.__find_message_indices_in_sample_range(self.end, self.signal.num_samples)
            last_removed_left = removed_left[-1] if removed_left else -1
            first_removed_right = removed_right[0] if removed_right else self.protocol.num_messages + 1

            for i in range(self.protocol.num_messages):
                if last_removed_left < i < first_removed_right:
                    keep_bock_indices[i] = i - len(removed_left)

        if self.mode == RangeAction.delete:
            self.signal.delete_range(self.start, self.end)
        elif self.mode == RangeAction.mute:
            self.signal.mute_range(self.start, self.end)
        elif self.mode == RangeAction.crop:
            self.signal.crop_to_range(self.start, self.end)

        # Restore old msg data
        if self.protocol:
            for old_index, new_index in keep_bock_indices.items():
                try:
                    old_msg = self.orig_messages[old_index]
                    new_msg = self.protocol.messages[new_index]
                    new_msg.decoder = old_msg.decoder
                    new_msg.message_type = old_msg.message_type
                    new_msg.participant = old_msg.participant
                except IndexError:
                    continue

        if self.protocol:
            self.protocol.qt_signals.protocol_updated.emit()

    def undo(self):
        if self.mode == RangeAction.delete:
            self.signal._fulldata = np.insert(self.signal._fulldata, self.start, self.orig_data_part)
            if self.cache_qad:
                self.signal._qad = np.insert(self.signal._qad, self.start, self.orig_qad_part)

        elif self.mode == RangeAction.mute:
            self.signal._fulldata[self.start:self.end] = self.orig_data_part
            if self.cache_qad:
                self.signal._qad[self.start:self.end] = self.orig_qad_part

        elif self.mode == RangeAction.crop:
            self.signal._fulldata = np.concatenate((self.pre_crop_data, self.signal._fulldata, self.post_crop_data))
            if self.cache_qad:
                self.signal._qad = np.concatenate((self.pre_crop_qad, self.signal._qad, self.post_crop_qad))

        self.signal._num_samples = self.orig_num_samples
        self.signal.parameter_cache = self.orig_parameter_cache

        if self.protocol:
            self.protocol.messages = self.orig_messages
            self.protocol.qt_signals.protocol_updated.emit()

        self.signal.changed = self.signal_was_changed
        self.signal.data_edited.emit()

    def __find_message_indices_in_sample_range(self, start: int, end: int):
        result = []
        for i, message in enumerate(self.protocol.messages):
            if message.bit_sample_pos[0] >= start and message.bit_sample_pos[-2] <= end:
                result.append(i)
            elif message.bit_sample_pos[-2] > end:
                break
        return result
