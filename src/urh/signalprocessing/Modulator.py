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

            if mod_type == "FSK" or mod_type == "GFSK":
                param = 1 if log_bit else -1
            else:
                param = self.param_for_one if log_bit else self.param_for_zero
            paramvector[sample_pos:sample_pos + samples_per_bit] = np.full(samples_per_bit, param, dtype=np.float64)
            sample_pos += samples_per_bit

        t = np.arange(start, start + total_samples - pause) / self.sample_rate
        a = paramvector / 100 if mod_type == "ASK" else self.carrier_amplitude
        phi = paramvector * (np.pi / 180) if mod_type == "PSK" else self.carrier_phase_deg * (np.pi / 180)

        if mod_type == "FSK" or mod_type == "GFSK":
            fmid = (self.param_for_one + self.param_for_zero)/2
            dist = abs(fmid - self.param_for_one)
            if mod_type == "GFSK":
                paramvector =  np.convolve(paramvector, self.gauss_fir(), mode="same")

            f = fmid + dist * paramvector

            phi = np.zeros(len(f))
            for i in range(0, len(phi) - 1):
                phi[i+1] = 2 * np.pi * t[i] * (f[i]-f[i+1]) + phi[i] # Correct the phase to prevent spiky jumps
        else:
            f = self.carrier_freq_hz

        self.modulated_samples.imag[:total_samples - pause] = a * np.sin(2 * np.pi * f * t + phi)
        self.modulated_samples.real[:total_samples - pause] = a * np.cos(2 * np.pi * f * t + phi)


    def gauss_fir(self, bt=0.5, filter_width=1):
        """

        :param bt: normalized 3-dB bandwidth-symbol time product
        :param span: Filter span in symbols
        :return:
        """
        # http://onlinelibrary.wiley.com/doi/10.1002/9780470041956.app2/pdf
        k = range(-int(filter_width * self.samples_per_bit), int(filter_width * self.samples_per_bit)+1)
        ts = self.samples_per_bit / self.sample_rate # symbol time
        a = np.sqrt(np.log(2)/2)*(ts/bt)
        B = a / np.sqrt(np.log(2)/2) # filter bandwidth
        h = np.sqrt((2*np.pi)/(np.log(2))) * bt/ts * np.exp(-(((np.sqrt(2)*np.pi)/np.sqrt(np.log(2))*bt*k/self.samples_per_bit)**2))
        return h / h.sum()


    def gauss_matlab(self, bt=0.5):
        # https://github.com/rikrd/matlab/blob/master/signal/signal/gaussfir.m
        symbol_range = 1
        filtLen = 2 * self.samples_per_bit * symbol_range + 1
        t = np.linspace(-symbol_range, symbol_range, filtLen)
        alpha = np.sqrt(np.log(2) / 2) / (bt)
        h = (np.sqrt(np.pi) / alpha) * np.exp(-(t * np.pi / alpha) ** 2)
        return h/h.sum()


    def gauss(self, n=11, sigma=1.0):
        r = range(-int(n / 2), int(n / 2) + 1)
        result =  np.array([1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-float(x) ** 2 / (2 * sigma ** 2)) for x in r])
        return result / result.sum()


    def gauss2(self, sigma=1.0, truncate=4.0):
        sd = float(sigma)
        # make the radius of the filter equal to truncate standard deviations
        lw = int(truncate * sd + 0.5)
        weights = [0.0] * (2 * lw + 1)
        weights[lw] = 1.0
        sum = 1.0
        sd = sd * sd
        # calculate the kernel:
        for ii in range(1, lw + 1):
            tmp = np.exp(-0.5 * float(ii * ii) / sd)
            weights[lw + ii] = tmp
            weights[lw - ii] = tmp
            sum += 2.0 * tmp
        for ii in range(2 * lw + 1):
            weights[ii] /= sum

        return weights

    def gauss3(self, n=22, bt=0.5):
        a = (1/bt) * np.sqrt(np.log10(2)/2)
        r = range(-int(n / 2), int(n / 2) + 1)
        result =  np.array([np.sqrt(np.pi)/a * np.exp(-(np.pi ** 2 * x ** 2)/(a**2)) for x in r])
        return result / result.sum()

    def gunradio_gauss(self):
        bit_len = 100
        gaussian_taps = self.firdes_gaussian(bit_len, 0.5, int(0.5*bit_len))
        sqwave = (1,) * bit_len
        taps = np.convolve(np.array(gaussian_taps),np.array(sqwave))
        return taps

    def firdes_gaussian(self, samples_per_symbol, bt, ntaps):
        taps = np.empty(ntaps, dtype=np.float32)
        dt = 1/samples_per_symbol
        s = 1.0/(np.sqrt(np.log(2.0)) / (2*np.pi*bt))
        t0 = -0.5 * ntaps
        for i in range(ntaps):
            t0 += 1
            ts = s*dt*t0
            taps[i] = np.exp(-0.5*ts*ts)

        taps /= taps.sum()
        return taps



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
