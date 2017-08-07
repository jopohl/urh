import unittest
import numpy as np
from tests.utils_testing import get_path_for_data_file
from urh.signalprocessing.Signal import Signal

from matplotlib import pyplot as plt


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

        plt.imshow(np.transpose(ims), aspect="auto")
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
