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
    def fft_convolve_1d(cls, x: np.ndarray, h: np.ndarray):
        n = len(x) + len(h) - 1
        n_opt = 1 << (n-1).bit_length()  # Get next power of 2
        if np.issubdtype(x.dtype, np.complexfloating) or np.issubdtype(h.dtype, np.complexfloating):
            fft, ifft = np.fft.fft, np.fft.ifft    # use complex fft
        else:
            fft, ifft = np.fft.rfft, np.fft.irfft  # use real fft

        result = ifft(fft(x, n_opt) * fft(h, n_opt), n_opt)[0:n]
        too_much = (len(result) - len(x)) // 2  # Center result
        return result[too_much: -too_much]

    @classmethod
    def apply_bandpass_filter(cls, data, f_low, f_high, sample_rate: float=None, filter_bw=0.01):
        if sample_rate is not None:
            f_low /= sample_rate
            f_high /= sample_rate

        assert 0 <= f_low <= 0.5
        assert 0 <= f_high <= 0.5
        assert f_low <= f_high

        h = cls.design_windowed_sinc_bandpass(f_low, f_high, filter_bw)
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
