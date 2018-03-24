import struct
from collections import defaultdict

import math

from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class ProtocolGenerator(object):
    DEFAULT_PREAMBLE = "10101010"
    DEFAULT_SYNC = "1001"
    BROADCAST_ADDRESS = "0xffff"

    def __init__(self, message_types: list, participants: list = None, preambles_by_mt=None,
                 syncs_by_mt=None, little_endian=True, length_in_bytes=True, sequence_numbers=None):
        """

        :param message_types:
        :param participants:
        :param preambles_by_mt:
        :param syncs_by_mt:
        :param byte_order:
        :param length_in_bytes: If false length will be given in bit
        """
        self.participants = participants if participants is not None else []

        self.protocol = ProtocolAnalyzer(None)
        self.protocol.message_types = message_types

        self.length_in_bytes = length_in_bytes
        self.little_endian = little_endian

        preambles_by_mt = dict() if preambles_by_mt is None else preambles_by_mt

        self.preambles_by_message_type = defaultdict(lambda: self.DEFAULT_PREAMBLE)
        for mt, preamble in preambles_by_mt.items():
            self.preambles_by_message_type[mt] = self.to_bits(preamble)

        syncs_by_mt = dict() if syncs_by_mt is None else syncs_by_mt

        self.syncs_by_message_type = defaultdict(lambda: self.DEFAULT_SYNC)
        for mt, sync in syncs_by_mt.items():
            self.syncs_by_message_type[mt] = self.to_bits(sync)

        sequence_numbers = dict() if sequence_numbers is None else sequence_numbers
        self.sequence_numbers = defaultdict(lambda: 0)

        for mt, seq in sequence_numbers.items():
            self.sequence_numbers[mt] = seq



    def __get_address_for_participant(self, participant: Participant):
        if participant is None:
            return self.to_bits(self.BROADCAST_ADDRESS)

        address = "0x" + participant.address_hex if not participant.address_hex.startswith("0x") else participant.address_hex
        return self.to_bits(address)

    @staticmethod
    def to_bits(bit_or_hex_str: str):
        if bit_or_hex_str.startswith("0x"):
            lut = {"{0:x}".format(i): "{0:04b}".format(i) for i in range(16)}
            return "".join(lut[c] for c in bit_or_hex_str[2:])
        else:
            return bit_or_hex_str

    def decimal_to_bits(self, number: int, num_bits: int) -> str:
        len_formats = {8: "B", 16: "H", 32: "I", 64: "Q"}
        if num_bits not in len_formats:
            raise ValueError("Invalid length for length field: {} bits".format(num_bits))

        struct_format = "<" if self.little_endian else ">"
        struct_format += len_formats[num_bits]

        byte_length = struct.pack(struct_format, number)
        return "".join("{0:08b}".format(byte) for byte in byte_length)

    def generate_message(self, message_type=None, data="0x00", source: Participant=None, destination: Participant=None):
        for participant in (source, destination):
            if isinstance(participant, Participant) and participant not in self.participants:
                self.participants.append(participant)

        if isinstance(message_type, MessageType):
            index = self.protocol.message_types.index(message_type)
        elif isinstance(message_type, int):
            index = message_type
        else:
            index = 0

        data = self.to_bits(data)

        mt = self.protocol.message_types[index]  # type: MessageType
        mt.sort()

        bits = []

        start = 0

        message_length = mt[-1].end - 1 + len(data)

        for lbl in mt:  # type: ProtocolLabel
            bits.append("0"*(lbl.start - start))
            len_field = lbl.end - lbl.start  # in bits

            if lbl.field_type.function == FieldType.Function.PREAMBLE:
                preamble = self.preambles_by_message_type[mt]
                assert len(preamble) == len_field
                bits.append(preamble)
                message_length -= len(preamble)
            elif lbl.field_type.function == FieldType.Function.SYNC:
                sync = self.syncs_by_message_type[mt]
                assert len(sync) == len_field
                bits.append(sync)
                message_length -= len(sync)
            elif lbl.field_type.function == FieldType.Function.LENGTH:
                value = int(math.ceil(message_length / 8))

                if not self.length_in_bytes:
                    value *= 8

                bits.append(self.decimal_to_bits(value, len_field))
            elif lbl.field_type.function == FieldType.Function.TYPE:
                bits.append(self.decimal_to_bits(hash(mt) % (2 ** len_field), len_field))
            elif lbl.field_type.function == FieldType.Function.SEQUENCE_NUMBER:
                bits.append(self.decimal_to_bits(self.sequence_numbers[mt], len_field))
            elif lbl.field_type.function == FieldType.Function.DST_ADDRESS:
                dst_bits = self.__get_address_for_participant(destination)

                if len(dst_bits) != len_field:
                    raise ValueError("Length of dst ({0} bits) != length dst field ({1} bits)".format(len(dst_bits), len_field))

                bits.append(dst_bits)
            elif lbl.field_type.function == FieldType.Function.SRC_ADDRESS:
                src_bits = self.__get_address_for_participant(source)

                if len(src_bits) != len_field:
                    raise ValueError("Length of src ({0} bits) != length src field ({1} bits)".format(len(src_bits), len_field))

                bits.append(src_bits)

            start = lbl.end

        bits.append(data)

        msg = Message.from_plain_bits_str("".join(bits))
        msg.message_type = mt
        msg.participant = source
        self.sequence_numbers[mt] += 1

        self.protocol.messages.append(msg)

    def to_file(self, filename: str):
        self.protocol.to_xml_file(filename, [], self.participants, write_bits=True)

if __name__ == '__main__':
    mb = MessageTypeBuilder("test")
    mb.add_label(FieldType.Function.PREAMBLE, 8)
    mb.add_label(FieldType.Function.SYNC, 4)
    mb.add_label(FieldType.Function.LENGTH, 8)
    mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)
    mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
    mb.add_label(FieldType.Function.DST_ADDRESS, 16)
    pg = ProtocolGenerator([mb.message_type], [], little_endian=False)
    pg.generate_message(data="1"*8)
    pg.generate_message(data="1"*16)
    pg.generate_message(data="0xab", source=Participant("Alice", "A", "1234"), destination=Participant("Bob", "B", "4567"))
    pg.to_file("/tmp/test.proto")
