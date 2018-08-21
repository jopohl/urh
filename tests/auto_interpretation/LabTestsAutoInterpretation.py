import unittest

import numpy as np

from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator
from typing import List

class LabTestsAutoInterpretation(unittest.TestCase):
    def rms(self, data):
        return np.sqrt(np.mean(np.square(data)))

    def generate_signal(self, messages: List[Message], modulator: Modulator, snr_db):
        result = []
        for msg in messages:
            result.append(modulator.modulate(msg.encoded_bits, msg.pause))

        result = np.concatenate(result)
        noise = np.random.normal(loc=0, scale=1, size=2*len(result)).astype(np.float32)

        ratio = 10 ** (snr_db / 10)
        # rms of data signal is carrier amplitude
        rms_data = modulator.carrier_amplitude
        if modulator.modulation_type_str == "ASK":
            rms_data *= max(modulator.param_for_zero, modulator.param_for_one) / 100
        target_noise_rms = rms_data / np.sqrt(ratio)
        noise = target_noise_rms * (noise / self.rms(noise))

        #print("SNR", 10 * np.log10((rms_data / self.rms(noise))**2))

        return result + noise.view(np.complex64)

    def test_fsk(self):
        modulator = Modulator("")
        modulator.samples_per_bit = 100
        modulator.modulation_type_str = "FSK"
        modulator.param_for_zero = -20e3
        modulator.param_for_one = 20e3
        modulator.sample_rate = 100e3
        modulator.carrier_amplitude = 1

        msg = Message.from_plain_bits_str("10101010111000", pause=1000)

        signal = self.generate_signal([msg], modulator, snr_db=20)

        signal.tofile("/tmp/test.complex")
