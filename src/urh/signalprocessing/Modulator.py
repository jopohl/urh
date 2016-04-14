import locale

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsScene

from urh import constants
from urh.cythonext import path_creator
from urh.cythonext.signalFunctions import Symbol
from urh.ui.ZoomableScene import ZoomableScene

class Modulator(object):
    """
    This class can modulate bits to a carrier.
    Very useful in generation phase.
    """

    MODULATION_TYPES = ["ASK", "FSK", "PSK", "GFSK"]


    def __init__(self, name: str):
        self.carrier_freq_hz = 40 * 10 ** 3
        self.carrier_amplitude = 1
        self.carrier_phase_deg = 0
        self.data = [True, False, True, False]
        self.samples_per_bit = 100
        self.default_sample_rate = 10 ** 6
        self.__sample_rate = None
        self.modulation_type = 0
        self.name = name

        self.param_for_zero = 0  # Freq, Amplitude (0..100%) or Phase (0..360)
        self.param_for_one = 100  # Freq, Amplitude (0..100%) or Phase (0..360)

        self.modulated_samples = None

    def __eq__(self, other):
        return self.carrier_freq_hz == other.carrier_freq_hz and\
               self.carrier_amplitude ==  other.carrier_amplitude and\
               self.carrier_phase_deg == other.carrier_phase_deg and\
               self.name == other.name and\
               self.modulation_type == other.modulation_type and\
               self.samples_per_bit == other.samples_per_bit and\
               self.sample_rate == other.sample_rate and\
               self.param_for_one == other.param_for_one and\
               self.param_for_zero == other.param_for_zero

    @property
    def sample_rate(self):
        if self.__sample_rate is not None:
            return self.__sample_rate
        else:
            return self.default_sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        self.__sample_rate = value

    @property
    def display_bits(self) -> str:
        return "".join(["1" if bit else "0" for bit in self.data])

    @display_bits.setter
    def display_bits(self, value: str):
        self.data = [True if bit == "1" else False for bit in value]

    @property
    def carrier_frequency_str(self):
        return self.get_value_with_suffix(self.carrier_freq_hz) + "Hz"

    @property
    def carrier_phase_str(self):
        return str(self.carrier_phase_deg) + "°"

    @property
    def bit_len_str(self):
        return str(self.samples_per_bit)

    @property
    def sample_rate_str(self):
        return self.get_value_with_suffix(self.sample_rate)

    @property
    def modulation_type_str(self):
        return self.MODULATION_TYPES[self.modulation_type]

    @modulation_type_str.setter
    def modulation_type_str(self, val: str):
        val = val.upper()
        if val in self.MODULATION_TYPES:
            self.modulation_type = self.MODULATION_TYPES.index(val)

    @property
    def param_for_zero_str(self):
        mod = self.MODULATION_TYPES[self.modulation_type]
        if mod == "ASK":
            return str(self.param_for_zero) + "%"
        elif mod == "FSK" or mod == "GFSK":
            return self.get_value_with_suffix(self.param_for_zero) + "Hz"
        elif mod == "PSK":
            return str(self.param_for_zero) + "°"

    @property
    def param_for_one_str(self):
        mod = self.MODULATION_TYPES[self.modulation_type]
        if mod == "ASK":
            return str(self.param_for_one) + "%"
        elif mod == "FSK" or mod == "GFSK":
            return self.get_value_with_suffix(self.param_for_one) + "Hz"
        elif mod == "PSK":
            return str(self.param_for_one) + "°"

    @property
    def carrier_data(self):
        nsamples = len(self.display_bits) * self.samples_per_bit
        x = np.arange(0, nsamples)
        carrier_phase_rad = self.carrier_phase_deg * (np.pi / 180)
        t = (x / self.sample_rate)
        f = self.carrier_freq_hz
        y = self.carrier_amplitude * np.sin(2 * np.pi * f * t + carrier_phase_rad)

        return y.astype(np.float32)

    @property
    def data_scene(self) -> QGraphicsScene:
        ones = np.ones(self.samples_per_bit, dtype=np.float32) * 1
        zeros = np.ones(self.samples_per_bit, dtype=np.float32) * -1
        n = self.samples_per_bit * len(self.display_bits)
        y = []
        for bit in self.display_bits:
            if bit == "0":
                y.extend(zeros)
            elif bit == "1":
                y.extend(ones)
        x = np.arange(0, n).astype(np.int64)
        scene = ZoomableScene()
        scene.setSceneRect(0, -1, n, 2)
        scene.setBackgroundBrush(constants.BGCOLOR)
        scene.addLine(0, 0, n, 0, QPen(constants.AXISCOLOR, Qt.FlatCap))
        y = np.array(y) if len(y) > 0 else np.array(y).astype(np.float32)
        path = path_creator.array_to_QPath(x, y)
        scene.addPath(path, QPen(constants.LINECOLOR, Qt.FlatCap))
        return scene

    def modulate(self, data = None, pause = 0, start = 0):
        assert pause >= 0
        if data is None:
            data = self.data
        else:
            self.data = data

        mod_type = self.MODULATION_TYPES[self.modulation_type]
        total_samples = sum(bit.nsamples if type(bit) == Symbol else self.samples_per_bit for bit in data) + pause

        self.modulated_samples = np.zeros(total_samples, dtype=np.complex64)

        # Lets build a paramvector
        paramvector = np.empty(total_samples - pause, dtype=np.float64)
        sample_pos = 0

        for i, bit in enumerate(data):
            if type(bit) == Symbol:
                samples_per_bit = bit.nsamples
                log_bit = True if bit.pulsetype == 1 else False
            else:
                log_bit = bit
                samples_per_bit = self.samples_per_bit

            param = self.param_for_one if log_bit else self.param_for_zero
            paramvector[sample_pos:sample_pos + samples_per_bit] = np.full(samples_per_bit, param, dtype=np.float64)
            sample_pos += samples_per_bit

        t = np.arange(start, start + total_samples - pause) / self.sample_rate
        a = paramvector / 100 if mod_type == "ASK" else self.carrier_amplitude
        phi = paramvector * (np.pi / 180) if mod_type == "PSK" else self.carrier_phase_deg * (np.pi / 180)

        if mod_type == "FSK":
            f = paramvector
        elif mod_type == "GFSK":
            #f = np.convolve(paramvector, self.gauss(len(paramvector)-1, sigma=2), mode="same")
            f = self.running_mean(paramvector, 4)
        else:
            f = self.carrier_freq_hz

        self.modulated_samples.imag[:total_samples - pause] = a * np.sin(2 * np.pi * f * t + phi)
        self.modulated_samples.real[:total_samples - pause] = a * np.cos(2 * np.pi * f * t + phi)


    def running_mean(self, x, N, times=2):
        result = x
        for _ in range(times):
            result = np.insert(result, 0, [result[0]] * (N-1))
            cumsum = np.cumsum(np.insert(result, 0, 0))
            result = (cumsum[N:] - cumsum[:-N]) / N
        return result

    def gauss(self, n=11, sigma=1.0):
        r = range(-int(n / 2), int(n / 2) + 1)
        result =  np.array([1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-float(x) ** 2 / (2 * sigma ** 2)) for x in r])
        return result / result.sum()

    @staticmethod
    def get_value_with_suffix(value):
        if abs(value) >= 10 ** 9:
            return locale.format_string("%.4fG", value / 10 ** 9)
        elif abs(value) >= 10 ** 6:
            return locale.format_string("%.4fM", value / 10 ** 6)
        elif abs(value) >= 10 ** 3:
            return locale.format_string("%.4fk",value / 10 ** 3)
        else:
            return locale.format_string("%f", value)
