import copy
import itertools
from enum import Enum

import array
import numpy
import time

from urh import constants
from urh.models.ProtocolTreeItem import ProtocolTreeItem
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.util.Logger import logger


class FuzzMode(Enum):
    successive = 0
    concurrent = 1
    exhaustive = 2


class ProtocolAnalyzerContainer(ProtocolAnalyzer):
    """
    A container to manage several ProtocolAnalyzers.
    This class is used by the generator to manage distinct protocols
    """

    def __init__(self, modulators):
        """

        :type modulators: list of Modulator
        """
        super().__init__(None)
        self.modulators = modulators

        self.fuzz_pause = 10000

        self.__group = ProtocolGroup("GeneratorGroup")
        self.__group.add_protocol_item(ProtocolTreeItem(self, None))  # Warning: parent is None

    @property
    def protocol_labels(self):
        result = list(set(lbl for msg in self.messages for lbl in msg.message_type))
        result.sort()
        return result

    @property
    def multiple_fuzz_labels_per_message(self):
        return any(len(msg.active_fuzzing_labels) > 1 for msg in self.messages)

    def insert_protocol_analyzer(self, index: int, proto_analyzer: ProtocolAnalyzer):
        for msg in reversed(proto_analyzer.messages):
            self.messages.insert(index, Message(plain_bits=msg.decoded_bits, pause=msg.pause,
                                                message_type=copy.copy(msg.message_type),
                                                rssi=msg.rssi, modulator_indx=0, decoder=msg.decoder,
                                                bit_len=msg.bit_len, participant=msg.participant))
        if len(self.pauses) > 0:
            self.fuzz_pause = self.pauses[0]

    def duplicate_line(self, row: int):
        try:
            self.messages.insert(row + 1, copy.deepcopy(self.messages[row]))
            self.qt_signals.line_duplicated.emit()
        except Exception as e:
            logger.error("Duplicating line ", str(e))

    def fuzz(self, mode: FuzzMode, default_pause=None):
        result = []
        appd_result = result.append

        added_message_indices = []

        for i, msg in enumerate(self.messages):
            labels = msg.active_fuzzing_labels
            appd_result(msg)

            if mode == FuzzMode.successive:
                combinations = [[(l.start, l.end, fuzz_val)] for l in labels for fuzz_val in l.fuzz_values[1:]]
            elif mode == FuzzMode.concurrent:
                num_values = numpy.max([len(l.fuzz_values) for l in labels]) if labels else 0
                f = lambda index, label: index if index < len(label.fuzz_values) else 0
                combinations = [[(l.start, l.end, l.fuzz_values[f(j, l)]) for l in labels] for j in
                                range(1, num_values)]
            elif mode == FuzzMode.exhaustive:
                pool = [[(l.start, l.end, fv) for fv in l.fuzz_values[1:]] for l in labels]
                combinations = itertools.product(*pool) if labels else []
            else:
                raise ValueError("Unknown fuzz mode")

            self.qt_signals.fuzzing_started.emit(len(combinations))

            message_type = copy.copy(msg.message_type)
            for lbl in labels:
                lbl = copy.copy(lbl)
                lbl.fuzz_values = []
                lbl.fuzz_created = True
                message_type[message_type.index(lbl)] = lbl

            for j, combination in enumerate(combinations):
                cpy_bits = msg.plain_bits[:]
                for start, end, fuz_val in combination:
                    cpy_bits[start:end] = array.array("B", map(int, fuz_val))

                pause = default_pause if default_pause is not None else msg.pause
                fuz_msg = Message(plain_bits=cpy_bits, pause=pause,
                                  rssi=msg.rssi, message_type=message_type,
                                  modulator_indx=msg.modulator_indx,
                                  decoder=msg.decoder, fuzz_created=True)
                added_message_indices.append(i+j+1)
                appd_result(fuz_msg)
                if j % 10000 == 0:
                    self.qt_signals.current_fuzzing_message_changed.emit(j)

        self.qt_signals.fuzzing_finished.emit()
        self.messages = result  # type: list[Message]
        return added_message_indices

    def fuzz_successive(self, default_pause=None):
        """
        Führt ein sukzessives Fuzzing über alle aktiven Fuzzing Label durch.
        Sequentiell heißt, ein Label wird durchgefuzzt und alle anderen Labels bleiben auf Standardwert.
        Das entspricht dem Vorgang nacheinander immer nur ein Label aktiv zu setzen.
        """
        return self.fuzz(FuzzMode.successive, default_pause=default_pause)

    def fuzz_concurrent(self, default_pause=None):
        """
        Führt ein gleichzeitiges Fuzzing durch, das heißt bei mehreren Labels pro Message werden alle Labels
        gleichzeitig iteriert. Wenn ein Label keine FuzzValues mehr übrig hat,
        wird der erste Fuzzing Value (per Definition der Standardwert) genommen.
        """
        return self.fuzz(FuzzMode.concurrent, default_pause=default_pause)

    def fuzz_exhaustive(self, default_pause=None):
        """
        Führt ein vollständiges Fuzzing durch. D.h. wenn es mehrere Label pro Message gibt, werden alle
        möglichen Kombinationen erzeugt (Kreuzprodukt!)
        """
        return self.fuzz(FuzzMode.exhaustive, default_pause=default_pause)

    def create_fuzzing_label(self, start, end, msg_index) -> ProtocolLabel:
        fuz_lbl = self.messages[msg_index].message_type.add_protocol_label(start=start, end=end)
        return fuz_lbl

    def set_decoder_for_messages(self, decoder, messages=None):
        raise NotImplementedError("Encoding cant be set in Generator!")

    def to_xml_file(self, filename: str, decoders=None, participants=None, tag_name="fuzz_profile",
                    include_message_types=True, write_bits=True):
        super().to_xml_file(filename=filename, decoders=None, participants=participants, tag_name=tag_name,
                            include_message_types=include_message_types, write_bits=write_bits)

    def from_xml_file(self, filename: str, read_bits=True):
        super().from_xml_file(filename=filename, read_bits=read_bits)

    def clear(self):
        self.messages[:] = []
