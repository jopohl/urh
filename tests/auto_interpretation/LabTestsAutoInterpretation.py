import os
import random
import tempfile
import unittest
from typing import List

import numpy as np

from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator


class LabTestsAutoInterpretation(unittest.TestCase):
    def rms(self, data):
        return np.sqrt(np.mean(np.square(data)))

    def generate_signal(self, messages: List[Message], modulator: Modulator, snr_db):
        result = []
        for msg in messages:
            result.append(modulator.modulate(msg.encoded_bits, msg.pause))

        result = np.concatenate(result)
        noise = np.random.normal(loc=0, scale=1, size=2 * len(result)).astype(np.float32)

        ratio = 10 ** (snr_db / 10)
        # rms of data signal is carrier amplitude
        rms_data = modulator.carrier_amplitude
        if modulator.modulation_type_str == "ASK":
            rms_data *= max(modulator.param_for_zero, modulator.param_for_one) / 100
        target_noise_rms = rms_data / np.sqrt(ratio)
        noise = target_noise_rms * (noise / self.rms(noise))

        # print("SNR", 10 * np.log10((rms_data / self.rms(noise))**2))

        return result + noise.view(np.complex64)

    def generate_message_bits(self, num_bits=80, preamble="", sync=""):
        bits_to_generate = num_bits - (len(preamble) + len(sync))

        if bits_to_generate < 0:
            raise ValueError("Preamble and Sync are together larger than requested num bits")

        bytes_to_generate = bits_to_generate // 8
        leftover_bits = bits_to_generate % 8
        return "".join([preamble, sync]
                       + ["{0:08b}".format(random.choice(range(0, 256))) for _ in range(bytes_to_generate)]
                       + [random.choice(["0", "1"]) for _ in range(leftover_bits)]
                       )

    def generate_random_messages(self, target_file: str, num_messages: int, num_bits: int, preamble: str, sync: str):
        with open(target_file, "w") as f:
            for _ in range(num_messages):
                f.write(self.generate_message_bits(num_bits, preamble, sync) + "\n")


    def test_against_noise(self):
        target_file = os.path.join(tempfile.gettempdir(), "auto_int_against_noise_data.txt")

        if not os.path.isfile(target_file):
            self.generate_random_messages(target_file, num_messages=1000, num_bits=80,
                                          preamble="10101010", sync="11110000")


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
