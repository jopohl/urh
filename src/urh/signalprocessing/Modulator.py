import array
import locale
import math
import xml.etree.ElementTree as ET

import numpy as np
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsScene

from urh import settings
from urh.cythonext import path_creator, signal_functions
from urh.signalprocessing.IQArray import IQArray
from urh.ui.painting.ZoomableScene import ZoomableScene
from urh.util.Formatter import Formatter


class Modulator(object):
    FORCE_DTYPE = None

    MODULATION_TYPES = ["ASK", "FSK", "PSK", "GFSK", "OQPSK"]
    MODULATION_TYPES_VERBOSE = {
        "ASK": "Amplitude Shift Keying (ASK)",
        "FSK": "Frequency Shift Keying (FSK)",
        "PSK": "Phase Shift Keying (PSK)",
        "OQPSK": "Offset Quadrature Phase Shift Keying (OQPSK)",
        "GFSK": "Gaussian Frequeny Shift Keying (GFSK)",
    }

    def __init__(self, name: str):
        self.carrier_freq_hz = 40 * 10**3
        self.carrier_amplitude = 1
        self.carrier_phase_deg = 0
        self.data = [True, False, True, False]
        self.samples_per_symbol = 100
        self.default_sample_rate = 10**6
        self.__sample_rate = None
        self.__modulation_type = "ASK"

        self.__bits_per_symbol = 1

        self.name = name

        self.gauss_bt = 0.5  # bt product for gaussian filter (GFSK)
        self.gauss_filter_width = 1  # filter width for gaussian filter (GFSK)

        self.parameters = array.array(
            "f", [0, 100]
        )  # Freq, Amplitude (0..100%) or Phase (0..360)

    def __eq__(self, other):
        return (
            self.carrier_freq_hz == other.carrier_freq_hz
            and self.carrier_amplitude == other.carrier_amplitude
            and self.carrier_phase_deg == other.carrier_phase_deg
            and self.name == other.name
            and self.modulation_type == other.modulation_type
            and self.samples_per_symbol == other.samples_per_symbol
            and self.bits_per_symbol == other.bits_per_symbol
            and self.sample_rate == other.sample_rate
            and self.parameters == other.parameters
        )

    @staticmethod
    def get_dtype():
        if Modulator.FORCE_DTYPE is not None:
            return Modulator.FORCE_DTYPE

        dtype_str = settings.read("modulation_dtype", "float32", str)
        if dtype_str == "int8":
            return np.int8
        elif dtype_str == "int16":
            return np.int16
        else:
            return np.float32

    @property
    def modulation_type(self) -> str:
        return self.__modulation_type

    @modulation_type.setter
    def modulation_type(self, value):
        try:
            # legacy support when modulation type was saved as int index
            self.__modulation_type = self.MODULATION_TYPES[int(value)]
        except (ValueError, IndexError):
            self.__modulation_type = value

    @property
    def is_binary_modulation(self):
        return self.bits_per_symbol == 1

    @property
    def is_amplitude_based(self):
        return "ASK" in self.modulation_type

    @property
    def is_frequency_based(self):
        return "FSK" in self.modulation_type

    @property
    def is_phase_based(self):
        return "PSK" in self.modulation_type

    @property
    def bits_per_symbol(self):
        return self.__bits_per_symbol

    @bits_per_symbol.setter
    def bits_per_symbol(self, value):
        value = int(value)
        if value != self.bits_per_symbol:
            self.__bits_per_symbol = value
            self.parameters = array.array("f", [0] * self.modulation_order)

    @property
    def modulation_order(self):
        return 2**self.bits_per_symbol

    @property
    def parameter_type_str(self) -> str:
        if self.is_amplitude_based:
            return "Amplitudes in %:"
        if self.is_frequency_based:
            return "Frequencies in Hz:"
        if self.is_phase_based:
            return "Phases in degree:"

        return "Unknown Modulation Type (This should not happen...)"

    @property
    def parameters_string(self) -> str:
        if self.is_amplitude_based:
            return "/".join(map(str, map(int, self.parameters)))
        elif self.is_frequency_based:
            return "/".join(map(Formatter.big_value_with_suffix, self.parameters))
        elif self.is_phase_based:
            return "/".join(map(str, map(int, self.parameters)))
        else:
            raise ValueError("")

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
    def samples_per_symbol_str(self):
        return self.get_value_with_suffix(self.samples_per_symbol, unit="")

    @property
    def sample_rate_str(self):
        return self.get_value_with_suffix(self.sample_rate)

    @property
    def modulation_type_verbose(self):
        return self.MODULATION_TYPES_VERBOSE[self.modulation_type]

    @property
    def carrier_data(self):
        num_samples = len(self.display_bits) * self.samples_per_symbol
        carrier_phase_rad = self.carrier_phase_deg * (np.pi / 180)
        t = (np.arange(0, num_samples) / self.sample_rate).astype(np.float32)
        arg = (2 * np.pi * self.carrier_freq_hz * t + carrier_phase_rad).astype(
            np.float32
        )
        y = self.carrier_amplitude * np.sin(arg)  # type: np.ndarray

        return y.astype(np.float32)

    @property
    def data_scene(self) -> QGraphicsScene:
        n = self.samples_per_symbol * len(self.display_bits)
        y = np.ones(n, dtype=np.float32)

        for i, bit in enumerate(self.display_bits):
            if bit == "0":
                y[
                    i * self.samples_per_symbol : (i + 1) * self.samples_per_symbol
                ] = -1.0

        x = np.arange(0, n).astype(np.int64)

        scene = ZoomableScene()
        scene.setSceneRect(0, -1.25, n, 2.5)
        scene.setBackgroundBrush(settings.BGCOLOR)
        scene.addLine(0, 0, n, 0, QPen(settings.AXISCOLOR, 0))

        path = path_creator.array_to_QPath(x, y)
        scene.addPath(path, QPen(settings.LINECOLOR, 0))

        return scene

    def modulate(self, data=None, pause=0, start=0, dtype=None) -> IQArray:
        assert pause >= 0
        if data is None:
            data = self.data
        else:
            self.data = data

        if isinstance(data, str):
            data = array.array("B", map(int, data))
        elif isinstance(data, list):
            data = array.array("B", data)

        if len(data) == 0:
            return IQArray(None, np.float32, 0)

        dtype = dtype or self.get_dtype()
        a = self.carrier_amplitude * IQArray.min_max_for_dtype(dtype)[1]

        parameters = self.parameters
        if self.modulation_type == "ASK":
            parameters = array.array("f", [a * p / 100 for p in parameters])
        elif self.modulation_type == "PSK":
            parameters = array.array("f", [p * (math.pi / 180) for p in parameters])

        result = signal_functions.modulate_c(
            data,
            self.samples_per_symbol,
            self.modulation_type,
            parameters,
            self.bits_per_symbol,
            a,
            self.carrier_freq_hz,
            self.carrier_phase_deg * (np.pi / 180),
            self.sample_rate,
            pause,
            start,
            dtype,
            self.gauss_bt,
            self.gauss_filter_width,
        )
        return IQArray(result)

    def get_default_parameters(self) -> array.array:
        if self.is_amplitude_based:
            parameters = np.linspace(0, 100, self.modulation_order, dtype=np.float32)
        elif self.is_frequency_based:
            parameters = []
            for i in range(self.modulation_order):
                parameters.append(
                    (i + 1) * self.carrier_freq_hz / self.modulation_order
                )
        elif self.is_phase_based:
            step = 360 / self.modulation_order
            parameters = np.arange(step / 2, 360, step) - 180
            if self.modulation_type == "OQPSK":
                parameters = parameters[
                    (self.__get_gray_code_indices(self.modulation_order))
                ]
        else:
            return None

        return array.array("f", parameters)

    @staticmethod
    def __get_gray_code_indices(n: int):
        result = []
        for i in range(0, n):
            result.append(i ^ (i >> 1))
        return result

    def to_xml(self, index: int) -> ET.Element:
        root = ET.Element("modulator")

        for attr, val in vars(self).items():
            if attr not in (
                "data",
                "_Modulator__sample_rate",
                "_Modulator__modulation_type",
                "_Modulator__bits_per_symbol",
                "default_sample_rate",
                "parameters",
            ):
                root.set(attr, str(val))

        root.set("sample_rate", str(self.__sample_rate))
        root.set("modulation_type", self.__modulation_type)
        root.set("index", str(index))
        root.set("parameters", ",".join(map(str, self.parameters)))
        root.set("bits_per_symbol", str(self.bits_per_symbol))

        return root

    def estimate_carrier_frequency(self, signal, protocol) -> int or None:
        if len(protocol.messages) == 0:
            return None

        # Take the first message for detection
        start, num_samples = protocol.get_samplepos_of_bitseq(0, 0, 0, 999999, False)
        # Avoid too large arrays
        if num_samples > 1e6:
            num_samples = int(1e6)

        return signal.estimate_frequency(start, start + num_samples, self.sample_rate)

    @staticmethod
    def from_xml(tag: ET.Element):
        result = Modulator("")
        for attrib, value in sorted(tag.attrib.items()):
            if attrib == "index":
                continue
            elif attrib == "name" or attrib == "modulation_type":
                setattr(result, attrib, str(value))
            elif attrib == "samples_per_bit" or attrib == "samples_per_symbol":
                # samples_per_bit as legacy support for older project files
                result.samples_per_symbol = Formatter.str2val(value, int, 100)
            elif attrib == "sample_rate":
                result.sample_rate = (
                    Formatter.str2val(value, float, 1e6) if value != "None" else None
                )
            elif attrib == "param_for_zero":
                result.parameters[0] = Formatter.str2val(value, float, 0)  # legacy
            elif attrib == "param_for_one":
                result.parameters[1] = Formatter.str2val(value, float, 100)  # legacy
            elif attrib == "bits_per_symbol":
                result.bits_per_symbol = Formatter.str2val(value, int, 1)
            elif attrib == "parameters":
                try:
                    result.parameters = array.array("f", map(float, value.split(",")))
                except ValueError:
                    continue
            elif not attrib.startswith("_Modulator__"):
                setattr(result, attrib, Formatter.str2val(value, float, 1))
        return result

    @staticmethod
    def modulators_to_xml_tag(modulators: list) -> ET.Element:
        modulators_tag = ET.Element("modulators")
        for i, modulator in enumerate(modulators):
            modulators_tag.append(modulator.to_xml(i))
        return modulators_tag

    @staticmethod
    def modulators_from_xml_tag(xml_tag: ET.Element) -> list:
        if xml_tag is None:
            return []

        if xml_tag.tag != "modulators":
            xml_tag = xml_tag.find("modulators")

        if xml_tag is None:
            return []

        result = []
        for mod_tag in xml_tag.iter("modulator"):
            result.append(Modulator.from_xml(mod_tag))
        return result

    @staticmethod
    def get_value_with_suffix(value, unit=""):
        decimal_point = locale.localeconv()["decimal_point"]

        if abs(value) >= 10**9:
            target_val, suffix = value / 10**9, "G"
        elif abs(value) >= 10**6:
            target_val, suffix = value / 10**6, "M"
        elif abs(value) >= 10**3:
            target_val, suffix = value / 10**3, "k"
        else:
            target_val, suffix = value, ""

        return (
            locale.format_string("%.3f", target_val).rstrip("0").rstrip(decimal_point)
            + suffix
            + unit
        )
