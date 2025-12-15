import os
import tempfile
import unittest

import numpy
from urh.awre.FormatFinder import FormatFinder

from tests.utils_testing import get_path_for_data_file
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

from urh.signalprocessing.MessageType import MessageType

from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType


class AWRETestCase(unittest.TestCase):
    def setUp(self):
        numpy.set_printoptions(linewidth=80)
        self.field_types = self.__init_field_types()

    def get_format_finder_from_protocol_file(
        self, filename: str, clear_participant_addresses=True, return_messages=False
    ):
        proto_file = get_path_for_data_file(filename)
        protocol = ProtocolAnalyzer(signal=None, filename=proto_file)
        protocol.from_xml_file(filename=proto_file, read_bits=True)

        self.clear_message_types(protocol.messages)

        ff = FormatFinder(protocol.messages)
        if clear_participant_addresses:
            ff.known_participant_addresses.clear()

        if return_messages:
            return ff, protocol.messages
        else:
            return ff

    @staticmethod
    def __init_field_types():
        result = []
        for field_type_function in FieldType.Function:
            result.append(FieldType(field_type_function.value, field_type_function))
        return result

    @staticmethod
    def clear_message_types(messages: list):
        mt = MessageType("empty")
        for msg in messages:
            msg.message_type = mt

    @staticmethod
    def save_protocol(name, protocol_generator, silent=False):
        filename = os.path.join(tempfile.gettempdir(), name + ".proto")
        if isinstance(protocol_generator, ProtocolGenerator):
            protocol_generator.to_file(filename)
        elif isinstance(protocol_generator, ProtocolAnalyzer):
            participants = list(
                set(msg.participant for msg in protocol_generator.messages)
            )
            protocol_generator.to_xml_file(
                filename, [], participants=participants, write_bits=True
            )
        info = "Protocol written to " + filename
        if not silent:
            print()
            print("-" * len(info))
            print(info)
            print("-" * len(info))
