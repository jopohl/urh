import unittest


from urh.awre.FormatFinder import FormatFinder
from urh.awre.components.Address import Address
from urh.awre.components.Flags import Flags
from urh.awre.components.Length import Length
from urh.awre.components.Preamble import Preamble
from urh.awre.components.SequenceNumber import SequenceNumber
from urh.awre.components.Type import Type
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Message import Message




from urh.cythonext import util
class TestAWRE(unittest.TestCase):
    def setUp(self):
        self.protocol = ProtocolAnalyzer(None)
        with open("./data/awre_consistent_addresses.txt") as f:
            for line in f:
                self.protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", ""), {}))
                self.protocol.messages[-1].message_type = self.protocol.default_message_type

        # Assign participants
        alice = Participant("Alice", "A")
        bob = Participant("Bob", "B")
        alice_indices = {1, 2, 5, 6, 9, 10, 13, 14, 17, 18, 20, 22, 23, 26, 27, 30, 31, 34, 35, 38, 39, 41}
        for i, block in enumerate(self.protocol.messages):
            block.participant = alice if i in alice_indices else bob

        self.participants = [alice, bob]

    def test_build_component_order(self):
        expected_default = [Preamble(), Length(None), Address(None, None), SequenceNumber(), Type(), Flags()]

        format_finder = FormatFinder(self.protocol)

        for expected, actual in zip(expected_default, format_finder.build_component_order()):
            assert type(expected) == type(actual)

        expected_swapped = [Preamble(), Address(None, None), Length(None), SequenceNumber(), Type(), Flags()]
        format_finder.length_component.priority = 3
        format_finder.address_component.priority = 2

        for expected, actual in zip(expected_swapped, format_finder.build_component_order()):
            assert type(expected) == type(actual)

        # Test duplicate Priority
        format_finder.sequence_number_component.priority = 5
        with self.assertRaises(ValueError) as context:
            format_finder.build_component_order()
            self.assertTrue('Duplicate priority' in context.exception)
        format_finder.sequence_number_component.priority = 4
        self.assertTrue(format_finder.build_component_order())

    def test_format_finding_rwe(self):
        preamble_start = 0
        preamble_end = 31
        sync_start = 32
        sync_end = 63
        length_start = 64
        length_end = 71

        preamble_label = ProtocolLabel(name="Preamble", start=preamble_start, end=preamble_end, color_index=0)
        sync_label = ProtocolLabel(name="Synchronization", start=sync_start, end=sync_end, color_index=1)
        length_label = ProtocolLabel(name="Length", start=length_start, end=length_end, color_index=2)


        ff = FormatFinder(self.protocol, self.participants)
        ff.perform_iteration()

        self.assertIn(preamble_label, self.protocol.default_message_type)
        self.assertIn(sync_label, self.protocol.default_message_type)
        self.assertIn(length_label, self.protocol.default_message_type)


    def test_format_finding_enocean(self):
        enocean_protocol = ProtocolAnalyzer(None)
        with open("./data/enocean_bits.txt") as f:
            for line in f:
                enocean_protocol.messages.append(Message.from_plain_bits_str(line.replace("\n", ""), {}))
                enocean_protocol.messages[-1].message_type = enocean_protocol.default_message_type


        preamble_start = 3
        preamble_end = 10
        sof_start = 11
        sof_end = 14

        preamble_label = ProtocolLabel(name="Preamble", start=preamble_start, end=preamble_end, color_index=0)
        sync_label = ProtocolLabel(name="Synchronization", start=sof_start, end=sof_end, color_index=1)


        ff = FormatFinder(enocean_protocol, self.participants)
        ff.perform_iteration()

        self.assertIn(preamble_label, enocean_protocol.default_message_type)
        self.assertIn(sync_label, enocean_protocol.default_message_type)
        self.assertTrue(not any(lbl.name == "Length" for lbl in enocean_protocol.default_message_type))


    def test_address_candidate_finding(self):
        candidates_participant_1 = ['1b6033', '1b6033fd57', '701b603378e289', '20701b603378e289000c62']
        candidates_participant_2 = ['1b603300', '78e289757e', '7078e2891b6033000000', '207078e2891b6033000000']

        expected_address1 = '1b6033'
        expected_address2 = '78e289'
        import time
        t = time.time()
        assert util.longest_common_substring("'78e289757e'", "'7078e2891b6033000000'") == "78e289"
        print((time.time()-t)*10**6)

