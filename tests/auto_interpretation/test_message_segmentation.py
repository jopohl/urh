import unittest

import numpy as np

from tests.test_util import get_path_for_data_file
from urh.ainterpretation.AutoInterpretation import segment_messages_from_magnitudes


class TestMessageSegmentation(unittest.TestCase):
    def test_segmentation_for_fsk(self):
        signal = np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)
        segments = segment_messages_from_magnitudes(np.abs(signal), 0.0009)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], (0, 17742))

    def test_segmentation_for_ask(self):
        signal = np.fromfile(get_path_for_data_file("ask.complex"), dtype=np.complex64)
        segments = segment_messages_from_magnitudes(np.abs(signal), 0.02)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], (462, 12011))

    def test_segmentation_enocean_multiple_messages(self):
        signal = np.fromfile(get_path_for_data_file("enocean.complex"), dtype=np.complex64)
        segments = segment_messages_from_magnitudes(np.abs(signal), 0.025)
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0], (6086, 6753))
        self.assertEqual(segments[1], (9751, 10417))
        self.assertEqual(segments[2], (22208, 22876))
