import copy

import numpy as np
from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.Filter import Filter
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal

from enum import Enum

from urh.util.Logger import logger


class EditAction(Enum):
    crop = 1
    mute = 2
    delete = 3
    paste = 4
    insert = 5
    filter = 6


class EditSignalAction(QUndoCommand):
    def __init__(self, signal: Signal, mode: EditAction,
                 start: int = 0, end: int = 0, position: int = 0,
                 data_to_insert: np.ndarray=None, dsp_filter: Filter=None,
                 protocol: ProtocolAnalyzer=None, cache_qad=True):
        """

        :param signal: Signal to change
        :param mode: Mode
        :param start: Start of selection
        :param end: End of selection
        :param position: Position to insert
        :param data_to_insert: (optionally) data to insert/paste
        :param protocol: (optional) protocol for the signal
        :param cache_qad: Enable/Disable caching of quad demod data.
        It is necessary to disable caching, when the signal does not use/need quad demod data
        """
        super().__init__()

        self.signal = signal
        self.mode = mode
        self.start = int(start)
        self.end = int(end)
        self.position = int(position)
        self.data_to_insert = data_to_insert
        self.protocol = protocol
        self.cache_qad = cache_qad
        self.dsp_filter = dsp_filter

        self.orig_qad_part = None

        if self.mode == EditAction.crop:
            self.setText("Crop Signal")
            self.pre_crop_data = self.signal._fulldata[0:self.start]
            self.post_crop_data = self.signal._fulldata[self.end:]
            if self.cache_qad:
                self.pre_crop_qad = self.signal._qad[0:self.start]
                self.post_crop_qad = self.signal._qad[self.end:]
        elif self.mode == EditAction.mute or self.mode == EditAction.filter:
            if self.mode == EditAction.mute:
                self.setText("Mute Signal")
            elif self.mode == EditAction.filter:
                self.setText("Filter Signal")
            self.orig_data_part = copy.copy(self.signal._fulldata[self.start:self.end])
            if self.cache_qad and self.signal._qad is not None:
                self.orig_qad_part = copy.copy(self.signal._qad[self.start:self.end])
        elif self.mode == EditAction.delete:
            self.setText("Delete Range")
            self.orig_data_part = self.signal._fulldata[self.start:self.end]
            if self.cache_qad and self.signal._qad is not None:
                self.orig_qad_part = self.signal._qad[self.start:self.end]
        elif self.mode == EditAction.paste:
            self.setText("Paste")
        elif self.mode == EditAction.insert:
            self.setText("insert sine wave")

        self.orig_parameter_cache = copy.deepcopy(self.signal.parameter_cache)
        self.signal_was_changed = self.signal.changed

        if self.protocol:
            # Do not make a deepcopy of the message type, or they will be out of sync in analysis
            self.orig_messages = copy.copy(self.protocol.messages)

    def redo(self):
        keep_msg_indices = {}

        if self.mode in (EditAction.delete, EditAction.mute) and self.protocol:
            removed_msg_indices = self.__find_message_indices_in_sample_range(self.start, self.end)
            if removed_msg_indices:
                for i in range(self.protocol.num_messages):
                    if i < removed_msg_indices[0]:
                        keep_msg_indices[i] = i
                    elif i > removed_msg_indices[-1]:
                        keep_msg_indices[i] = i - len(removed_msg_indices)
            else:
                keep_msg_indices = {i: i for i in range(self.protocol.num_messages)}
        elif self.mode == EditAction.crop and self.protocol:
            removed_left = self.__find_message_indices_in_sample_range(0, self.start)
            removed_right = self.__find_message_indices_in_sample_range(self.end, self.signal.num_samples)
            last_removed_left = removed_left[-1] if removed_left else -1
            first_removed_right = removed_right[0] if removed_right else self.protocol.num_messages + 1

            for i in range(self.protocol.num_messages):
                if last_removed_left < i < first_removed_right:
                    keep_msg_indices[i] = i - len(removed_left)

        if self.mode == EditAction.delete:
            self.signal.delete_range(self.start, self.end)
        elif self.mode == EditAction.mute:
            self.signal.mute_range(self.start, self.end)
        elif self.mode == EditAction.crop:
            self.signal.crop_to_range(self.start, self.end)
        elif self.mode == EditAction.paste or self.mode == EditAction.insert:
            self.signal.insert_data(self.position, self.data_to_insert)
            if self.protocol:
                keep_msg_indices = self.__get_keep_msg_indices_for_paste()
        elif self.mode == EditAction.filter:
            self.signal.filter_range(self.start, self.end, self.dsp_filter)

        # Restore old msg data
        if self.protocol:
            for old_index, new_index in keep_msg_indices.items():
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
        if self.mode == EditAction.delete:
            self.signal._fulldata = np.insert(self.signal._fulldata, self.start, self.orig_data_part)
            if self.cache_qad and self.orig_qad_part is not None:
                try:
                    self.signal._qad = np.insert(self.signal._qad, self.start, self.orig_qad_part)
                except ValueError:
                    self.signal._qad = None
                    logger.warning("Could not restore cached qad.")

        elif self.mode == EditAction.mute or self.mode == EditAction.filter:
            self.signal._fulldata[self.start:self.end] = self.orig_data_part
            if self.cache_qad and self.orig_qad_part is not None:
                try:
                    self.signal._qad[self.start:self.end] = self.orig_qad_part
                except (ValueError, TypeError):
                    self.signal._qad = None
                    logger.warning("Could not restore cached qad.")

        elif self.mode == EditAction.crop:
            self.signal._fulldata = np.concatenate((self.pre_crop_data, self.signal._fulldata, self.post_crop_data))
            if self.cache_qad:
                try:
                    self.signal._qad = np.concatenate((self.pre_crop_qad, self.signal._qad, self.post_crop_qad))
                except ValueError:
                    self.signal._qad = None
                    logger.warning("Could not restore cached qad.")

        elif self.mode == EditAction.paste or self.mode == EditAction.insert:
            self.signal.delete_range(self.position, self.position+len(self.data_to_insert))

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

    def __get_keep_msg_indices_for_paste(self):
        keep_msg_indices = {i: i for i in range(len(self.orig_messages))}

        try:
            paste_start_index = self.__find_message_indices_in_sample_range(self.position, self.signal.num_samples)[0]
        except IndexError:
            paste_start_index = 0

        try:
            paste_end_index = self.__find_message_indices_in_sample_range(self.position + len(self.data_to_insert),
                                                                          self.signal.num_samples)[0]
        except IndexError:
            paste_end_index = 0

        for i in range(paste_start_index, paste_end_index):
            del keep_msg_indices[i]

        n = paste_end_index - paste_start_index
        for i in range(paste_end_index, len(self.orig_messages) + n):
            keep_msg_indices[i - n] = i

        return keep_msg_indices
