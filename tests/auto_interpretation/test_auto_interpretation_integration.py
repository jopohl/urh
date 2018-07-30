import unittest

import numpy as np

from tests.test_util import get_path_for_data_file
from urh.ainterpretation import AutoInterpretation


class TestAutoInterpretationIntegration(unittest.TestCase):
    def test_auto_interpretation_fsk(self):
        fsk_signal = np.fromfile(get_path_for_data_file("fsk.complex"), dtype=np.complex64)
        AutoInterpretation.estimate(fsk_signal)

        # noise = 0.0009 // center ~= -0.0234 // bit len = 100

    def test_auto_interpretation_ask(self):
        ask_signal = np.fromfile(get_path_for_data_file("ask.complex"), dtype=np.complex64)
        AutoInterpretation.estimate(ask_signal)

        # noise ~= 0.020 // center ~= 0 // bit len = 300

    def test_auto_interpretation_enocean(self):
        enocean_signal = np.fromfile(get_path_for_data_file("enocean.complex"), dtype=np.complex64)
        AutoInterpretation.estimate(enocean_signal)

        # noise ~= 0.025 // center ~= 0.0837 // bit len = 8
