import math

import numpy as np
from PyQt5.QtGui import QImage

from urh import colormaps
from urh.cythonext import util
from urh.signalprocessing.IQArray import IQArray
from urh.util.Logger import logger


class Spectrogram(object):
    MAX_LINES_PER_VIEW = 1000
    DEFAULT_FFT_WINDOW_SIZE = 1024

    def __init__(self, samples: np.ndarray, window_size=DEFAULT_FFT_WINDOW_SIZE,
                 overlap_factor=0.5, window_function=np.hanning):
        """

        :param samples: Complex samples
        :param window_size: Size of DFT window
        :param overlap_factor: Value between 0 (= No Overlapping) and 1 (= Full overlapping) of windows
        :param window_function: Function for DFT window
        """

        self.__samples = np.zeros(1, dtype=np.complex64)
        self.samples = samples

        self.__window_size = window_size
        self.__overlap_factor = overlap_factor
        self.__window_function = window_function

        self.data_min, self.data_max = -140, 10

    @property
    def samples(self):
        return self.__samples

    @samples.setter
    def samples(self, value):
        if isinstance(value, IQArray):
            value = value.as_complex64()
        elif isinstance(value, np.ndarray) and value.dtype != np.complex64:
            value = IQArray(value).as_complex64()
        elif value is None:
            value = np.zeros(1, dtype=np.complex64)

        self.__samples = value

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
    def time_bins(self):
        return int(math.ceil(len(self.samples) / self.hop_size))

    @property
    def freq_bins(self):
        return self.window_size

    @property
    def hop_size(self):
        """
        hop size determines by how many samples the window is advanced
        """
        return self.window_size - int(self.overlap_factor * self.window_size)

    def stft(self, samples: np.ndarray):
        """
        Perform Short-time Fourier transform to get the spectrogram for the given samples
        :return: short-time Fourier transform of the given signal
        """
        window = self.window_function(self.window_size)
        hop_size = self.hop_size

        if len(samples) < self.window_size:
            samples = np.append(samples, np.zeros(self.window_size - len(samples)))

        num_frames = max(1, (len(samples) - self.window_size) // hop_size + 1)

        # Get frames as numpy view with stride_tricks to save RAM
        # Same as: frames = [padded_samples[i*hop_size:i*hop_size+self.window_size] for i in range(num_frames)]
        shape = (num_frames, self.window_size)
        strides = (hop_size * samples.strides[-1], samples.strides[-1])
        frames = np.lib.stride_tricks.as_strided(samples, shape=shape, strides=strides)

        result = np.fft.fft(frames * window, self.window_size) / np.atleast_1d(self.window_size)
        return result

    def export_to_fta(self, sample_rate, filename: str, include_amplitude=False):
        """
        Export to Frequency, Time, Amplitude file.
        Frequency is double, Time (nanosecond) is uint32, Amplitude is float32

        :return:
        """
        spectrogram = self.__calculate_spectrogram(self.samples)
        spectrogram = np.flipud(spectrogram.T)
        if include_amplitude:
            result = np.empty((spectrogram.shape[0], spectrogram.shape[1], 3),
                              dtype=[('f', np.float64), ('t', np.uint32), ('a', np.float32)])
        else:
            result = np.empty((spectrogram.shape[0], spectrogram.shape[1], 2),
                              dtype=[('f', np.float64), ('t', np.uint32)])

        fft_freqs = np.fft.fftshift(np.fft.fftfreq(spectrogram.shape[0], 1/sample_rate))
        time_width = 1e9 * ((len(self.samples) / sample_rate) / spectrogram.shape[1])

        for i in range(spectrogram.shape[0]):
            for j in range(spectrogram.shape[1]):
                if include_amplitude:
                    result[i, j] = (fft_freqs[i], int(j*time_width), spectrogram[i, j])
                else:
                    result[i, j] = (fft_freqs[i], int(j * time_width))

        result.tofile(filename)

    def __calculate_spectrogram(self, samples: np.ndarray) -> np.ndarray:
        # Only shift axis 1 (frequency) and not time
        spectrogram = np.fft.fftshift(self.stft(samples), axes=(1,))
        spectrogram = util.arr2decibel(spectrogram.astype(np.complex64))

        # Flip Array so Y axis goes from negative to positive
        return np.fliplr(spectrogram)

    def create_spectrogram_image(self, sample_start: int=None, sample_end: int=None, step: int=None, transpose=False):
        spectrogram = self.__calculate_spectrogram(self.samples[sample_start:sample_end:step])
        if transpose:
            spectrogram = np.flipud(spectrogram.T)
        return self.create_image(spectrogram, colormaps.chosen_colormap_numpy_bgra, self.data_min, self.data_max)

    def create_image_segments(self):
        n_segments = max(1, self.time_bins // self.MAX_LINES_PER_VIEW)
        step = self.time_bins / n_segments
        step = max(1, int((step / self.hop_size) * self.hop_size ** 2))

        for i in range(0, len(self.samples), step):
            image = self.create_spectrogram_image(sample_start=i, sample_end=i+step)
            yield image

    @staticmethod
    def apply_bgra_lookup(data: np.ndarray, colormap, data_min=None, data_max=None, normalize=True) -> np.ndarray:
        if normalize and (data_min is None or data_max is None):
            raise ValueError("Can't normalize without data min and data max")

        if normalize:
            normalized_values = (len(colormap) - 1) * ((data.T - data_min) / (data_max - data_min))
        else:
            normalized_values = data.T

        return np.take(colormap, normalized_values.astype(np.int), axis=0, mode='clip')

    @staticmethod
    def create_image(data: np.ndarray, colormap, data_min=None, data_max=None, normalize=True) -> QImage:
        """
        Create QImage from ARGB array.
        The ARGB must have shape (width, height, 4) and dtype=ubyte.
        NOTE: The order of values in the 3rd axis must be (blue, green, red, alpha).
        :return:
        """
        image_data = Spectrogram.apply_bgra_lookup(data, colormap, data_min, data_max, normalize)

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

    @staticmethod
    def create_colormap_image(colormap_name: str, height=100) -> QImage:
        colormap = colormaps.calculate_numpy_brga_for(colormap_name)

        indices = np.zeros((len(colormap), height), dtype=np.int64)
        for i in np.arange(len(colormap), dtype=np.int64):
            indices[i, :] = np.repeat(i, height)

        return Spectrogram.create_image(indices, colormap, normalize=False)
