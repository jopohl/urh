import unittest
import numpy as np
from tests.utils_testing import get_path_for_data_file
from urh.signalprocessing.Filter import Filter
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Signal import Signal
import array

from matplotlib import pyplot as plt
from urh.cythonext import signalFunctions
from urh.signalprocessing.Spectrogram import Spectrogram


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
        spectrogram = np.fft.fftshift(self.stft(self.signal.data, 2**10, overlap_factor=0.5)) / 1024

        ims = 10 * np.log10(spectrogram.real ** 2 + spectrogram.imag ** 2)  # convert amplitudes to decibel
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
        fs = 2000
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

        lowcut = f0 - 200
        highcut = f0 + 200

        # Define the parameters
        fc = f0 / fs
        b = 0.05
        data = x

        y = Filter.apply_bandpass_filter(data, lowcut / fs, highcut / fs, filter_bw=b)

        plt.plot(y, label='Filtered signal (%g Hz)' % f0)
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

    def test_channels(self):
        sample_rate = 10 ** 6

        channel1_freq = 40 * 10 ** 3
        channel2_freq = 240 * 10 ** 3

        channel1_data = array.array("B", [1, 0, 1, 0, 1, 0, 0, 1])
        channel2_data = array.array("B", [1, 1, 0, 0, 1, 1, 0, 1])
        channel3_data = array.array("B", [1, 0, 0, 1, 0, 1, 1, 1])

        filter_bw = 0.1

        filter_freq1_high = 1.5 * channel1_freq
        filter_freq1_low = 0.5 * channel1_freq
        filter_freq2_high = 1.5*channel2_freq
        filter_freq2_low = 0.5 * channel2_freq

        modulator1, modulator2, modulator3 = Modulator("test"), Modulator("test2"), Modulator("test3")
        modulator1.carrier_freq_hz = channel1_freq
        modulator2.carrier_freq_hz = channel2_freq
        modulator3.carrier_freq_hz = -channel2_freq
        modulator1.sample_rate = modulator2.sample_rate = modulator3.sample_rate = sample_rate
        data1 = modulator1.modulate(channel1_data)
        data2 = modulator2.modulate(channel2_data)
        data3 = modulator3.modulate(channel3_data)

        mixed_signal = data1 + data2 + data3

        mixed_signal.tofile("/tmp/three_channels.complex")

        plt.subplot("221")
        plt.title("Signal")
        plt.plot(mixed_signal)

        spectrogram = Spectrogram(mixed_signal)
        plt.subplot("222")
        plt.title("Spectrogram")
        plt.imshow(np.transpose(spectrogram.data), aspect="auto", cmap="magma")
        plt.ylim(0, spectrogram.freq_bins)

        chann1_filtered = Filter.apply_bandpass_filter(mixed_signal, filter_freq1_low / sample_rate, filter_freq1_high / sample_rate, filter_bw)
        plt.subplot("223")
        plt.title("Channel 1 Filtered ({})".format("".join(map(str, channel1_data))))
        plt.plot(chann1_filtered)

        chann2_filtered = Filter.apply_bandpass_filter(mixed_signal, filter_freq2_low / sample_rate, filter_freq2_high / sample_rate, filter_bw)
        plt.subplot("224")
        plt.title("Channel 2 Filtered ({})".format("".join(map(str, channel2_data))))
        plt.plot(chann2_filtered)

        plt.show()


    def test_bandpass_h(self):
        f_low = -0.4
        f_high = -0.3
        bw = 0.01

        f_shift = (f_low + f_high) / 2
        f_c = (f_high - f_low) / 2

        N = Filter.get_filter_length_from_bandwidth(bw)

        h = Filter.design_windowed_sinc_lpf(f_c, bw=bw) * np.exp(np.complex(0,1) * np.pi * 2 * f_shift * np.arange(0, N, dtype=complex))

        #h = Filter.design_windowed_sinc_bandpass(f_low=f_low, f_high=f_high, bw=bw)
        #h = Filter.design_windowed_sinc_lpf(0.42, bw=0.08)

        impulse = np.exp(1j * np.linspace(0, 1, 50))

        plt.subplot("221")
        plt.title("f_low={} f_high={} bw={}".format(f_low, f_high, bw))
        plt.plot(np.fft.fftfreq(1024), np.fft.fft(h, 1024))

        plt.subplot("222")
        plt.plot(h)

        plt.show()



        # h = cls.design_windowed_sinc_bandpass(f_low, f_high, filter_bw)
