import random
import sys
import math
from urh import constants
from urh.signalprocessing.encoding import encoding
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock


class ProtocolGroup(object):
    def __init__(self, name: str, decoding: encoding = encoding(["Non Return To Zero (NRZ)"])):
        self.name = name
        self.__decoding = decoding
        self.__items = []

        self.loaded_from_file = False

    @property
    def decoding(self) -> encoding:
        return self.__decoding

    @decoding.setter
    def decoding(self, val:encoding):
        if self.decoding != val:
            self.__decoding = val
            for proto in self.protocols:
                proto.set_decoder_for_blocks(self.decoding)
            self.refresh_labels()

    @property
    def items(self):
        """

        :rtype: list of ProtocolTreeItem
        """
        return self.__items

    @property
    def labels(self):
        """

        :rtype: list of ProtocolLabel
        """
        return self.__labels

    @property
    def num_protocols(self):
        return len(self.items)

    @property
    def num_blocks(self):
        return sum(p.num_blocks for p in self.protocols)

    @property
    def all_protocols(self):
        """

        :rtype: list of ProtocolAnalyzer
        """
        return [self.protocol_at(i) for i in range(self.num_protocols)]

    @property
    def protocols(self):
        """

        :rtype: list of ProtocolAnalyzer
        """
        return [proto for proto in self.all_protocols if proto.show]

    @property
    def blocks(self):
        """

        :rtype: list of ProtocolBlock
        """
        result = []
        for proto in self.protocols:
            result.extend(proto.blocks)
        return result

    @property
    def plain_bits_str(self):
        """

        :rtype: list of str
        """
        result = []
        for proto in self.protocols:
            result.extend(proto.plain_bits_str)
        return result

    @property
    def decoded_bits_str(self):
        """

        :rtype: list of str
        """
        result = []
        for proto in self.protocols:
            result.extend(proto.decoded_proto_bits_str)
        return result

    def protocol_at(self, index: int) -> ProtocolAnalyzer:
        try:
            proto = self.items[index].protocol
            proto.set_labels(self.labels) # Ensure Protocol has same labels as group
            return proto
        except IndexError:
            return None

    def refresh_label(self, lbl: ProtocolLabel, decode=True):
        if lbl not in self.labels:
            print("Label {0} is not in Group {1}".format(lbl.name, self.name), file=sys.stderr)
            return

        if decode:
            lbl.find_block_numbers(self.decoded_bits_str)
        else:
            lbl.find_block_numbers(self.plain_bits_str)

    def refresh_labels(self, decode=True):
        for lbl in self.labels:
            #lbl.signals.apply_decoding_changed.emit(lbl) # Update DnD Labels for new blocks
            self.refresh_label(lbl, decode)

    def convert_index(self, index: int, from_view: int, to_view: int, decoded: bool, block_indx=-1) -> tuple:
        """
        Konvertiert einen Index aus der einen Sicht (z.B. Bit) in eine andere (z.B. Hex)

        :param block_indx: Wenn -1, wird der Block mit der maximalen Länge ausgewählt
        :return:
        """
        if len(self.blocks) == 0:
            return (0, 0)

        if block_indx == -1:
            block_indx = self.blocks.index(max(self.blocks, key=len)) # Longest Block

        if block_indx >= len(self.blocks):
            block_indx = len(self.blocks) - 1

        return self.blocks[block_indx].convert_index(index, from_view, to_view, decoded)

    def convert_range(self, index1: int, index2: int, from_view: int,
                      to_view: int, decoded: bool, block_indx=-1):
        start = self.convert_index(index1, from_view, to_view, decoded, block_indx=block_indx)[0]
        end = self.convert_index(index2, from_view, to_view, decoded, block_indx=block_indx)[1]

        return int(start), int(math.ceil(end))

    def get_label_range(self, lbl: ProtocolLabel, view: int, decode: bool):
        start = self.convert_index(lbl.start, 0, view, decode, block_indx = lbl.refblock)[0]
        end = self.convert_index(lbl.end, 0, view, decode, block_indx = lbl.refblock)[1]
        return int(start), int(end)

    def find_overlapping_labels(self, start: int, end: int, proto_view):
        ostart = self.convert_index(start, proto_view, 0, True)[0]
        oend = self.convert_index(end, proto_view, 0, True)[1]


        overlapping_labels = [lbl for lbl in self.labels
                              if any(i in range(lbl.start, lbl.end) for i in range(ostart, oend))]

        return overlapping_labels

    def split_labels(self, start: int, end: int, proto_view: int):
        overlapping_labels = self.find_overlapping_labels(start, end, proto_view)
        ostart = self.convert_index(start, proto_view, 0, True)[0]
        oend = self.convert_index(end, proto_view, 0, True)[1]

        for lbl in overlapping_labels:
            self.remove_label(lbl)
            if ostart > lbl.start:

                left_part = self.add_protocol_label(lbl.start, ostart - 1, lbl.refblock, 0, lbl.restrictive)
                left_part.name = lbl.name + "-Left"
                left_part.find_block_numbers(self.decoded_bits_str)

            if oend < lbl.end:
                right_part = self.add_protocol_label(oend, lbl.end - 1, lbl.refblock, 0, lbl.restrictive)
                right_part.name = lbl.name + "-Right"
                right_part.find_block_numbers(self.decoded_bits_str)

    def split_for_new_label(self, label: ProtocolLabel):
        overlapping_labels = self.find_overlapping_labels(label.start, label.end - 1, 0)
        for lbl in overlapping_labels:
            self.remove_label(lbl)
            if label.start > lbl.start:
                left_part = self.add_protocol_label(lbl.start, label.start - 1, lbl.refblock, 0, lbl.restrictive)
                left_part.name = lbl.name + "-Left"
                left_part.find_block_numbers(self.decoded_bits_str)

            if label.start < lbl.end:
                right_part = self.add_protocol_label(label.end, lbl.end - 1, lbl.refblock, 0, lbl.restrictive)
                right_part.name = lbl.name + "-Right"
                right_part.find_block_numbers(self.decoded_bits_str)

    def add_protocol_label(self, start: int, end: int, refblock: int, type_index: int,
                            restrictive: bool, name=None, color_ind=None) -> \
            ProtocolLabel:

        if refblock >= self.num_blocks:
            refblock = 0

        name = "Label {0:d}".format(len(self.labels) + 1) if not name else name
        used_colors = [p.color_index for p in self.labels]
        avail_colors = [i for i, _ in enumerate(constants.LABEL_COLORS) if i not in used_colors]

        if color_ind is None:
            if len(avail_colors) > 0:
                color_ind = avail_colors[random.randint(0, len(avail_colors)-1)]
            else:
                color_ind = random.randint(0, len(constants.LABEL_COLORS) - 1)

        proto_label = ProtocolLabel(name, start, end, refblock, type_index, color_ind, restrictive)
        try:
            proto_label.reference_bits = self.decoded_bits_str[refblock][proto_label.start:proto_label.end]
        except IndexError:
            return None

        proto_label.signals.apply_decoding_changed.connect(self.handle_plabel_apply_decoding_changed)
        proto_label.find_block_numbers(self.decoded_bits_str)
        self.labels.append(proto_label)
        self.labels.sort()

        return proto_label

    def add_label(self, lbl: ProtocolLabel, refresh=True, decode=True):
        if lbl not in self.labels:
            lbl.signals.apply_decoding_changed.connect(self.handle_plabel_apply_decoding_changed)
            self.labels.append(lbl)
            if refresh:
                self.refresh_label(lbl, decode=decode)
            self.labels.sort()

    def handle_plabel_apply_decoding_changed(self, lbl: ProtocolLabel):
        apply_decoding = lbl.apply_decoding
        for i, block in enumerate(self.blocks):
            if i in lbl.block_numbers:
                if apply_decoding:
                    try:
                        block.exclude_from_decoding_labels.remove(lbl)
                        block.clear_decoded_bits()
                        block.clear_encoded_bits()
                    except ValueError:
                        continue
                else:
                    if lbl not in block.exclude_from_decoding_labels:
                        block.exclude_from_decoding_labels.append(lbl)
                        block.exclude_from_decoding_labels.sort()
                        block.clear_decoded_bits()
                        block.clear_encoded_bits()

    def remove_label(self, label: ProtocolLabel):
        try:
            self.labels.remove(label)
        except ValueError:
            return

        for block in self.blocks:
            try:
                block.exclude_from_decoding_labels.remove(label)
            except ValueError:
                continue

            try:
                block.fuzz_labels.remove(label)
            except ValueError:
                continue

    def __repr__(self):
        return "{0} ({1})".format(self.name, self.decoding.name)

    def set_labels(self, val):
        self.__labels = val # For AmbleAssignPlugin

    def clear_labels(self):
        self.__labels[:] = []

    def add_protocol_item(self, protocol_item):
        """
        This is intended for adding a protocol item directly to the group

        :type protocol: ProtocolTreeItem
        :return:
        """
        self.__items.append(protocol_item) # Warning: parent is None!