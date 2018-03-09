import os
import tempfile
import unittest

import numpy

from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType


class AWRETestCase(unittest.TestCase):
    def setUp(self):
        numpy.set_printoptions(linewidth=80)
        self.field_types = self.__init_field_types()

    @staticmethod
    def __init_field_types():
        result = []
        for field_type_function in FieldType.Function:
            result.append(FieldType(field_type_function.value, field_type_function))
        return result

    @staticmethod
    def build_protocol_generator(preamble_syncs: list, num_messages: tuple, data: tuple) -> ProtocolGenerator:
        message_types = []
        preambles_by_mt = dict()
        syncs_by_mt = dict()

        assert len(preamble_syncs) == len(num_messages) == len(data)

        for i, (preamble, sync_word) in enumerate(preamble_syncs):
            assert isinstance(preamble, str)
            assert isinstance(sync_word, str)

            preamble, sync_word = map(ProtocolGenerator.to_bits, (preamble, sync_word))

            mb = MessageTypeBuilder("message type #{0}".format(i))
            mb.add_label(FieldType.Function.PREAMBLE, len(preamble))
            mb.add_label(FieldType.Function.SYNC, len(sync_word))

            message_types.append(mb.message_type)
            preambles_by_mt[mb.message_type] = preamble
            syncs_by_mt[mb.message_type] = sync_word

        pg = ProtocolGenerator(message_types, preambles_by_mt=preambles_by_mt, syncs_by_mt=syncs_by_mt)
        for i, msg_type in enumerate(message_types):
            for j in range(num_messages[i]):
                if callable(data[i]):
                    msg_data = pg.decimal_to_bits(data[i](j), num_bits=8)
                else:
                    msg_data = data[i]

                pg.generate_message(message_type=msg_type, data=msg_data)

        return pg

    @staticmethod
    def save_protocol(name, protocol_generator):
        filename = os.path.join(tempfile.gettempdir(), name + ".proto")
        protocol_generator.to_file(filename)
        info = "Protocol written to " + filename
        print()
        print("-" * len(info))
        print(info)
        print("-" * len(info))
