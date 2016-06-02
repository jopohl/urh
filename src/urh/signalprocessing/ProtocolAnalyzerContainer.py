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
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.signalprocessing.encoding import encoding
from urh.util.Formatter import Formatter
from urh.util.Logger import logger


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
        self.created_fuz_blocks = []

        self.__group = ProtocolGroup("GeneratorGroup")
        self.__group.add_protocol_item(ProtocolTreeItem(self, None)) # Warning: parent is None

    @property
    def protocol_labels(self):
        result = list(set(lbl for block in self.blocks for lbl in block.labelset))
        result.sort()
        return  result

    @property
    def active_fuzzing_labels(self):
        return [p for p in self.protocol_labels if p.active_fuzzing]

    @property
    def multiple_fuzz_labels_per_block(self):
        return any(len(block.active_fuzzing_labels) > 1 for block in self.blocks)

    def insert_protocol_analyzer(self, index: int, proto_analyzer: ProtocolAnalyzer):

        blocks = [ProtocolBlock(plain_bits=copy.copy(block.decoded_bits), pause=block.pause,
                                bit_alignment_positions=self.bit_alignment_positions, labelset=copy.deepcopy(block.labelset),
                                rssi=block.rssi, modulator_indx=0, decoder=block.decoder, bit_len=block.bit_len, participant=block.participant)
                  for block in proto_analyzer.blocks if block]

        self.blocks[index:0] = blocks
        self.used_symbols |= proto_analyzer.used_symbols

        if len(self.pauses) > 0:
            self.fuzz_pause = self.pauses[0]

    def duplicate_line(self, row: int):
        try:
            self.blocks.insert(row + 1, copy.deepcopy(self.blocks[row]))
            self.qt_signals.line_duplicated.emit()
        except Exception as e:
            logger.error("Duplicating line ", str(e))

    def fuzz_successive(self):
        """
        Führt ein sukzessives Fuzzing über alle aktiven Fuzzing Label durch.
        Sequentiell heißt, ein Label wird durchgefuzzt und alle anderen Labels bleiben auf Standardwert.
        Das entspricht dem Vorgang nacheinander immer nur ein Label aktiv zu setzen.

        :rtype: list of ProtocolBlock
        """
        result = []
        appd_result = result.append

        for i, block in enumerate(self.blocks):
            labels = block.active_fuzzing_labels

            appd_result(block)

            labels.sort()
            n = sum([len(l.fuzz_values[1:]) for l in labels])

            for l in labels:
                l.nfuzzed = n
                for fuzz_val in l.fuzz_values[1:]:
                    bool_fuzz_val = [True if bit == "1" else False for bit in fuzz_val]
                    cpy_bits = copy.deepcopy(block.plain_bits)
                    cpy_bits[l.start:l.end] = bool_fuzz_val
                    fuz_block = ProtocolBlock(plain_bits=cpy_bits, pause=block.pause,
                                              bit_alignment_positions=self.bit_alignment_positions, rssi=block.rssi,
                                              labelset=block.labelset.copy_for_fuzzing(),
                                              modulator_indx=block.modulator_indx, decoder=block.decoder,
                                              fuzz_created=True)
                    appd_result(fuz_block)

        self.blocks = result
        """:type: list of ProtocolBlock """

    def fuzz_concurrent(self):
        """
        Führt ein gleichzeitiges Fuzzing durch, das heißt bei mehreren Labels pro Block werden alle Labels
        gleichzeitig iteriert. Wenn ein Label keine FuzzValues mehr übrig hat,
        wird der erste Fuzzing Value (per Definition der Standardwert) genommen.
        """
        result = []
        appd_result = result.append
        block_offsets = {}

        for i, block in enumerate(self.blocks):
            labels = block.active_fuzzing_labels
            appd_result(block)

            nvalues = numpy.max([len(l.fuzz_values[1:]) for l in labels])
            for j in range(nvalues):
                cpy_bits = copy.deepcopy(block.plain_bits)
                for l in labels:
                    index = j

                    if index >= len(l.fuzz_values[1:]):
                        index = 0

                    bool_fuzz_val = [True if bit == "1" else False for bit in l.fuzz_values[1:][index]]
                    cpy_bits[l.start:l.end] = bool_fuzz_val

                fuzz_block = ProtocolBlock(plain_bits=cpy_bits, pause=block.pause, bit_alignment_positions=self.bit_alignment_positions,
                                           rssi=block.rssi, labelset=block.labelset.copy_for_fuzzing(),
                                           modulator_indx=block.modulator_indx, decoder=block.decoder, fuzz_created=True)
                appd_result(fuzz_block)

            block_offsets[i] = nvalues - 1
            for l in labels:
                l.nfuzzed = nvalues

        self.blocks = result
        """:type: list of ProtocolBlock """

    def fuzz_exhaustive(self):
        """
        Führt ein vollständiges Fuzzing durch. D.h. wenn es mehrere Label pro Block gibt, werden alle
        möglichen Kombinationen erzeugt (Kreuzprodukt!)
        """
        result = []
        appd_result = result.append

        for i, block in enumerate(self.blocks):
            labels = block.active_fuzzing_labels
            appd_result(block)

            pool = []
            for l in labels:
                pool.append([(l.start, l.end, fv) for fv in l.fuzz_values[1:]])

            n = 0

            for combination in itertools.product(*pool):
                n += 1
                cpy_bits = copy.deepcopy(block.plain_bits)
                for start, end, fuz_val in combination:
                    bool_fuzz_val = [True if bit == "1" else False for bit in fuz_val]
                    cpy_bits[start:end] = bool_fuzz_val

                fuz_block = ProtocolBlock(plain_bits=cpy_bits, pause=block.pause, bit_alignment_positions=self.bit_alignment_positions,
                                          rssi=block.rssi, labelset=block.labelset.copy_for_fuzzing(),
                                          modulator_indx=block.modulator_indx,
                                          decoder=block.decoder, fuzz_created=True)
                appd_result(fuz_block)

            for l in labels:
                l.nfuzzed = n

        self.blocks = result
        """:type: list of ProtocolBlock """

    def create_fuzzing_label(self, start, end, block_index) -> ProtocolLabel:
        fuz_lbl = self.blocks[block_index].labelset.add_protocol_label(start=start, end=end, type_index= 0)
        return fuz_lbl

    def set_decoder_for_blocks(self, decoder, blocks=None):
        raise NotImplementedError("Encoding cant be set in Generator!")

    def to_xml_file(self, filename: str, decoders=None, participants=None, tag_name="fuzz_profile", include_labelset=True, write_bits=True):
        super().to_xml_file(filename=filename, decoders=None, participants=participants, tag_name=tag_name, include_labelset=include_labelset, write_bits=write_bits)

    def from_xml_file(self, filename: str, read_bits=True):
        super().from_xml_file(filename=filename, read_bits=read_bits)

    def clear(self):
        self.blocks[:] = []