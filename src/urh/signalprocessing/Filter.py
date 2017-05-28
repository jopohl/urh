import numpy as np
from urh.cythonext import signalFunctions
from enum import Enum


class FilterType(Enum):
    moving_average = "moving average"
    custom = "custom"

class Filter(object):

    def __init__(self, taps: list, filter_type: FilterType = FilterType.custom):
        self.filter_type = filter_type
        self.taps = taps

    def apply_fir_filter(self, input_signal: np.ndarray) -> np.ndarray:
        if input_signal.dtype != np.complex64:
            input_signal = np.array(input_signal, dtype=np.complex64)

        return signalFunctions.fir_filter(input_signal, np.array(self.taps, dtype=np.complex64))
