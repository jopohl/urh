import copy
import itertools
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
        return self.__group.labels

    @protocol_labels.setter
    def protocol_labels(self, val):
        self.__group.set_labels(val)

    @property
    def num_blocks_successive_fuzzing(self):
        result = self.num_blocks
        for i in range(self.num_blocks):
            result += sum([len(l.fuzz_values) for l in self.protocol_labels if l.refblock == i and l.active_fuzzing])

        return result

    @property
    def num_blocks_concurrent_fuzzing(self):
        result = self.num_blocks
        for i in range(self.num_blocks):
            vals = [len(l.fuzz_values) for l in self.protocol_labels if l.refblock == i and l.active_fuzzing]
            if len(vals) > 0:
                result += numpy.max(vals)

        return result

    @property
    def num_blocks_exhaustive_fuzzing(self):
        result = self.num_blocks
        for i in range(self.num_blocks):
            vals = [len(l.fuzz_values) for l in self.protocol_labels if l.refblock == i and l.active_fuzzing]
            if len(vals) > 0:
                result += numpy.product(vals)

        return result

    @property
    def active_fuzzing_labels(self):
        return [p for p in self.protocol_labels if p.active_fuzzing]

    @property
    def has_fuzz_labels_with_same_block(self):
        act_labels = self.active_fuzzing_labels
        return any(p1.refblock == p2.refblock
                   for p1 in act_labels for p2 in act_labels if p1 != p2)

    def insert_protocol_analyzer(self, index: int, proto_analyzer: ProtocolAnalyzer):

        blocks = [ProtocolBlock(copy.copy(block.decoded_bits), block.pause,
                                self.bit_alignment_positions, block.rssi, 0, block.decoder, bit_len=block.bit_len,
                                exclude_from_decoding_labels=copy.copy(block.exclude_from_decoding_labels))
                  for block in proto_analyzer.blocks if block]

        self.blocks[index:0] = blocks
        self.used_symbols |= proto_analyzer.used_symbols

        proto_labels = [copy.deepcopy(lbl) for lbl in proto_analyzer.protocol_labels]

        for l in proto_labels:
            l.refblock += index

        for l in self.protocol_labels:
            if l.refblock > index:
                l.refblock += proto_analyzer.num_blocks

        for p in proto_labels:
            self.__group.add_label(p, decode=False)

        for block in self.blocks:
            block.fuzz_labels[index:0] = [p for p in proto_labels if p not in block.fuzz_labels]

        if len(self.pauses) > 0:
            self.fuzz_pause = self.pauses[0]

        self.refresh_protolabel_blocks()

    def duplicate_line(self, row: int):
        self.blocks.insert(row + 1, copy.deepcopy(self.blocks[row]))
        plabels = [l for l in self.protocol_labels if l.refblock > row]
        for pl in plabels:
            pl.refblock += 1

        self.refresh_protolabel_blocks()
        self.qt_signals.line_duplicated.emit()

    def refresh_protolabel_blocks(self):
        self.__group.refresh_labels(decode=False)

    def fuzz_successive(self):
        """
        Führt ein sukzessives Fuzzing über alle aktiven Fuzzing Label durch.
        Sequentiell heißt, ein Label wird durchgefuzzt und alle anderen Labels bleiben auf Standardwert.
        Das entspricht dem Vorgang nacheinander immer nur ein Label aktiv zu setzen.

        :rtype: list of ProtocolBlock
        """
        result = []
        appd_result = result.append
        block_offsets = {}

        for i, block in enumerate(self.blocks):
            labels = [l for l in self.active_fuzzing_labels if l.refblock == i]

            if len(labels) == 0:
                appd_result(block)
                continue

            labels.sort()
            n = sum([len(l.fuzz_values) for l in labels])
            block_offsets[i] = n - 1

            for l in labels:
                l.nfuzzed = n
                for fuzz_val in l.fuzz_values:
                    bool_fuzz_val = [True if bit == "1" else False for bit in fuzz_val]
                    cpy_bits = copy.deepcopy(block.plain_bits)
                    cpy_bits[l.start:l.end] = bool_fuzz_val
                    fuz_block = ProtocolBlock(cpy_bits, block.pause, self.bit_alignment_positions, block.rssi,
                                              block.modulator_indx, block.decoder, [(l.start, l.end)])
                    fuz_block.fuzz_labels = copy.deepcopy(block.fuzz_labels)
                    appd_result(fuz_block)

        # Refblockindizes anpassen
        for l in self.protocol_labels:
            offset = sum(block_offsets[i] for i in block_offsets.keys() if i < l.refblock)
            l.refblock_offset += offset

        self.blocks = result
        """:type: list of ProtocolBlock """
        self.refresh_protolabel_blocks()

    def fuzz_concurrent(self):
        """
        Führt ein gleichzeitiges Fuzzing durch, das heißt bei mehreren Labels pro Block werden alle Labels
        gleichzeitig iteriert. Wenn ein Label keine FuzzValues mehr übrig hat,
        wird der erste Fuzzing Value (per Definition der Standardwert) genommen.

        :rtype: list of ProtocolBlock
        """
        result = []
        appd_result = result.append
        block_offsets = {}

        for i, block in enumerate(self.blocks):
            labels = [l for l in self.active_fuzzing_labels if l.refblock == i]


            if len(labels) == 0:
                appd_result(block)
                continue

            nvalues = numpy.max([len(l.fuzz_values) for l in labels])
            for j in range(nvalues):
                cpy_bits = copy.deepcopy(block.plain_bits)
                fuzz_created = []
                for l in labels:
                    index = j

                    if index >= len(l.fuzz_values):
                        index = 0

                    bool_fuzz_val = [True if bit == "1" else False for bit in l.fuzz_values[index]]
                    cpy_bits[l.start:l.end] = bool_fuzz_val
                    fuzz_created.append((l.start, l.end))

                fuzz_block = ProtocolBlock(cpy_bits, block.pause, self.bit_alignment_positions, block.rssi,
                                           block.modulator_indx, block.decoder, fuzz_created[:])
                fuzz_block.fuzz_labels = copy.deepcopy(block.fuzz_labels)
                appd_result(fuzz_block)

            block_offsets[i] = nvalues - 1
            for l in labels:
                l.nfuzzed = nvalues

        # Refblockindizes anpassen
        for l in self.protocol_labels:
            offset = sum(block_offsets[i] for i in block_offsets.keys() if i < l.refblock)
            l.refblock_offset += offset

        self.blocks = result
        """:type: list of ProtocolBlock """
        self.refresh_protolabel_blocks()

    def fuzz_exhaustive(self):
        """
        Führt ein vollständiges Fuzzing durch. D.h. wenn es mehrere Label pro Block gibt, werden alle
        möglichen Kombinationen erzeugt (Kreuzprodukt!)

        :rtype: list of str
        """
        result = []
        appd_result = result.append
        block_offsets = {}

        for i, block in enumerate(self.blocks):
            labels = [l for l in self.active_fuzzing_labels if l.refblock == i]

            if len(labels) == 0:
                appd_result(block)
                continue

            pool = []
            for l in labels:
                pool.append([(l.start, l.end, fv) for fv in l.fuzz_values])

            n = 0

            for combination in itertools.product(*pool):
                n += 1
                cpy_bits = copy.deepcopy(block.plain_bits)
                fuzz_created = []
                for start, end, fuz_val in combination:
                    bool_fuzz_val = [True if bit == "1" else False for bit in fuz_val]
                    cpy_bits[start:end] = bool_fuzz_val
                    fuzz_created.append((start, end))

                fuz_block = ProtocolBlock(cpy_bits, block.pause, self.bit_alignment_positions, block.rssi,
                                          block.modulator_indx,
                                          block.decoder, fuzz_created)
                fuz_block.fuzz_labels = copy.deepcopy(block.fuzz_labels)
                appd_result(fuz_block)

            block_offsets[i] = n - 1
            for l in labels:
                l.nfuzzed = n

        # Refblockindizes anpassen
        for l in self.protocol_labels:
            offset = sum(block_offsets[i] for i in block_offsets.keys() if i < l.refblock)
            l.refblock_offset += offset

        self.blocks = result
        """:type: list of ProtocolBlock """
        self.refresh_protolabel_blocks()

    def clear(self):
        self.blocks[:] = []
        self.__group.clear_labels()
        self.protocol_labels[:] = []


    def get_label_range(self, lbl: ProtocolLabel, view: int, decode: bool):
        return self.__group.get_label_range(lbl, view, decode)

    def create_fuzzing_label(self, start, end, refblock) -> ProtocolLabel:
        fuz_lbl = self.__group.add_protocol_label(start, end, refblock, 0, False)
        for block in self.blocks:
            block.fuzz_labels.append(fuz_lbl)
        return fuz_lbl

    def remove_label(self, label: ProtocolLabel):
        self.__group.remove_label(label)

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
            block_tag = ET.SubElement(data_tag, "block", attrib={"modulator_index": str(block.modulator_indx),
                                                                 "decoding_index": str(decoders.index(block.decoder)),
                                                                 "index": str(i)})
            block_tag.text = block.plain_bits_str

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

        root = tree.getroot()
        self.clear()

        mod_tags = root.find("modulators").findall("modulator")
        self.modulators[:] = [None] * len(mod_tags)
        for modulator_tag in mod_tags:
            self.modulators[int(modulator_tag.get("index"))] = Modulator.from_xml(modulator_tag)


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
        self.blocks[:] = [None] * len(block_tags)

        for block_tag in block_tags:
            block = ProtocolBlock.from_plain_bits_str(block_tag.text, {s.name: s for s in self.used_symbols})
            block.modulator_indx = int(block_tag.get("modulator_index"))
            block.decoder = decoders[int(block_tag.get("decoding_index"))]
            self.blocks[int(block_tag.get("index"))] = block

        self.protocol_labels[:] = []
        labels_tag = root.find("labels")
        if labels_tag:
            label_tags = labels_tag.findall("label")
            self.protocol_labels = [None] * len(label_tags)
            for label_tag in label_tags:
                self.protocol_labels[int(label_tag.get("index"))] = ProtocolLabel.from_xml(label_tag)