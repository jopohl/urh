import numpy as np
from urh.cythonext import signalFunctions


class Filter(object):
    def __init__(self, name: str, taps: list):
        self.name = name
        self.taps = taps

    def apply_fir_filter(self, input_signal: np.ndarray) -> np.ndarray:
        return signalFunctions.fir_filter(input_signal, np.array(self.taps, dtype=np.complex64))
