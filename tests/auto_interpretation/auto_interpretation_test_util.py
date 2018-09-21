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
