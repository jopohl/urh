import unittest

import numpy as np

from tests.test_util import get_path_for_data_file
from urh.ainterpretation.AutoInterpretation import (
    segment_messages_from_magnitudes,
    merge_message_segments_for_ook,
)
from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Signal import Signal


class TestMessageSegmentation(unittest.TestCase):
    def test_segmentation_for_fsk(self):
        signal = np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)
        segments = segment_messages_from_magnitudes(np.abs(signal), 0.0009)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], (0, 17742))

    def test_segmentation_for_ask(self):
        signal = np.fromfile(get_path_for_data_file("ask.complex"), dtype=np.complex64)
        segments = segment_messages_from_magnitudes(np.abs(signal), 0.02)
        segments = merge_message_segments_for_ook(segments)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], (462, 12011))

    def test_segmentation_enocean_multiple_messages(self):
        signal = np.fromfile(
            get_path_for_data_file("enocean.complex"), dtype=np.complex64
        )
        segments = segment_messages_from_magnitudes(np.abs(signal), 0.0448)
        segments = merge_message_segments_for_ook(segments)
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0], (2107, 5432))
        self.assertEqual(segments[1], (20428, 23758))
        self.assertEqual(segments[2], (44216, 47546))

    def test_message_segmentation_fsk_xavax(self):
        signal = Signal(get_path_for_data_file("xavax.coco"), "")
        segments = segment_messages_from_magnitudes(
            signal.iq_array.magnitudes, noise_threshold=0.002
        )

        # Signal starts with overdrive, so one message more
        self.assertTrue(len(segments) == 6 or len(segments) == 7)
        if len(segments) == 7:
            segments = segments[1:]

        self.assertEqual(
            segments,
            [
                (275146, 293697),
                (321073, 338819),
                (618213, 1631898),
                (1657890, 1678041),
                (1803145, 1820892),
                (1846213, 1866364),
            ],
        )

    def test_segmentation_ask_50(self):
        modulator = Modulator("ask50")
        modulator.modulation_type = "ASK"
        modulator.parameters[0] = 50
        modulator.parameters[1] = 100
        modulator.samples_per_symbol = 100

        msg1 = modulator.modulate("1010101111", pause=10000)
        msg2 = modulator.modulate("1010101110010101", pause=20000)
        msg3 = modulator.modulate("1010101010101111", pause=30000)

        data = IQArray.concatenate((msg1, msg2, msg3))

        segments = segment_messages_from_magnitudes(data.magnitudes, noise_threshold=0)
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments, [(0, 999), (10999, 12599), (32599, 34199)])

    def test_segmentation_elektromaten(self):
        signal = Signal(get_path_for_data_file("elektromaten.complex16s"), "")

        signal.noise_threshold_relative = 0.1

        segments = segment_messages_from_magnitudes(
            signal.iq_array.magnitudes, noise_threshold=signal.noise_threshold
        )
        segments = merge_message_segments_for_ook(segments)

        self.assertEqual(len(segments), 11)

    def test_ook_merge(self):
        input = [
            (26728, 27207),
            (28716, 29216),
            (30712, 32190),
            (32695, 34178),
            (34686, 35181),
            (36683, 38181),
            (38670, 39165),
            (40668, 42154),
            (42659, 44151),
            (44642, 46139),
            (46634, 47121),
            (47134, 47145),
            (48632, 50129),
            (50617, 51105),
            (52612, 54089),
            (54100, 54113),
            (54601, 56095),
            (56592, 58075),
            (58581, 59066),
            (59076, 59091),
            (60579, 61081),
            (62567, 64063),
            (64559, 66053),
            (66548, 67035),
            (68539, 69031),
            (70533, 71035),
            (72527, 73008),
            (73019, 73035),
            (74522, 75006),
            (90465, 90958),
            (92456, 92944),
            (94455, 95935),
            (96441, 97930),
            (98437, 98937),
            (100430, 101914),
            (102414, 102901),
            (104413, 105889),
            (106398, 107895),
            (108389, 109873),
            (110385, 110877),
            (112374, 113853),
            (114367, 114862),
            (116355, 117842),
            (118344, 119826),
            (120340, 121824),
            (122324, 122825),
            (124323, 124821),
            (126316, 127807),
            (128300, 129782),
            (130293, 130777),
            (132280, 132774),
            (134275, 134773),
            (136266, 136767),
            (138265, 138751),
            (154205, 154694),
            (156206, 156703),
            (158191, 159685),
            (160189, 161683),
            (162176, 162667),
            (164164, 165657),
            (166159, 166648),
            (168147, 169631),
            (170145, 171621),
            (172131, 173611),
            (174125, 174607),
            (176118, 177600),
            (178105, 178590),
            (180093, 181574),
            (181585, 181599),
            (182090, 183573),
            (184074, 185565),
            (186070, 186553),
            (188061, 188555),
            (190052, 191533),
            (192043, 193523),
            (194034, 194518),
            (196021, 196510),
            (198012, 198503),
            (200014, 200496),
            (202003, 202485),
            (202498, 202511),
            (217953, 218430),
            (218442, 218457),
            (219940, 220426),
            (221935, 223431),
            (223926, 225409),
            (225912, 226399),
            (227912, 229387),
            (229896, 230382),
            (231886, 233369),
            (233383, 233393),
            (233882, 235375),
            (235874, 237357),
            (237858, 238361),
            (239850, 241343),
            (241844, 242328),
            (243840, 245331),
            (245828, 247306),
            (247820, 249296),
            (249811, 250298),
            (251803, 252283),
            (252296, 252309),
            (253790, 255271),
            (255778, 257276),
            (257774, 258258),
            (259764, 260257),
            (261760, 262239),
            (263744, 264241),
            (265744, 266225),
            (281684, 282171),
            (283676, 284163),
            (285668, 287153),
            (287665, 289149),
            (289654, 290145),
            (291642, 293131),
            (293633, 294120),
            (295629, 297104),
            (297116, 297129),
        ]

        merged = merge_message_segments_for_ook(input)
        self.assertEqual(len(merged), 5)
