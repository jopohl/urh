import unittest

from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel


class TestMessageType(unittest.TestCase):
    def test_find_unlabeled_range(self):
        lbl11 = ProtocolLabel(name="Label 1.1", start=2, end=10, color_index=0)
        lbl12 = ProtocolLabel(name="Label 1.2", start=15, end=20, color_index=0)
        lbl13 = ProtocolLabel(name="Label 1.3", start=40, end=60, color_index=0)

        mt1 = MessageType(name="MT1", iterable=[lbl11, lbl12, lbl13])

        self.assertEqual([(0, 2), (11, 15), (21, 40), (61, None)], mt1.unlabeled_ranges)
        self.assertEqual(
            [(0, 2), (11, 15), (21, 40), (61, None)],
            mt1.unlabeled_ranges_with_other_mt(mt1),
        )

        lbl21 = ProtocolLabel(name="Label 2.1", start=1, end=11, color_index=0)
        lbl22 = ProtocolLabel(name="Label 2.2", start=14, end=18, color_index=0)
        lbl23 = ProtocolLabel(name="Label 2.3", start=50, end=70, color_index=0)

        mt2 = MessageType(name="MT2", iterable=[lbl21, lbl22, lbl23])

        self.assertEqual(
            mt1.unlabeled_ranges_with_other_mt(mt2),
            mt2.unlabeled_ranges_with_other_mt(mt1),
        )
        self.assertEqual(
            mt1.unlabeled_ranges_with_other_mt(mt2),
            [(0, 1), (11, 14), (21, 40), (71, None)],
        )
