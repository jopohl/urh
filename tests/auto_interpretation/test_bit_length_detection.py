import unittest
import numpy as np

from urh.ainterpretation import AutoInterpretation


class TestAutoInterpretation(unittest.TestCase):
    def __run_merge(self, data):
        return list(
            AutoInterpretation.merge_plateau_lengths(np.array(data, dtype=np.uint64))
        )

    def test_merge_plateau_lengths(self):
        self.assertEqual(AutoInterpretation.merge_plateau_lengths([]), [])
        self.assertEqual(AutoInterpretation.merge_plateau_lengths([42]), [42])
        self.assertEqual(
            AutoInterpretation.merge_plateau_lengths([100, 100, 100]), [100, 100, 100]
        )
        self.assertEqual(self.__run_merge([100, 49, 1, 50, 100]), [100, 100, 100])
        self.assertEqual(self.__run_merge([100, 48, 2, 50, 100]), [100, 100, 100])
        self.assertEqual(
            self.__run_merge([100, 100, 67, 1, 10, 1, 21]), [100, 100, 100]
        )
        self.assertEqual(
            self.__run_merge([100, 100, 67, 1, 10, 1, 21, 100, 50, 1, 49]),
            [100, 100, 100, 100, 100],
        )

    def test_estimate_tolerance_from_plateau_lengths(self):
        self.assertEqual(
            AutoInterpretation.estimate_tolerance_from_plateau_lengths([]), None
        )
        self.assertEqual(
            AutoInterpretation.estimate_tolerance_from_plateau_lengths([10]), None
        )
        self.assertEqual(
            AutoInterpretation.estimate_tolerance_from_plateau_lengths(
                [100, 49, 1, 50, 100]
            ),
            1,
        )
        self.assertEqual(
            AutoInterpretation.estimate_tolerance_from_plateau_lengths(
                [100, 49, 2, 50, 100]
            ),
            2,
        )
        self.assertEqual(
            AutoInterpretation.estimate_tolerance_from_plateau_lengths(
                [100, 49, 2, 50, 100, 1]
            ),
            2,
        )
        self.assertEqual(
            AutoInterpretation.estimate_tolerance_from_plateau_lengths([8, 8, 6, 1, 1]),
            1,
        )

    def test_tolerant_greatest_common_divisor(self):
        self.assertEqual(AutoInterpretation.get_tolerant_greatest_common_divisor([]), 1)
        self.assertEqual(
            AutoInterpretation.get_tolerant_greatest_common_divisor([22]), 1
        )
        self.assertEqual(
            AutoInterpretation.get_tolerant_greatest_common_divisor([10, 5, 5]), 5
        )
        self.assertEqual(
            AutoInterpretation.get_tolerant_greatest_common_divisor([100, 100, 100]),
            100,
        )
        self.assertEqual(
            AutoInterpretation.get_tolerant_greatest_common_divisor(
                [100, 100, 200, 300, 100, 400]
            ),
            100,
        )
        self.assertEqual(
            AutoInterpretation.get_tolerant_greatest_common_divisor(
                [100, 101, 100, 100]
            ),
            100,
        )
        self.assertEqual(
            AutoInterpretation.get_tolerant_greatest_common_divisor(
                [100, 101, 202, 301, 100, 500]
            ),
            100,
        )

    def test_get_bit_length_from_plateau_length(self):
        self.assertEqual(AutoInterpretation.get_bit_length_from_plateau_lengths([]), 0)
        self.assertEqual(
            AutoInterpretation.get_bit_length_from_plateau_lengths([42]), 42
        )
        plateau_lengths = np.array(
            [
                2,
                1,
                2,
                73,
                1,
                26,
                100,
                40,
                1,
                59,
                100,
                47,
                1,
                52,
                67,
                1,
                10,
                1,
                21,
                33,
                1,
                66,
                100,
                5,
                1,
                3,
                1,
                48,
                1,
                27,
                1,
                8,
            ],
            dtype=np.uint64,
        )
        merged_lengths = AutoInterpretation.merge_plateau_lengths(plateau_lengths)
        self.assertEqual(
            AutoInterpretation.get_bit_length_from_plateau_lengths(merged_lengths), 100
        )

        plateau_lengths = np.array(
            [
                1,
                292,
                331,
                606,
                647,
                286,
                645,
                291,
                334,
                601,
                339,
                601,
                338,
                602,
                337,
                603,
                338,
                604,
                336,
                605,
                337,
                600,
                338,
                605,
                646,
            ],
            dtype=np.uint64,
        )
        merged_lengths = AutoInterpretation.merge_plateau_lengths(plateau_lengths)
        self.assertEqual(
            AutoInterpretation.get_bit_length_from_plateau_lengths(merged_lengths), 300
        )

        plateau_lengths = np.array(
            [
                3,
                8,
                8,
                8,
                8,
                8,
                8,
                8,
                8,
                16,
                8,
                8,
                16,
                32,
                8,
                8,
                8,
                8,
                8,
                24,
                8,
                24,
                8,
                24,
                8,
                24,
                8,
                24,
                16,
                16,
                24,
                8,
            ],
            dtype=np.uint64,
        )
        merged_lengths = AutoInterpretation.merge_plateau_lengths(plateau_lengths)
        self.assertEqual(
            AutoInterpretation.get_bit_length_from_plateau_lengths(merged_lengths), 8
        )

    def test_get_bit_length_from_merged_plateau_lengths(self):
        merged_lengths = np.array(
            [40, 40, 40, 40, 40, 30, 50, 30, 90, 40, 40, 80, 160, 30, 50, 30],
            dtype=np.uint64,
        )
        self.assertEqual(
            AutoInterpretation.get_bit_length_from_plateau_lengths(merged_lengths), 40
        )
