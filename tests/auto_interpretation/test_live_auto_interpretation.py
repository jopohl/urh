import unittest

from tests.auto_interpretation import auto_interpretation_test_util
from urh.signalprocessing.Modulator import Modulator


class TestLiveAutoInterpretation(unittest.TestCase):
    def test_without_noise(self):
        modulator = Modulator("FSK_mod")
        modulator.modulation_type_str = "FSK"
        modulator.samples_per_bit = 100
        modulator.param_for_zero = 10e3
        modulator.param_for_one = 20e3
        modulator.sample_rate = 1e6

        messages = auto_interpretation_test_util.generate_random_messages(num_messages=5,
                                                                          num_bits=80,
                                                                          preamble="1010101010101010",
                                                                          sync="1001101010011100",
                                                                          eof="0110",
                                                                          message_pause=1000)

        sdr_chunk_size = 32768

        full_signal = auto_interpretation_test_util.generate_signal(messages, modulator, 0, add_noise=False)

        for i in range(0, len(full_signal), sdr_chunk_size):
            # TODO
            pass