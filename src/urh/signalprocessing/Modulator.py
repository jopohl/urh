import locale
import xml.etree.ElementTree as ET

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsScene

from urh import constants
from urh.cythonext import path_creator
from urh.ui.ZoomableScene import ZoomableScene
from urh.util.Formatter import Formatter


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

        self.gauss_bt = 0.5  # bt product for gaussian filter (GFSK)
        self.gauss_filter_width = 1  # filter width for gaussian filter (GFSK)

        self.param_for_zero = 0  # Freq, Amplitude (0..100%) or Phase (0..360)
        self.param_for_one = 100  # Freq, Amplitude (0..100%) or Phase (0..360)

        self.modulated_samples = None

    def __eq__(self, other):
        return self.carrier_freq_hz == other.carrier_freq_hz and \
               self.carrier_amplitude == other.carrier_amplitude and \
               self.carrier_phase_deg == other.carrier_phase_deg and \
               self.name == other.name and \
               self.modulation_type == other.modulation_type and \
               self.samples_per_bit == other.samples_per_bit and \
               self.sample_rate == other.sample_rate and \
               self.param_for_one == other.param_for_one and \
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
        return self.get_value_with_suffix(self.carrier_freq_hz, unit="Hz")

    @property
    def carrier_phase_str(self):
        return self.get_value_with_suffix(self.carrier_phase_deg, unit="°")

    @property
    def bit_len_str(self):
        return self.get_value_with_suffix(self.samples_per_bit, unit="")

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
        units = {"ASK": "%", "FSK": "Hz", "GFSK": "Hz", "PSK": "°"}
        return self.get_value_with_suffix(self.param_for_zero, units[mod])

    @property
    def param_for_one_str(self):
        mod = self.MODULATION_TYPES[self.modulation_type]
        units = {"ASK": "%", "FSK": "Hz", "GFSK": "Hz", "PSK": "°"}
        return self.get_value_with_suffix(self.param_for_one, units[mod])

    @property
    def carrier_data(self):
        num_samples = len(self.display_bits) * self.samples_per_bit
        carrier_phase_rad = self.carrier_phase_deg * (np.pi / 180)
        t = (np.arange(0, num_samples) / self.sample_rate).astype(np.float32)
        arg = (2 * np.pi * self.carrier_freq_hz * t + carrier_phase_rad).astype(np.float32)
        y = self.carrier_amplitude * np.sin(arg)  # type: np.ndarray

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

    def modulate(self, data=None, pause=0, start=0):
        assert pause >= 0
        if data is None:
            data = self.data
        else:
            self.data = data

        mod_type = self.MODULATION_TYPES[self.modulation_type]
        total_samples = int(len(data) * self.samples_per_bit + pause)

        self.modulated_samples = np.zeros(total_samples, dtype=np.complex64)

        # Lets build a param_vector
        param_vector = np.empty(total_samples - pause, dtype=np.float64)
        sample_pos = 0

        for i, bit in enumerate(data):
            log_bit = bit
            samples_per_bit = int(self.samples_per_bit)

            if mod_type == "FSK" or mod_type == "GFSK":
                param = 1 if log_bit else -1
            else:
                param = self.param_for_one if log_bit else self.param_for_zero
            param_vector[sample_pos:sample_pos + samples_per_bit] = np.full(samples_per_bit, param, dtype=np.float64)
            sample_pos += samples_per_bit

        t = np.arange(start, start + total_samples - pause) / self.sample_rate
        a = param_vector / 100 if mod_type == "ASK" else self.carrier_amplitude
        phi = param_vector * (np.pi / 180) if mod_type == "PSK" else self.carrier_phase_deg * (np.pi / 180)

        if mod_type == "FSK" or mod_type == "GFSK":
            fmid = (self.param_for_one + self.param_for_zero) / 2
            dist = abs(fmid - self.param_for_one)
            if mod_type == "GFSK":
                gfir = self.gauss_fir(bt=self.gauss_bt, filter_width=self.gauss_filter_width)
                if len(param_vector) >= len(gfir):
                    param_vector = np.convolve(param_vector, gfir, mode="same")
                else:
                    # Prevent dimension crash later, because gaussian finite impulse response is longer then param_vector
                    param_vector = np.convolve(gfir, param_vector, mode="same")[:len(param_vector)]

            f = fmid + dist * param_vector

            # sin(2*pi*f_1*t_1 + phi_1) = sin(2*pi*f_2*t_1 + phi_2) <=> phi_2 = 2*pi*t_1*(f_1 - f_2) + phi_1
            phi = np.empty(len(f))
            phi[0] = self.carrier_phase_deg
            for i in range(0, len(phi) - 1):
                phi[i + 1] = 2 * np.pi * t[i] * (f[i] - f[i + 1]) + phi[i]  # Correct the phase to prevent spiky jumps
        else:
            f = self.carrier_freq_hz

        arg = ((2 * np.pi * f * t + phi) * 1j).astype(np.complex64)
        self.modulated_samples[:total_samples - pause] = a * np.exp(arg)

    def gauss_fir(self, bt=0.5, filter_width=1):
        """

        :param filter_width: Filter width
        :param bt: normalized 3-dB bandwidth-symbol time product
        :return:
        """
        # http://onlinelibrary.wiley.com/doi/10.1002/9780470041956.app2/pdf
        k = np.arange(-int(filter_width * self.samples_per_bit), int(filter_width * self.samples_per_bit) + 1)
        ts = self.samples_per_bit / self.sample_rate  # symbol time
        # a = np.sqrt(np.log(2)/2)*(ts/bt)
        # B = a / np.sqrt(np.log(2)/2) # filter bandwidth
        h = np.sqrt((2 * np.pi) / (np.log(2))) * bt / ts * np.exp(
            -(((np.sqrt(2) * np.pi) / np.sqrt(np.log(2)) * bt * k / self.samples_per_bit) ** 2))
        return h / h.sum()

    def to_xml(self, index: int) -> ET.Element:
        root = ET.Element("modulator")

        for attr, val in vars(self).items():
            if attr not in ("modulated_samples", "data", "_Modulator__sample_rate", "default_sample_rate"):
                root.set(attr, str(val))

        root.set("sample_rate", str(self.__sample_rate))
        root.set("index", str(index))

        return root

    @staticmethod
    def from_xml(tag: ET.Element):
        result = Modulator("")
        for attrib, value in tag.attrib.items():
            if attrib == "index":
                continue
            elif attrib == "name":
                setattr(result, attrib, str(value))
            elif attrib == "modulation_type":
                setattr(result, attrib, Formatter.str2val(value, int, 0))
            elif attrib == "samples_per_bit":
                setattr(result, attrib, Formatter.str2val(value, int, 100))
            elif attrib == "sample_rate":
                result.sample_rate = Formatter.str2val(value, float, 1e6) if value != "None" else None
            else:
                setattr(result, attrib, Formatter.str2val(value, float, 1))
        return result

    @staticmethod
    def get_value_with_suffix(value, unit=""):
        decimal_point = locale.localeconv()["decimal_point"]

        if abs(value) >= 10 ** 9:
            target_val, suffix = value / 10 ** 9, "G"
        elif abs(value) >= 10 ** 6:
            target_val, suffix = value / 10 ** 6, "M"
        elif abs(value) >= 10 ** 3:
            target_val, suffix = value / 10 ** 3, "k"
        else:
            target_val, suffix = value, ""

        return locale.format_string("%.3f", target_val).rstrip("0").rstrip(decimal_point) + suffix + unit
