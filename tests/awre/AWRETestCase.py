import os
import tempfile
import unittest

import numpy
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

from urh.signalprocessing.MessageType import MessageType

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
    def clear_message_types(messages: list):
        mt = MessageType("empty")
        for msg in messages:
            msg.message_type = mt

    @staticmethod
    def save_protocol(name, protocol_generator):
        filename = os.path.join(tempfile.gettempdir(), name + ".proto")
        if isinstance(protocol_generator, ProtocolGenerator):
            protocol_generator.to_file(filename)
        elif isinstance(protocol_generator, ProtocolAnalyzer):
            protocol_generator.to_xml_file(filename, [], [], write_bits=True)
        info = "Protocol written to " + filename
        print()
        print("-" * len(info))
        print(info)
        print("-" * len(info))
