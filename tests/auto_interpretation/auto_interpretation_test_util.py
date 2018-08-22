import numpy as np

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


def demodulate(signal_data, mod_type: str, bit_length, center, noise, tolerance, decoding=None, pause_threshold=8):
    signal = Signal("", "")
    signal._fulldata = signal_data
    signal.modulation_type = signal.MODULATION_TYPES.index(mod_type)
    signal.bit_len = bit_length
    signal.qad_center = center
    signal.noise_threshold = noise
    signal.pause_threshold = pause_threshold
    if tolerance is not None:
        signal.tolerance = tolerance
    pa = ProtocolAnalyzer(signal)
    if decoding is not None:
        pa.decoder = decoding
    pa.get_protocol_from_signal()
    return pa.decoded_hex_str


def demodulate_from_aint_dict(signal_data, aint_parameters: dict, pause_threshold=8):
    if aint_parameters is None:
        return None

    signal = Signal("", "")
    signal._fulldata = signal_data
    signal.modulation_type = signal.MODULATION_TYPES.index(aint_parameters["modulation_type"])
    signal.bit_len = aint_parameters["bit_length"]
    signal.qad_center = aint_parameters["center"]
    signal.noise_threshold = aint_parameters["noise"]
    signal.tolerance = aint_parameters["tolerance"]
    signal.pause_threshold = pause_threshold
    pa = ProtocolAnalyzer(signal)
    pa.get_protocol_from_signal()
    return pa.plain_bits_str


def bitvector_diff(x: str, y: str):
    if x is None and y is None:
        return 0

    if y is None or len(y) == 0:
        return len(x)

    x = np.fromiter(x, dtype=np.int8, count=len(x))
    y = np.fromiter(y, dtype=np.int8, count=len(y))

    length = len(x) if len(y) >= len(x) else len(y)

    diff_vector = np.ones(len(x), dtype=np.int8)
    diff_vector[:length] = x[:length]-y[:length]

    return np.count_nonzero(diff_vector)

