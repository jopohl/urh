import unittest

from urh.awre.FormatFinder import FormatFinder
from urh.awre.components.Address import Address
from urh.awre.components.Flags import Flags
from urh.awre.components.Length import Length
from urh.awre.components.Preamble import Preamble
from urh.awre.components.SequenceNumber import SequenceNumber
from urh.awre.components.Synchronization import Synchronization
from urh.awre.components.Type import Type


class TestAWRE(unittest.TestCase):
    def test_build_component_order(self):
        expected_default = [Preamble(), Synchronization(), Length(), Address(), SequenceNumber(), Type(), Flags()]

        format_finder = FormatFinder()

        for expected, actual in zip(expected_default, format_finder.build_component_order()):
            assert type(expected) == type(actual)

        expected_swapped = [Preamble(), Synchronization(), Address(), Length(), SequenceNumber(), Type(), Flags()]
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

        # Test invalid predecessor order
        format_finder.sync_component.priority = 0
        format_finder.preamble_component.priority = 1
        with self.assertRaises(ValueError) as context:
            format_finder.build_component_order()
            self.assertTrue('comes before at least one of its predecessors' in context.exception)
        format_finder.sync_component.priority = 1
        format_finder.preamble_component.priority = 0
        self.assertTrue(format_finder.build_component_order())

