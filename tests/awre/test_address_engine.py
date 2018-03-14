import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.awre.engines.AddressEngine import AddressEngine
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Participant import Participant


class TestAddressEngine(AWRETestCase):
    def setUp(self):
        super().setUp()
        self.alice = Participant("Alice", "A", address_hex="1234")
        self.bob = Participant("Bob", "B", address_hex="5678")

    def test_one_participant(self):
        """
        Test a simple protocol with
        preamble, sync and length field (8 bit) and some random data

        :return:
        """
        mb = MessageTypeBuilder("simple_address_test")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)

        num_messages_by_data_length = {8: 5, 16: 10, 32: 15}
        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x9a9d"},
                               participants=[self.alice])
        for data_length, num_messages in num_messages_by_data_length.items():
            for i in range(num_messages):
                pg.generate_message(data=pg.decimal_to_bits(22*i, data_length), source=self.alice)

        self.save_protocol("address_one_participant", pg)

        ff = FormatFinder(pg.protocol)

        address_engine = AddressEngine(ff.bitvectors, ff.participant_indices)
        address_engine.find_addresses()

    def test_perf(self):
        from urh.cythonext import awre_util
        import time
        str1 = "11110000" * 800
        str2 = "00001111" * 800

        bits1 = np.array(list(map(int, str1)), dtype=np.uint8, order="C")
        bits2 = np.array(list(map(int, str2)), dtype=np.uint8, order="C")

        t = time.time()
        indices = awre_util.find_longest_common_bit_sequence_indices(bits1, bits2)
        print(time.time()-t)
        print(indices)
        for ind in indices:
            s = str1[slice(*ind)]
            print(s)
            print(s in str1)
            print(s in str2)

