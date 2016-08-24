import copy
import itertools
import xml
from xml.dom import minidom
import xml.etree.ElementTree as ET

import numpy

from urh.cythonext.signalFunctions import Symbol
from urh.models.ProtocolTreeItem import ProtocolTreeItem
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.signalprocessing.encoding import encoding
from urh.util.Formatter import Formatter
from urh.util.Logger import logger
from enum import Enum

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
        self.__group.add_protocol_item(ProtocolTreeItem(self, None)) # Warning: parent is None

    @property
    def protocol_labels(self):
        result = list(set(lbl for msg in self.messages for lbl in msg.labelset))
        result.sort()
        return result

    @property
    def multiple_fuzz_labels_per_message(self):
        return any(len(msg.active_fuzzing_labels) > 1 for msg in self.messages)

    def insert_protocol_analyzer(self, index: int, proto_analyzer: ProtocolAnalyzer):

        messages = [Message(plain_bits=copy.copy(msg.decoded_bits), pause=msg.pause,
                          labelset=copy.deepcopy(msg.labelset),
                          rssi=msg.rssi, modulator_indx=0, decoder=msg.decoder, bit_len=msg.bit_len, participant=msg.participant)
                  for msg in proto_analyzer.messages if msg]

        self.messages[index:0] = messages
        self.used_symbols |= proto_analyzer.used_symbols

        if len(self.pauses) > 0:
            self.fuzz_pause = self.pauses[0]

    def duplicate_line(self, row: int):
        try:
            self.messages.insert(row + 1, copy.deepcopy(self.messages[row]))
            self.qt_signals.line_duplicated.emit()
        except Exception as e:
            logger.error("Duplicating line ", str(e))

    def fuzz(self, mode: FuzzMode):
        result = []
        appd_result = result.append

        for i, msg in enumerate(self.messages):
            labels = msg.active_fuzzing_labels
            appd_result(msg)

            if mode == FuzzMode.successive:
                combinations = [[(l.start, l.end, fuzz_val)] for l in labels for fuzz_val in l.fuzz_values[1:]]
            elif mode == FuzzMode.concurrent:
                nval = numpy.max([len(l.fuzz_values) for l in labels]) if labels else 0
                f = lambda index, label: index if index < len(label.fuzz_values) else 0
                combinations = [[(l.start, l.end, l.fuzz_values[f(j, l)]) for l in labels] for j in range(1, nval)]
            elif mode == FuzzMode.exhaustive:
                pool = [[(l.start, l.end, fv) for fv in l.fuzz_values[1:]] for l in labels]
                combinations = itertools.product(*pool) if labels else []
            else:
                raise ValueError("Unknown fuzz mode")

            for combination in combinations:
                cpy_bits = msg.plain_bits[:]
                for start, end, fuz_val in combination:
                    cpy_bits[start:end] = [True if bit == "1" else False for bit in fuz_val]

                fuz_msg = Message(plain_bits=cpy_bits, pause=msg.pause,
                                    rssi=msg.rssi, labelset=msg.labelset.copy_for_fuzzing(),
                                    modulator_indx=msg.modulator_indx,
                                    decoder=msg.decoder, fuzz_created=True)
                appd_result(fuz_msg)

        self.messages = result
        """:type: list of Message """

    def fuzz_successive(self):
        """
        Führt ein sukzessives Fuzzing über alle aktiven Fuzzing Label durch.
        Sequentiell heißt, ein Label wird durchgefuzzt und alle anderen Labels bleiben auf Standardwert.
        Das entspricht dem Vorgang nacheinander immer nur ein Label aktiv zu setzen.
        """
        self.fuzz(FuzzMode.successive)

    def fuzz_concurrent(self):
        """
        Führt ein gleichzeitiges Fuzzing durch, das heißt bei mehreren Labels pro Message werden alle Labels
        gleichzeitig iteriert. Wenn ein Label keine FuzzValues mehr übrig hat,
        wird der erste Fuzzing Value (per Definition der Standardwert) genommen.
        """
        self.fuzz(FuzzMode.concurrent)

    def fuzz_exhaustive(self):
        """
        Führt ein vollständiges Fuzzing durch. D.h. wenn es mehrere Label pro Message gibt, werden alle
        möglichen Kombinationen erzeugt (Kreuzprodukt!)
        """
        self.fuzz(FuzzMode.exhaustive)

    def create_fuzzing_label(self, start, end, msg_index) -> ProtocolLabel:
        fuz_lbl = self.messages[msg_index].labelset.add_protocol_label(start=start, end=end, type_index= 0)
        return fuz_lbl

    def set_decoder_for_messages(self, decoder, messages=None):
        raise NotImplementedError("Encoding cant be set in Generator!")

    def to_xml_file(self, filename: str, decoders=None, participants=None, tag_name="fuzz_profile", include_labelset=True, write_bits=True):
        super().to_xml_file(filename=filename, decoders=None, participants=participants, tag_name=tag_name, include_labelset=include_labelset, write_bits=write_bits)

    def from_xml_file(self, filename: str, read_bits=True):
        super().from_xml_file(filename=filename, read_bits=read_bits)

    def clear(self):
        self.messages[:] = []