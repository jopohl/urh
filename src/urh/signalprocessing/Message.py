import array
import copy
import math
import xml.etree.ElementTree as ET

import time

from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.util.Formatter import Formatter
from urh.util.Logger import logger


class Message(object):
    """
    A protocol message is a single line of a protocol.
    """

    __slots__ = ["__plain_bits", "__bit_alignments", "pause", "modulator_index", "rssi", "participant", "message_type",
                 "absolute_time", "relative_time", "__decoder", "align_labels", "decoding_state", "timestamp",
                 "fuzz_created", "__decoded_bits", "__encoded_bits", "decoding_errors", "samples_per_symbol", "bit_sample_pos",
                 "alignment_offset", "bits_per_symbol"]

    def __init__(self, plain_bits, pause: int, message_type: MessageType, rssi=0, modulator_index=0, decoder=None,
                 fuzz_created=False, bit_sample_pos=None, samples_per_symbol=100, participant=None, bits_per_symbol=1):
        """

        :param pause: pause AFTER the message in samples
        :type plain_bits: list[bool|int]
        :type decoder: Encoding
        :type bit_alignment_positions: list of int
        :param bit_alignment_positions: Für Ausrichtung der Hex Darstellung (Leere Liste für Standardverhalten)
        :param samples_per_symbol: Für Übernahme der Bitlänge in Modulator Dialog
        :param fuzz_created: message was created through fuzzing
        :return:
        """
        self.__plain_bits = array.array("B", plain_bits)
        self.pause = pause
        self.modulator_index = modulator_index
        self.rssi = rssi
        self.participant = participant    # type: Participant
        self.message_type = message_type  # type: MessageType

        self.timestamp = time.time()
        self.absolute_time = 0  # set in Compare Frame
        self.relative_time = 0  # set in Compare Frame

        self.__decoder = decoder if decoder else Encoding(["Non Return To Zero (NRZ)"])  # type: Encoding

        self.align_labels = True
        self.fuzz_created = fuzz_created

        self.alignment_offset = 0

        self.__decoded_bits = None
        self.__encoded_bits = None
        self.__bit_alignments = []
        self.decoding_errors = 0
        self.decoding_state = Encoding.ErrorState.SUCCESS

        self.samples_per_symbol = samples_per_symbol  # to take over in modulator
        self.bits_per_symbol = bits_per_symbol # to take over in generator tab (default modulator settings)

        if bit_sample_pos is None:
            self.bit_sample_pos = array.array("L", [])
        else:
            self.bit_sample_pos = bit_sample_pos
            """
            :param bit_sample_pos: Position of samples for each bit. Last position is pause so last bit is on pos -2.
            :type  bit_sample_pos: array.array
            """

    @property
    def plain_bits(self):
        """

        :rtype: array.array
        """
        return self.__plain_bits

    @plain_bits.setter
    def plain_bits(self, value: list):
        self.__plain_bits = array.array("B", value)
        self.clear_decoded_bits()
        self.clear_encoded_bits()

    @property
    def active_fuzzing_labels(self):
        return [lbl for lbl in self.message_type if lbl.active_fuzzing]

    @property
    def exclude_from_decoding_labels(self):
        return [lbl for lbl in self.message_type if not lbl.apply_decoding]

    def __getitem__(self, index: int):
        return self.plain_bits[index]

    def __setitem__(self, index: int, value):
        """

        :type value: bool
        """
        self.plain_bits[index] = value
        self.clear_decoded_bits()
        self.clear_encoded_bits()

    def __add__(self, other):
        return self.__plain_bits + other.__plain_bits

    def _remove_labels_for_range(self, index, instant_remove=True):
        if isinstance(index, int):
            index = slice(index, index + 1, 1)

        assert isinstance(index, slice)

        start = index.start if index.start is not None else 0
        stop = index.stop
        step = index.step if index.step is not None else 1

        removed_labels = []

        for lbl in self.message_type:  # type: ProtocolLabel
            if (start <= lbl.start and stop >= lbl.end) \
                    or start <= lbl.start <= stop \
                    or (start >= lbl.start and stop <= lbl.end) \
                    or lbl.start <= start < lbl.end:
                if instant_remove:
                    self.message_type.remove(lbl)
                removed_labels.append(lbl)

            elif stop - 1 < lbl.start:
                number_elements = len(range(start, stop, step))
                l_cpy = lbl.get_copy()
                l_cpy.start -= number_elements
                l_cpy.end -= number_elements

                if instant_remove:
                    self.message_type.remove(lbl)
                    self.message_type.append(l_cpy)

        return removed_labels

    def __delitem__(self, index):
        self._remove_labels_for_range(index)
        del self.plain_bits[index]
        self.clear_decoded_bits()
        self.clear_encoded_bits()

    def __str__(self):
        return self.bits2string(self.plain_bits)

    def delete_range_without_label_range_update(self, start: int, end: int):
        del self.plain_bits[start:end]
        self.clear_decoded_bits()
        self.clear_encoded_bits()

    def get_byte_length(self, decoded=True) -> int:
        """
        Return the length of this message in byte.

        """
        end = len(self.decoded_bits) if decoded else len(self.__plain_bits)
        end = self.convert_index(end, 0, 2, decoded=decoded)[0]
        return int(end)

    def bits2string(self, bits: array.array) -> str:
        return "".join(map(str, bits))

    def __len__(self):
        return len(self.plain_bits)

    def insert(self, index: int, item: bool):
        self.plain_bits.insert(index, item)
        self.clear_decoded_bits()
        self.clear_encoded_bits()

    @property
    def decoder(self) -> Encoding:
        return self.__decoder

    @decoder.setter
    def decoder(self, val: Encoding):
        self.__decoder = val
        self.clear_decoded_bits()
        self.clear_encoded_bits()
        self.decoding_errors, self.decoding_state = self.decoder.analyze(self.plain_bits)

    @property
    def encoded_bits(self):
        """

        :rtype: array.array
        """
        if self.__encoded_bits is None:
            self.__encoded_bits = array.array("B", [])
            start = 0
            encode = self.decoder.encode
            bits = self.plain_bits

            for label in self.exclude_from_decoding_labels:
                self.__encoded_bits.extend(encode(bits[start:label.start]))
                start = label.start if label.start > start else start  # Overlapping
                self.__encoded_bits.extend(bits[start:label.end])
                start = label.end if label.end > start else start  # Overlapping

            self.__encoded_bits.extend(encode(bits[start:]))
        return self.__encoded_bits

    @property
    def encoded_bits_str(self) -> str:
        return self.bits2string(self.encoded_bits)

    @property
    def decoded_bits(self) -> array.array:
        if self.__decoded_bits is None:
            self.__decoded_bits = array.array("B", [])
            start = 0
            code = self.decoder.code  # 0 = decoded, 1 = analyzed
            # decode = self.decoder.decode
            # analyze = self.decoder.analyze
            bits = self.plain_bits
            self.decoding_errors = 0
            states = set()
            self.decoding_state = self.decoder.ErrorState.SUCCESS
            for label in self.exclude_from_decoding_labels:
                decoded, errors, state = code(True, bits[start:label.start])
                states.add(state)
                self.__decoded_bits.extend(decoded)
                self.decoding_errors += errors

                if label.start == -1 or label.end == -1:
                    label.start = len(self.__decoded_bits)
                    label.end = label.start + (label.end - label.start)

                start = label.start if label.start > start else start  # Überlappende Labels -.-
                self.__decoded_bits.extend(bits[start:label.end])
                start = label.end if label.end > start else start  # Überlappende Labels FFS >.<

            decoded, errors, state = code(True, bits[start:])
            states.add(state)
            self.__decoded_bits.extend(decoded)
            self.decoding_errors += errors

            states.discard(self.decoder.ErrorState.SUCCESS)
            if len(states) > 0:
                self.decoding_state = sorted(states)[0]

        return self.__decoded_bits

    @decoded_bits.setter
    def decoded_bits(self, val):
        self.__decoded_bits = array.array("B", val)

    @property
    def decoded_bits_str(self) -> str:
        return self.bits2string(self.decoded_bits)

    @property
    def plain_bits_str(self) -> str:
        return str(self)

    @property
    def decoded_bits_buffer(self) -> bytes:
        return self.decoded_bits.tobytes()

    @property
    def plain_hex_array(self) -> array.array:
        padded_bitchains = self.split(decode=False)
        return self.__bit_chains_to_hex(padded_bitchains)

    @property
    def plain_hex_str(self) -> str:
        return "".join(map(lambda h: "{0:x}".format(h), self.plain_hex_array))

    @property
    def plain_ascii_array(self) -> array.array:
        padded_bitchains = self.split(decode=False)
        return self.__bit_chains_to_ascii(padded_bitchains)

    @property
    def plain_ascii_str(self) -> str:
        return "".join(map(chr, self.plain_ascii_array))

    @property
    def decoded_hex_array(self) -> array.array:
        padded_bitchains = self.split()
        return self.__bit_chains_to_hex(padded_bitchains)

    @property
    def decoded_hex_str(self) -> str:
        return "".join(map(lambda h: "{0:x}".format(h), self.decoded_hex_array))

    @property
    def decoded_ascii_array(self) -> array.array:
        padded_bitchains = self.split()
        return self.__bit_chains_to_ascii(padded_bitchains)

    @property
    def decoded_ascii_str(self) -> str:
        return "".join(map(chr, self.decoded_ascii_array))

    def __get_bit_range_from_hex_or_ascii_index(self, from_index: int, decoded: bool, is_hex: bool) -> tuple:
        bits = self.decoded_bits if decoded else self.plain_bits
        factor = 4 if is_hex else 8
        for i in range(len(bits)):
            if self.__get_hex_ascii_index_from_bit_index(i, to_hex=is_hex)[0] == from_index:
                return i, i + factor - 1

        return factor * from_index, factor * (from_index+1) - 1

    def __get_hex_ascii_index_from_bit_index(self, bit_index: int, to_hex: bool) -> tuple:
        factor = 4 if to_hex else 8
        result = 0

        last_alignment = 0
        for ba in self.__bit_alignments:
            if ba <= bit_index:
                result += math.ceil((ba - last_alignment) / factor)
                last_alignment = ba
            else:
                break

        result += math.floor((bit_index - last_alignment) / factor)

        return result, result

    def convert_index(self, index: int, from_view: int, to_view: int, decoded: bool):
        if to_view == from_view:
            return index, index

        if to_view == 0:
            return self.__get_bit_range_from_hex_or_ascii_index(index, decoded, is_hex=from_view == 1)
        if to_view == 1:
            if from_view == 0:
                return self.__get_hex_ascii_index_from_bit_index(index, to_hex=True)
            elif from_view == 2:
                bi = self.__get_bit_range_from_hex_or_ascii_index(index, decoded, is_hex=True)[0]
                return self.__get_hex_ascii_index_from_bit_index(bi, to_hex=False)
        elif to_view == 2:
            if from_view == 0:
                return self.__get_hex_ascii_index_from_bit_index(index, to_hex=False)
            elif from_view == 1:
                bi = self.__get_bit_range_from_hex_or_ascii_index(index, decoded, is_hex=False)[0]
                return self.__get_hex_ascii_index_from_bit_index(bi, to_hex=True)
        else:
            raise NotImplementedError("Only Three View Types (Bit/Hex/ASCII)")

    def convert_range(self, index1: int, index2: int, from_view: int, to_view: int, decoded: bool):
        start = self.convert_index(index1, from_view, to_view, decoded)[0]
        end = self.convert_index(index2, from_view, to_view, decoded)[1]

        try:
            return int(start), int(math.ceil(end))
        except TypeError:
            return 0, 0

    def get_duration(self, sample_rate: int) -> float:
        if len(self.bit_sample_pos) < 2:
            raise ValueError("Not enough bit samples for calculating duration")

        return (self.bit_sample_pos[-1] - self.bit_sample_pos[0]) / sample_rate

    def get_src_address_from_data(self, decoded=True):
        """
        Return the SRC address of a message if SRC_ADDRESS label is present in message type of the message
        Return None otherwise

        :param decoded:
        :return:
        """
        src_address_label = next((lbl for lbl in self.message_type if lbl.field_type
                                  and lbl.field_type.function == FieldType.Function.SRC_ADDRESS), None)
        if src_address_label:
            start, end = self.get_label_range(src_address_label, view=1, decode=decoded)
            if decoded:
                src_address = self.decoded_hex_str[start:end]
            else:
                src_address = self.plain_hex_str[start:end]
        else:
            src_address = None

        return src_address

    @staticmethod
    def __bit_chains_to_hex(bit_chains) -> array.array:
        """

        :type bit_chains: list of array.array
        :return:
        """
        result = array.array("B", [])
        for bc in bit_chains:
            bc += array.array("B", [0] * ((4 - len(bc) % 4) % 4))  # pad hex view
            result.extend((8*bc[i]+4*bc[i+1]+2*bc[i+2]+bc[i+3]) for i in range(0, len(bc), 4))

        return result

    @staticmethod
    def __bit_chains_to_ascii(bit_chains) -> array.array:
        """

        :type bit_chains: list of array.array
        :return:
        """
        result = array.array("B", [])
        for bc in bit_chains:
            bc += array.array("B", [0] * ((8 - len(bc) % 8) % 8))  # pad ascii view
            result.extend((128*bc[i]+64*bc[i+1]+32*bc[i+2]+16*bc[i+3]+8*bc[i+4]+4*bc[i+5]+2*bc[i+6]+bc[i+7])
                          for i in range(0, len(bc), 8))
        return result

    def split(self, decode=True):
        """
        Für das Bit-Alignment (neu Ausrichten von Hex, ASCII-View)

        :rtype: list of array.array
        """
        start = 0
        result = []
        message = self.decoded_bits if decode else self.plain_bits
        bit_alignments = set()
        if self.align_labels:
            for l in self.message_type:
                bit_alignments.add(l.start)
                bit_alignments.add(l.end)

        self.__bit_alignments = sorted(bit_alignments)

        for pos in self.__bit_alignments:
            result.append(message[start:pos])
            start = pos

        result.append(message[start:])
        return result

    def view_to_string(self, view: int, decoded: bool, show_pauses=True, sample_rate: float = None) -> str:
        """

        :param view: 0 - Bits ## 1 - Hex ## 2 - ASCII
        """
        if view == 0:
            proto = self.decoded_bits_str if decoded else self.plain_bits_str
        elif view == 1:
            proto = self.decoded_hex_str if decoded else self.plain_hex_str
        elif view == 2:
            proto = self.decoded_ascii_str if decoded else self.plain_ascii_str
        else:
            return None

        if show_pauses:
            return '%s %s' % (proto, self.get_pause_str(sample_rate))
        else:
            return proto

    def get_pause_str(self, sample_rate):
        if sample_rate:
            return ' [<b>Pause:</b> %s]' % (Formatter.science_time(self.pause / sample_rate))
        else:
            return ' [<b>Pause:</b> %d samples]' % (self.pause)

    def clear_decoded_bits(self):
        self.__decoded_bits = None

    def clear_encoded_bits(self):
        self.__encoded_bits = None

    @staticmethod
    def from_plain_bits_str(bits, pause=0):
        plain_bits = list(map(int, bits))
        return Message(plain_bits=plain_bits, pause=pause, message_type=MessageType("none"))

    @staticmethod
    def from_plain_hex_str(hex_str, pause=0):
        lut = {"{0:x}".format(i): "{0:04b}".format(i) for i in range(16)}
        bits = "".join((lut[h] for h in hex_str))
        return Message.from_plain_bits_str(bits, pause)

    def to_xml(self, decoders=None, include_message_type=False, write_bits=False) -> ET.Element:
        root = ET.Element("message")
        root.set("message_type_id", self.message_type.id)
        root.set("modulator_index", str(self.modulator_index))
        root.set("pause", str(self.pause))
        root.set("timestamp", str(self.timestamp))

        if write_bits:
            root.set("bits", self.plain_bits_str)

        if decoders:
            try:
                decoding_index = decoders.index(self.decoder)
            except ValueError:
                logger.warning("Failed to find '{}' in list of decodings".format(self.decoder.name))
                decoding_index = 0
            root.set("decoding_index", str(decoding_index))
        if self.participant is not None:
            root.set("participant_id", self.participant.id)
        if include_message_type:
            root.append(self.message_type.to_xml())
        return root

    def from_xml(self, tag: ET.Element, participants, decoders=None, message_types=None):
        timestamp = tag.get("timestamp", None)
        if timestamp:
            self.timestamp = float(timestamp)

        part_id = tag.get("participant_id", None)
        message_type_id = tag.get("message_type_id", None)
        self.modulator_index = int(tag.get("modulator_index", self.modulator_index))
        self.pause = int(tag.get("pause", self.pause))
        decoding_index = tag.get("decoding_index", None)
        if decoding_index and decoders is not None:
            try:
                self.decoder = decoders[int(decoding_index)]
            except IndexError:
                pass

        if part_id:
            self.participant = Participant.find_matching(part_id, participants)
            if self.participant is None:
                logger.warning("No participant matched the id {0} from xml".format(part_id))

        if message_type_id and message_types:
            for message_type in message_types:
                if message_type.id == message_type_id:
                    self.message_type = message_type
                    break

        message_type_tag = tag.find("message_type")
        if message_type_tag:
            self.message_type = MessageType.from_xml(message_type_tag)

    @classmethod
    def new_from_xml(cls, tag: ET.Element, participants, decoders=None, message_types=None):
        assert "bits" in tag.attrib
        result = cls.from_plain_bits_str(bits=tag.get("bits"))
        result.from_xml(tag, participants, decoders=decoders, message_types=message_types)
        return result

    def get_label_range(self, lbl: ProtocolLabel, view: int, decode: bool, consider_alignment=False):
        a = self.alignment_offset if consider_alignment else 0
        start = self.convert_index(index=lbl.start+a, from_view=0, to_view=view, decoded=decode)[0]
        end = self.convert_index(index=lbl.end+a, from_view=0, to_view=view, decoded=decode)[1]
        return int(start), int(end)
