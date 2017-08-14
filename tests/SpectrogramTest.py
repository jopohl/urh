import unittest
import numpy as np
from tests.utils_testing import get_path_for_data_file
from urh.signalprocessing.Signal import Signal

from matplotlib import pyplot as plt
from urh.cythonext import signalFunctions

class SpectrogramTest(unittest.TestCase):
    """ short time fourier transform of audio signal """

    def stft(self, samples, window_size, overlap_factor=0.5, window_function=np.hanning):
        """
        Perform Short-time Fourier transform to get the spectrogram for the given samples

        :param samples: Complex samples
        :param window_size: Size of DFT window
        :param overlap_factor: Value between 0 (= No Overlapping) and 1 (= Full overlapping) of windows
        :param window_function: Function for DFT window
        :return: short-time Fourier transform of the given signal
        """
        window = window_function(window_size)

        # hop size determines by how many samples the window is advanced
        hop_size = window_size - int(overlap_factor * window_size)

        # pad with zeros to ensure last window fits signal
        padded_samples = np.append(samples, np.zeros((len(samples) - window_size) % hop_size))
        num_frames = ((len(padded_samples) - window_size) // hop_size) + 1
        frames = [padded_samples[i*hop_size:i*hop_size+window_size] * window for i in range(num_frames)]
        return np.fft.fft(frames)

    def setUp(self):
        self.signal = Signal(get_path_for_data_file("two_participants.complex"), "test")

    def test_numpy_impl(self):
        sample_rate = 1e6
        spectrogram = np.fft.fftshift(self.stft(self.signal.data, 2**10, overlap_factor=0.5))

        ims = 20 * np.log10(np.abs(spectrogram) / 10e-6)  # convert amplitudes to decibel
        num_time_bins, num_freq_bins = np.shape(ims)

        plt.imshow(np.transpose(ims), aspect="auto", cmap="magma")
        plt.colorbar()

        plt.xlabel("time in seconds")
        plt.ylabel("frequency in Hz")
        plt.ylim(ymin=0, ymax=num_freq_bins)

        x_tick_pos = np.linspace(0, num_time_bins - 1, 5, dtype=np.float32)
        plt.xticks(x_tick_pos, ["%.02f" % l for l in (x_tick_pos * len(self.signal.data) / num_time_bins) / sample_rate])
        y_tick_pos = np.linspace(0, num_freq_bins - 1, 10, dtype=np.int16)
        frequencies = np.fft.fftshift(np.fft.fftfreq(num_freq_bins, 1/sample_rate))
        plt.yticks(y_tick_pos, ["%.02f" % frequencies[i] for i in y_tick_pos])

        plt.show()

    def design_windowed_sinc_lpf(self, fc, bw):
        N = int(np.ceil((4 / bw)))
        if not N % 2: N += 1  # Make sure that N is odd.
        n = np.arange(N)

        # Compute sinc filter.
        h = np.sinc(2 * fc * (n - (N - 1) / 2.))

        # Compute Blackman window.
        w = np.blackman(N)

        # Multiply sinc filter with window.
        h = h * w

        # Normalize to get unity gain.
        h_unity = h / np.sum(h)

        return h_unity

    def design_windowed_sinc_bandpass(self, f_low, f_high, bw):
        lp1 = self.design_windowed_sinc_lpf(f_low, bw)
        lp2 = self.design_windowed_sinc_lpf(f_high, bw)

        lp2_spectral_inverse = np.negative(lp2)
        lp2_spectral_inverse[len(lp2_spectral_inverse) // 2] += 1

        band_reject_kernel = lp1 + lp2_spectral_inverse
        band_pass_kernel = np.negative(band_reject_kernel)
        band_pass_kernel[len(band_pass_kernel) // 2] += 1

        return band_pass_kernel

    def fftconvolve_1d(self, in1, in2):
        import math
        outlen = in1.shape[-1] + in2.shape[-1] - 1
        n = int(2**(math.ceil(math.log2(outlen))))

        tr1 = np.fft.fft(in1, n)
        tr2 = np.fft.fft(in2, n)
        out = np.fft.ifft(tr1 * tr2, n)

        return out[..., :outlen].copy()

    def narrowband_iir(self, fc, bw, fs):
        fc /= fs
        bw /= fs

        R = 1 - 3 * bw
        K = (1 - 2 * R * np.cos(2 * np.pi * fc) + R ** 2) / (2 - 2*np.cos(2 * np.pi * fc))

        a = np.array([K, -2*K*np.cos(2 * np.pi * fc), K], dtype=np.float64)
        b = np.array([2 * R * np.cos(2 * np.pi * fc), -R**2], dtype=np.float64)

        return a, b

    def test_bandpass(self):
        # Generate a noisy signal
        fs = 1e6
        T = 0.1
        nsamples = T * fs
        t = np.linspace(0, T, nsamples, endpoint=False)
        a = 0.02
        f0 = 600
        x = 0.25 * np.sin(2 * np.pi * 0.25*f0 * t)
        x += 0.25 * np.sin(2 * np.pi * f0 * t)
        x += 0.25 * np.sin(2 * np.pi * 2*f0 * t)
        x += 0.25 * np.sin(2 * np.pi * 3*f0 * t)

        import time

        lowcut = 0
        highcut = 1e6

        # Define the parameters
        fc = f0 / fs
        b = 0.01

        # Normalize to get unity gain.
        t = time.time()
        h_unity = self.design_windowed_sinc_bandpass(lowcut / fs, highcut / fs, b)
        print("Design time", time.time() - t)

        data = np.concatenate([self.signal.data, self.signal.data, self.signal.data, self.signal.data])

        data = np.ones(10*10**6, dtype=np.complex64)

        print("Len data", len(data))

        t = time.time()
        y = np.convolve(data, h_unity, 'same')
        print("Concolve time", time.time() - t)

        t = time.time()
        a = self.fftconvolve_1d(data, h_unity)
        print("FFT convolve time", time.time() - t)



        plt.plot(y, label='Filtered signal (%g Hz)' % f0)
        plt.plot(a, label='Filtered signal (%g Hz) with fft' % f0)
        plt.plot(data, label='Noisy signal')
        plt.legend(loc='upper left')
        plt.show()

    def test_iir_bandpass(self):
        # Generate a noisy signal
        fs = 2400
        T = 6
        nsamples = T * fs
        t = np.linspace(0, T, nsamples, endpoint=False)
        a = 0.02
        f0 = 300
        x = 0.5 * np.sin(2 * np.pi * f0 * t)
        x += 0.25 * np.sin(2 * np.pi * 2 * f0 * t)
        x += 0.25 * np.sin(2 * np.pi * 3 * f0 * t)

        #data = x.astype(np.complex64)
        data = np.sin(2 * np.pi * f0 * t).astype(np.complex64)

        print("Len data", len(data))
        a, b = self.narrowband_iir(f0, 100, fs)
        s = a.sum() + b.sum()
        #a /= s
        #b /= s
        print(a,  b)

        filtered_data = signalFunctions.iir_filter(a, b, data)

        #plt.plot(data, label='Noisy signal')
        plt.plot(np.fft.fft(filtered_data), label='Filtered signal (%g Hz)' % f0)



        plt.legend(loc='upper left')
        plt.show()
