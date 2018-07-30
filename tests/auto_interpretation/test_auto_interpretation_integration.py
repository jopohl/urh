import unittest

import numpy as np

from urh.ainterpretation import AutoInterpretation


class TestAutoInterpretationIntegration(unittest.TestCase):
    def test_get_bit_length_from_magnitudes(self):

        # todo: adapt to new API
        fsk_signal = np.fromfile("fsk.complex", dtype=np.complex64)
        message_indices = AutoInterpretation.segment_messages_from_magnitudes(np.abs(fsk_signal), 0.0009, q=2)
        demod_signal = np.fromfile("fsk-demodulated.complex", dtype=np.float32)
        #self.assertEqual(AutoInterpretation.get_bit_length_from_signal(demod_signal, message_indices, center=-0.0234), 100)

        ask_signal = np.fromfile("ask.complex", dtype=np.complex64)
        message_indices = AutoInterpretation.segment_messages_from_magnitudes(np.abs(ask_signal), 0.020, q=2)
        demod_signal = np.fromfile("ask-demodulated.complex", dtype=np.float32)
        #self.assertEqual(AutoInterpretation.get_bit_length_from_signal(demod_signal, message_indices, center=0), 300)

        enocean_signal = np.fromfile("enocean.complex", dtype=np.complex64)
        message_indices = AutoInterpretation.segment_messages_from_magnitudes(np.abs(enocean_signal), 0.025, q=2)
        demod_signal = np.fromfile("enocean-demodulated.complex", dtype=np.float32)
        #self.assertEqual(AutoInterpretation.get_bit_length_from_signal(demod_signal, message_indices, center=0.0837), 8)