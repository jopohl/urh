import numpy as np

import colormaps

class Spectrogram(object):
    def __init__(self, samples: np.ndarray, sample_rate: float, window_size=1024, overlap_factor=0.5, window_function=np.hanning):
        """

        :param samples: Complex samples
        :param window_size: Size of DFT window
        :param overlap_factor: Value between 0 (= No Overlapping) and 1 (= Full overlapping) of windows
        :param window_function: Function for DFT window
        """
        self.__samples = samples
        self.__sample_rate = sample_rate
        self.__window_size = window_size
        self.__overlap_factor = overlap_factor
        self.__window_function = window_function
        self.data = self.__calculate_spectrogram()
        self.data_min, self.data_max = np.min(self.data), np.max(self.data)

    @property
    def samples(self):
        return self.__samples

    @samples.setter
    def samples(self, value):
        self.__samples = value

    @property
    def sample_rate(self):
        return self.__sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        self.__sample_rate = value

    @property
    def window_size(self):
        return self.__window_size

    @window_size.setter
    def window_size(self, value):
        self.__window_size = value

    @property
    def overlap_factor(self):
        return self.__overlap_factor

    @overlap_factor.setter
    def overlap_factor(self, value):
        self.__overlap_factor = value

    @property
    def window_function(self):
        return self.__window_function

    @window_function.setter
    def window_function(self, value):
        self.__window_function = value

    @property
    def dimension(self) -> tuple:
        time_bins, freq_bins = np.shape(self.data)
        return time_bins, freq_bins

    def stft(self):
        """
        Perform Short-time Fourier transform to get the spectrogram for the given samples
        :return: short-time Fourier transform of the given signal
        """
        window = self.window_function(self.window_size)

        # hop size determines by how many samples the window is advanced
        hop_size = self.window_size - int(self.overlap_factor * self.window_size)

        # pad with zeros to ensure last window fits signal
        padded_samples = np.append(self.samples, np.zeros((len(self.samples) - self.window_size) % hop_size))
        num_frames = ((len(padded_samples) - self.window_size) // hop_size) + 1
        frames = [padded_samples[i*hop_size:i*hop_size+self.window_size] * window for i in range(num_frames)]
        return np.fft.fft(frames)

    def __calculate_spectrogram(self) -> np.ndarray:
        spectrogram = np.fft.fftshift(self.stft())
        spectrogram = 20 * np.log10(np.abs(spectrogram))  # convert magnitudes to decibel
        return spectrogram

    def get_color_for_value(self, value: float):
        colormap = colormaps.DEFAULT
        num_colors = len(colormap)
        normalized_value = (value - self.data_min) / (self.data_max - self.data_min)
        return colormap[int(normalized_value * (num_colors-1))]
