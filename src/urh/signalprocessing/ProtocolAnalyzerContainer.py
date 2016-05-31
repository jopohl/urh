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
                                rssi=block.rssi, modulator_indx=0, decoder=block.decoder, bit_len=block.bit_len)
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

    def clear(self):
        self.blocks[:] = []
        self.protocol_labels[:] = []

    def create_fuzzing_label(self, start, end, block_index) -> ProtocolLabel:
        fuz_lbl = self.blocks[block_index].labelset.add_protocol_label(start=start, end=end, type_index= 0)
        return fuz_lbl

    def set_decoder_for_blocks(self, decoder, blocks=None):
        raise NotImplementedError("Encoding cant be set in Generator!")

    def to_xml_file(self, filename: str):
        root = ET.Element("fuzz_profile")

        # Save modulators
        modulators_tag = ET.SubElement(root, "modulators")
        for i, modulator in enumerate(self.modulators):
            modulators_tag.append(modulator.to_xml(i))

        # Save decodings
        decodings_tag = ET.SubElement(root, "decodings")
        decoders = []
        for block in self.blocks:
            if block.decoder not in decoders:
                decoders.append(block.decoder)

        for i, decoding in enumerate(decoders):
            dec_str = ""
            for chn in decoding.get_chain():
                dec_str += repr(chn) + ", "
            dec_tag = ET.SubElement(decodings_tag, "decoding")
            dec_tag.set("index", str(i))
            dec_tag.text = dec_str

        # Save symbols
        if len(self.used_symbols) > 0:
            symbols_tag = ET.SubElement(root, "symbols")
            for symbol in self.used_symbols:
                ET.SubElement(symbols_tag, "symbol", attrib={"name": symbol.name, "pulsetype": str(symbol.pulsetype),
                                                            "nbits": str(symbol.nbits), "nsamples": str(symbol.nsamples)})
        # Save data
        data_tag = ET.SubElement(root, "data")
        for i, block in enumerate(self.blocks):
            block_tag = block.to_xml(decoders=decoders, include_labelset=True)
            block_tag.set("bits", block.plain_bits_str)
            data_tag.append(block_tag)

        # Save labels
        if len(self.protocol_labels) > 0:
            labels_tag = ET.SubElement(root, "labels")
            for i, lbl in enumerate(self.protocol_labels):
                labels_tag.append(lbl.to_xml(i))

        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        with open(filename, "w") as f:
            for line in xmlstr.split("\n"):
                if line.strip():
                    f.write(line+"\n")

    def from_xml_file(self, filename: str):
        try:
            tree = ET.parse(filename)
        except FileNotFoundError:
            logger.error("Could not find file "+filename)
            return
        except xml.etree.ElementTree.ParseError:
            logger.error("Could not parse file " + filename)
            return

        root = tree.getroot()
        self.clear()

        mod_tags = root.find("modulators").findall("modulator")
        self.modulators[:] = [Modulator("Bugged")] * len(mod_tags)
        for modulator_tag in mod_tags:
            self.modulators[Formatter.str2val(modulator_tag.get("index"), int) % len(self.modulators)] = Modulator.from_xml(modulator_tag)


        decodings_tags = root.find("decodings").findall("decoding")
        decoders = [None] * len(decodings_tags)
        for decoding_tag in decodings_tags:
            conf = [d.strip().replace("'", "") for d in decoding_tag.text.split(",") if d.strip().replace("'", "")]
            decoders[int(decoding_tag.get("index"))] = encoding(conf)

        self.used_symbols.clear()
        symbols_tag = root.find("symbols")
        if symbols_tag:
            for symbol_tag in symbols_tag.findall("symbol"):
                s = Symbol(symbol_tag.get("name"), int(symbol_tag.get("nbits")),
                           int(symbol_tag.get("pulsetype")), int(symbol_tag.get("nsamples")))
                self.used_symbols.add(s)

        block_tags = root.find("data").findall("block")
        self.blocks[:] = []

        for block_tag in block_tags:
            block = ProtocolBlock.from_plain_bits_str(bits=block_tag.get("bits"), symbols={s.name: s for s in self.used_symbols},
                                                      labelset=None)
            block.from_xml(tag=block_tag, participants=None, decoders=decoders)
            block.modulator_indx = Formatter.str2val(block_tag.get("modulator_index"), int, 0)
            block.decoder = decoders[Formatter.str2val(block_tag.get("decoding_index"), int, 0)]
            block.pause = Formatter.str2val(block_tag.get("pause"), int)
            self.blocks.append(block)
