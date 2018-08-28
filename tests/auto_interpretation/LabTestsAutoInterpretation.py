import os
import random
import tempfile
import unittest
from collections import defaultdict
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from tests.auto_interpretation.auto_interpretation_test_util import demodulate_from_aint_dict, bitvector_diff
from urh.ainterpretation import AutoInterpretation
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

    def generate_message_bits(self, num_bits=80, preamble="", sync="", eof=""):
        bits_to_generate = num_bits - (len(preamble) + len(sync) + len(eof))

        if bits_to_generate < 0:
            raise ValueError("Preamble and Sync and EOF are together larger than requested num bits")

        bytes_to_generate = bits_to_generate // 8
        leftover_bits = bits_to_generate % 8
        return "".join([preamble, sync]
                       + ["{0:08b}".format(random.choice(range(0, 256))) for _ in range(bytes_to_generate)]
                       + [random.choice(["0", "1"]) for _ in range(leftover_bits)]
                       + [eof]
                       )

    def generate_random_messages(self, target_file: str, num_messages: int, num_bits: int,
                                 preamble: str, sync: str, eof:str):
        with open(target_file, "w") as f:
            for _ in range(num_messages):
                f.write(self.generate_message_bits(num_bits, preamble, sync, eof) + "\n")

    def read_messages_from_file(self, filename: str, message_pause: int) -> List[Message]:
        result = []
        with open(filename, "r") as f:
            for line in f:
                result.append(Message.from_plain_bits_str(line.strip(), pause=message_pause))
        return result

    def test_against_noise(self):
        # file is only created once, delete it for fresh testdata
        target_file = os.path.join(tempfile.gettempdir(), "auto_int_against_noise_data.txt")

        # delete target file after changing these values!
        num_messages = 30
        num_bits = 80

        # no need to delete target file when changing these values
        messages_per_signal = 5
        snr_values = range(60, 0, -5)

        if not os.path.isfile(target_file):
            self.generate_random_messages(target_file,
                                          num_messages=num_messages,
                                          num_bits=num_bits,
                                          preamble="1010101010101010",
                                          sync="11011001",
                                          eof="1001")
            print("Bits written to {}".format(target_file))

        messages = self.read_messages_from_file(target_file, message_pause=10000)

        fsk_modulator = Modulator("FSK")
        fsk_modulator.modulation_type_str = "FSK"
        fsk_modulator.param_for_zero = -10e3
        fsk_modulator.param_for_one = 10e3

        ook_modulator = Modulator("OOK")
        ook_modulator.modulation_type_str = "ASK"
        ook_modulator.param_for_zero = 0
        ook_modulator.param_for_one = 100

        ask_modulator = Modulator("ASK")
        ask_modulator.modulation_type_str = "ASK"
        ask_modulator.param_for_zero = 50
        ask_modulator.param_for_one = 100

        psk_modulator = Modulator("PSK")
        psk_modulator.modulation_type_str = "PSK"
        psk_modulator.param_for_zero = 180
        psk_modulator.param_for_one = 0

        mean_errors = defaultdict(list)

        modulators_by_name = {"FSK": fsk_modulator, "OOK": ook_modulator, "ASK": ask_modulator, "PSK": psk_modulator}
        #modulators_by_name = {"PSK": psk_modulator}

        for modulator in modulators_by_name.values():
            modulator.samples_per_bit = 100
            modulator.sample_rate = 250e3
            modulator.carrier_freq_hz = 5e3

        for modulation_name, modulator in modulators_by_name.items():
            print("Running for {}".format(modulation_name))
            for snr in snr_values:
                print("  SNR={0:02d}dB".format(snr), end=" ")
                estimations = []
                errors = []
                for i in range(0, len(messages), messages_per_signal):
                    messages_in_signal = messages[i:i + messages_per_signal]
                    signal = self.generate_signal(messages_in_signal, modulator, snr_db=snr)

                    estimated_params = AutoInterpretation.estimate(signal)
                    estimations.append(estimated_params)

                    # Demodulate
                    demodulated = demodulate_from_aint_dict(signal, estimated_params, pause_threshold=16)
                    demodulated = demodulated if demodulated is not None else []
                    if len(demodulated) < messages_per_signal:
                        demodulated.extend([None] * (messages_per_signal - len(demodulated)))

                    # todo: bitvector diff currently does not align messages (necessary?)
                    error = sum([bitvector_diff(x.plain_bits_str, y) for x, y in zip(messages_in_signal, demodulated)])
                    errors.append(error)

                mean_error = np.mean(errors)
                mean_errors[modulation_name].append(mean_error)
                print("(Error: {})".format(mean_error))

        num_signals = len(messages) // messages_per_signal

        for modulation_name in modulators_by_name:
            plt.plot(snr_values, mean_errors[modulation_name], label=modulation_name)
        plt.ylabel("Error (number differing bits)")
        plt.xlabel("SNR (dB)")
        title_str = "Accuracy for {} signals with {} messages per signal and {} bits per message"
        plt.title(title_str.format(num_signals, messages_per_signal, num_bits))
        plt.xlim(max(snr_values), min(snr_values))  # decreasing time
        plt.legend()

        plt.savefig("/tmp/plot.png")
        plt.show()
        # print(mean_errors)

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
