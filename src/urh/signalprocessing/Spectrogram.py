import numpy as np
from PyQt5.QtGui import QImage

import colormap
from urh.util.Logger import logger

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
        # TODO: Check if we can use predifined values e.g. -160 and 0 here
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
    def time_bins(self) -> int:
        return np.shape(self.data)[0]

    @property
    def freq_bins(self) -> int:
        return np.shape(self.data)[1]

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

    def apply_bgra_lookup(self, data: np.ndarray, normalize=True) -> np.ndarray:
        cmap = colormap.colormap_numpy_bgra

        if normalize:
            normalized_values = (len(cmap) - 1) * ((data.T - self.data_min) / (self.data_max - self.data_min))
        else:
            normalized_values = data.T

        return np.take(cmap, normalized_values.astype(np.int64), axis=0, mode='clip')

    def create_image(self, data: np.ndarray, normalize=True) -> QImage:
        """
        Create QImage from ARGB array.
        The ARGB must have shape (width, height, 4) and dtype=ubyte.
        NOTE: The order of values in the 3rd axis must be (blue, green, red, alpha).
        :return:
        """
        image_data = self.apply_bgra_lookup(data, normalize)

        if not image_data.flags['C_CONTIGUOUS']:
            logger.debug("Array was not C_CONTIGUOUS. Converting it.")
            image_data = np.ascontiguousarray(image_data)

        try:
            # QImage constructor needs inverted row/column order
            image = QImage(image_data.ctypes.data, image_data.shape[1], image_data.shape[0], QImage.Format_ARGB32)
        except Exception as e:
            logger.error("could not create image " + str(e))
            return QImage()

        image.data = image_data
        return image

    def create_spectrogram_image(self):
        return self.create_image(self.data)

    def create_colormap_image(self, width=100) -> QImage:
        indices = np.zeros((width, len(colormap.colormap_numpy_bgra)), dtype=np.int64)
        for i in np.arange(indices.shape[1], dtype=np.int64):
            indices[:, i] = np.repeat(indices.shape[1]-i, width)
        return self.create_image(indices, normalize=False)
