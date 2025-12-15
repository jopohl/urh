import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.CommonRange import CommonRange, CommonRangeContainer
from urh.awre.FormatFinder import FormatFinder


class TestFormatFinder(AWRETestCase):
    def test_create_message_types_1(self):
        rng1 = CommonRange(0, 8, "1" * 8, score=1, field_type="Length")
        rng1.message_indices = {0, 1, 2}
        rng2 = CommonRange(8, 8, "1" * 8, score=1, field_type="Address")
        rng2.message_indices = {0, 1, 2}

        message_types = FormatFinder.create_common_range_containers({rng1, rng2})
        self.assertEqual(len(message_types), 1)

        expected = CommonRangeContainer([rng1, rng2], message_indices={0, 1, 2})
        self.assertEqual(message_types[0], expected)

    def test_create_message_types_2(self):
        rng1 = CommonRange(0, 8, "1" * 8, score=1, field_type="Length")
        rng1.message_indices = {0, 2, 4, 6, 8, 12}
        rng2 = CommonRange(8, 8, "1" * 8, score=1, field_type="Address")
        rng2.message_indices = {1, 2, 3, 4, 5, 12}
        rng3 = CommonRange(16, 8, "1" * 8, score=1, field_type="Seq")
        rng3.message_indices = {1, 3, 5, 7, 12}

        message_types = FormatFinder.create_common_range_containers({rng1, rng2, rng3})
        expected1 = CommonRangeContainer([rng1], message_indices={0, 6, 8})
        expected2 = CommonRangeContainer([rng1, rng2], message_indices={2, 4})
        expected3 = CommonRangeContainer([rng1, rng2, rng3], message_indices={12})
        expected4 = CommonRangeContainer([rng2, rng3], message_indices={1, 3, 5})
        expected5 = CommonRangeContainer([rng3], message_indices={7})

        self.assertEqual(len(message_types), 5)

        self.assertIn(expected1, message_types)
        self.assertIn(expected2, message_types)
        self.assertIn(expected3, message_types)
        self.assertIn(expected4, message_types)
        self.assertIn(expected5, message_types)

    def test_retransform_message_indices(self):
        sync_ends = np.array([12, 12, 12, 14, 14])

        rng = CommonRange(
            0, 8, "1" * 8, score=1, field_type="length", message_indices={0, 1, 2, 3, 4}
        )
        retransformed_ranges = FormatFinder.retransform_message_indices(
            [rng], [0, 1, 2, 3, 4], sync_ends
        )

        # two different sync ends
        self.assertEqual(len(retransformed_ranges), 2)

        expected1 = CommonRange(
            12, 8, "1" * 8, score=1, field_type="length", message_indices={0, 1, 2}
        )
        expected2 = CommonRange(
            14, 8, "1" * 8, score=1, field_type="length", message_indices={3, 4}
        )

        self.assertIn(expected1, retransformed_ranges)
        self.assertIn(expected2, retransformed_ranges)

    def test_handle_no_overlapping_conflict(self):
        rng1 = CommonRange(0, 8, "1" * 8, score=1, field_type="Length")
        rng1.message_indices = {0, 1, 2}
        rng2 = CommonRange(8, 8, "1" * 8, score=1, field_type="Address")
        rng2.message_indices = {0, 1, 2}

        container = CommonRangeContainer([rng1, rng2], message_indices={0, 1, 2})

        # no conflict
        result = FormatFinder.handle_overlapping_conflict([container])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 2)
        self.assertIn(rng1, result[0])
        self.assertEqual(result[0].message_indices, {0, 1, 2})
        self.assertIn(rng2, result[0])

    def test_handle_easy_overlapping_conflict(self):
        # Easy conflict: First Label has higher score
        rng1 = CommonRange(8, 8, "1" * 8, score=1, field_type="Length")
        rng1.message_indices = {0, 1, 2}
        rng2 = CommonRange(8, 8, "1" * 8, score=0.8, field_type="Address")
        rng2.message_indices = {0, 1, 2}

        container = CommonRangeContainer([rng1, rng2], message_indices={0, 1, 2})
        result = FormatFinder.handle_overlapping_conflict([container])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 1)
        self.assertIn(rng1, result[0])
        self.assertEqual(result[0].message_indices, {0, 1, 2})

    def test_handle_medium_overlapping_conflict(self):
        rng1 = CommonRange(8, 8, "1" * 8, score=1, field_type="Length")
        rng2 = CommonRange(4, 10, "1" * 8, score=0.8, field_type="Address")
        rng3 = CommonRange(15, 20, "1" * 8, score=1, field_type="Seq")
        rng4 = CommonRange(60, 80, "1" * 8, score=0.8, field_type="Type")
        rng5 = CommonRange(70, 90, "1" * 8, score=0.9, field_type="Data")

        container = CommonRangeContainer([rng1, rng2, rng3, rng4, rng5])
        result = FormatFinder.handle_overlapping_conflict([container])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 3)
        self.assertIn(rng1, result[0])
        self.assertIn(rng3, result[0])
        self.assertIn(rng5, result[0])
