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

    @classmethod
    def apply_bandpass_filter(cls, data, f_low, f_high, sample_rate, filter_bw=0.05):
        h = cls.design_windowed_sinc_bandpass(f_low / sample_rate, f_high / sample_rate, filter_bw)
        return np.convolve(data, h, 'same')

    @classmethod
    def design_windowed_sinc_lpf(cls, fc, bw):
        N = int(np.ceil((4 / bw)))
        N += 1 if N % 2 == 0 else 0  # Ensure N is odd.

        # Compute sinc filter impulse response
        h = np.sinc(2 * fc * (np.arange(N) - (N - 1) / 2.))

        # We use blackman window function
        w = np.blackman(N)

        # Multiply sinc filter with window function
        h = h * w

        # Normalize to get unity gain
        h_unity = h / np.sum(h)

        return h_unity

    @classmethod
    def design_windowed_sinc_bandpass(cls, f_low, f_high, bw):
        lp1 = cls.design_windowed_sinc_lpf(f_low, bw)
        lp2 = cls.design_windowed_sinc_lpf(f_high, bw)

        lp2_spectral_inverse = np.negative(lp2)
        lp2_spectral_inverse[len(lp2_spectral_inverse) // 2] += 1

        band_reject_kernel = lp1 + lp2_spectral_inverse
        band_pass_kernel = np.negative(band_reject_kernel)
        band_pass_kernel[len(band_pass_kernel) // 2] += 1

        return band_pass_kernel
