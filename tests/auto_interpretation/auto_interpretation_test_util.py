import random

import numpy as np

from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


def demodulate(
    signal_data,
    mod_type: str,
    bit_length,
    center,
    noise,
    tolerance,
    decoding=None,
    pause_threshold=8,
):
    signal = Signal("", "")
    if isinstance(signal_data, IQArray):
        signal.iq_array = signal_data
    else:
        if signal_data.dtype == np.complex64:
            signal.iq_array = IQArray(signal_data.view(np.float32))
        else:
            signal.iq_array = IQArray(signal_data)
    signal.modulation_type = mod_type
    signal.samples_per_symbol = bit_length
    signal.center = center
    signal.noise_threshold = noise
    signal.pause_threshold = pause_threshold
    if tolerance is not None:
        signal.tolerance = tolerance
    pa = ProtocolAnalyzer(signal)
    if decoding is not None:
        pa.decoder = decoding
    pa.get_protocol_from_signal()
    return pa.decoded_hex_str


def generate_signal(messages: list, modulator: Modulator, snr_db: int, add_noise=True):
    result = []

    message_powers = []
    if isinstance(messages, Message):
        messages = [messages]

    for msg in messages:
        modulated = modulator.modulate(msg.encoded_bits, msg.pause)

        if add_noise:
            message_powers.append(
                np.mean(np.abs(modulated[: len(modulated) - msg.pause]))
            )

        result.append(modulated)

    result = np.concatenate(result)
    if not add_noise:
        return result

    noise = (
        np.random.normal(loc=0, scale=1, size=2 * len(result))
        .astype(np.float32)
        .view(np.complex64)
    )

    # https://stackoverflow.com/questions/23690766/proper-way-to-add-noise-to-signal
    snr_ratio = np.power(10, snr_db / 10)

    signal_power = np.mean(message_powers)
    noise_power = signal_power / snr_ratio
    noise = 1 / np.sqrt(2) * noise_power * noise

    return result + noise


def generate_message_bits(num_bits=80, preamble="", sync="", eof=""):
    bits_to_generate = num_bits - (len(preamble) + len(sync) + len(eof))

    if bits_to_generate < 0:
        raise ValueError(
            "Preamble and Sync and EOF are together larger than requested num bits"
        )

    bytes_to_generate = bits_to_generate // 8
    leftover_bits = bits_to_generate % 8
    return "".join(
        [preamble, sync]
        + [
            "{0:08b}".format(random.choice(range(0, 256)))
            for _ in range(bytes_to_generate)
        ]
        + [random.choice(["0", "1"]) for _ in range(leftover_bits)]
        + [eof]
    )


def generate_random_messages(
    num_messages: int,
    num_bits: int,
    preamble: str,
    sync: str,
    eof: str,
    message_pause: int,
):
    return [
        Message.from_plain_bits_str(
            generate_message_bits(num_bits, preamble, sync, eof), pause=message_pause
        )
        for _ in range(num_messages)
    ]
