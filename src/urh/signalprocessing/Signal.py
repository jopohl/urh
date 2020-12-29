import math
import os
import tarfile
import wave

import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject, QDir, Qt
from PyQt5.QtWidgets import QApplication

import urh.cythonext.signal_functions as signal_functions
from urh.ainterpretation import AutoInterpretation
from urh.signalprocessing.Filter import Filter
from urh.signalprocessing.IQArray import IQArray
from urh.util import FileOperator
from urh.util.Logger import logger


class Signal(QObject):
    """
    Representation of a loaded signal (complex file).
    """

    MODULATION_TYPES = ["ASK", "FSK", "PSK", "QAM"]

    samples_per_symbol_changed = pyqtSignal(int)
    tolerance_changed = pyqtSignal(int)
    noise_threshold_changed = pyqtSignal()
    center_changed = pyqtSignal(float)
    center_spacing_changed = pyqtSignal(float)
    name_changed = pyqtSignal(str)
    sample_rate_changed = pyqtSignal(float)
    modulation_type_changed = pyqtSignal(str)
    bits_per_symbol_changed = pyqtSignal(int)

    saved_status_changed = pyqtSignal()
    protocol_needs_update = pyqtSignal()
    data_edited = pyqtSignal()  # On Crop/Mute/Delete etc.

    def __init__(self, filename: str, name="Signal", modulation: str = None, sample_rate: float = 1e6, parent=None):
        super().__init__(parent)
        self.__name = name
        self.__tolerance = 5
        self.__samples_per_symbol = 100
        self.__pause_threshold = 8
        self.__message_length_divisor = 1
        self.__costas_loop_bandwidth = 0.1
        self._qad = None
        self.__center = 0
        self._noise_threshold = 0
        self.__sample_rate = sample_rate
        self.noise_min_plot = 0
        self.noise_max_plot = 0
        self.block_protocol_update = False

        self.iq_array = IQArray(None, np.int8, 1)

        self.wav_mode = filename.endswith(".wav")
        self.__changed = False
        if modulation is None:
            modulation = "FSK"
        self.__modulation_type = modulation
        self.__bits_per_symbol = 1
        self.__center_spacing = 1  # required for higher order modulations

        self.__parameter_cache = {mod: {"center": None, "samples_per_symbol": None} for mod in self.MODULATION_TYPES}

        self.__already_demodulated = False

        if len(filename) > 0:
            if self.wav_mode:
                self.__load_wav_file(filename)
            elif filename.endswith(".coco"):
                self.__load_compressed_complex(filename)
            else:
                self.__load_complex_file(filename)

            self.filename = filename
            self.noise_threshold = AutoInterpretation.detect_noise_level(self.iq_array.magnitudes)
        else:
            self.filename = ""

    def __load_complex_file(self, filename: str):
        self.iq_array = IQArray.from_file(filename)

    def __load_wav_file(self, filename: str):
        wav = wave.open(filename, "r")
        num_channels, sample_width, sample_rate, num_frames, comptype, compname = wav.getparams()

        if sample_width == 1:
            params = {"min": 0, "max": 255, "fmt": np.uint8}  # Unsigned Byte
        elif sample_width == 2:
            params = {"min": -32768, "max": 32767, "fmt": np.int16}
        elif sample_width == 3:
            params = {"min": -8388608, "max": 8388607, "fmt": np.int32}
        elif sample_width == 4:
            params = {"min": -2147483648, "max": 2147483647, "fmt": np.int32}
        else:
            raise ValueError("Can't handle sample width {0}".format(sample_width))

        params["center"] = (params["min"] + params["max"]) / 2

        byte_frames = wav.readframes(num_frames * num_channels)
        if sample_width == 3:
            num_samples = len(byte_frames) // (sample_width * num_channels)
            arr = np.empty((num_samples, num_channels, 4), dtype=np.uint8)
            raw_bytes = np.frombuffer(byte_frames, dtype=np.uint8)
            arr[:, :, :sample_width] = raw_bytes.reshape(-1, num_channels, sample_width)
            arr[:, :, sample_width:] = (arr[:, :, sample_width - 1:sample_width] >> 7) * 255
            data = arr.view(np.int32).flatten()
        else:
            data = np.frombuffer(byte_frames, dtype=params["fmt"])

        self.iq_array = IQArray(None, np.float32, n=num_frames)
        if num_channels == 1:
            self.iq_array.real = np.multiply(1 / params["max"], np.subtract(data, params["center"]))
            self.__already_demodulated = True
        elif num_channels == 2:
            self.iq_array.real = np.multiply(1 / params["max"], np.subtract(data[0::2], params["center"]))
            self.iq_array.imag = np.multiply(1 / params["max"], np.subtract(data[1::2], params["center"]))
        else:
            raise ValueError("Can't handle {0} channels. Only 1 and 2 are supported.".format(num_channels))

        wav.close()

        self.sample_rate = sample_rate

    def __load_compressed_complex(self, filename: str):
        obj = tarfile.open(filename, "r")
        members = obj.getmembers()
        obj.extract(members[0], QDir.tempPath())
        extracted_filename = os.path.join(QDir.tempPath(), obj.getnames()[0])
        self.__load_complex_file(extracted_filename)
        os.remove(extracted_filename)

    @property
    def already_demodulated(self) -> bool:
        return self.__already_demodulated

    @property
    def sample_rate(self):
        return self.__sample_rate

    @sample_rate.setter
    def sample_rate(self, val):
        if val != self.sample_rate:
            self.__sample_rate = val
            self.sample_rate_changed.emit(val)

    @property
    def parameter_cache(self) -> dict:
        """
        Caching bit_len and center for modulations, so they do not need
        to be recalculated every time.

        :return:
        """
        return self.__parameter_cache

    @parameter_cache.setter
    def parameter_cache(self, val):
        self.__parameter_cache = val

    @property
    def modulation_type(self) -> str:
        return self.__modulation_type

    @modulation_type.setter
    def modulation_type(self, value: str):
        if self.__modulation_type != value:
            self.__modulation_type = value
            self._qad = None

            self.modulation_type_changed.emit(self.__modulation_type)
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def bits_per_symbol(self):
        return self.__bits_per_symbol

    @bits_per_symbol.setter
    def bits_per_symbol(self, value: int):
        if self.__bits_per_symbol != value:
            self.__bits_per_symbol = int(value)
            self._qad = None

            self.bits_per_symbol_changed.emit(self.__bits_per_symbol)
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def samples_per_symbol(self):
        return self.__samples_per_symbol

    @samples_per_symbol.setter
    def samples_per_symbol(self, value):
        if self.__samples_per_symbol != value:
            self.__samples_per_symbol = value
            self.samples_per_symbol_changed.emit(value)
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def modulation_order(self):
        return 2 ** self.bits_per_symbol

    @property
    def tolerance(self):
        return self.__tolerance

    @tolerance.setter
    def tolerance(self, value):
        value = int(value)
        if self.__tolerance != value:
            self.__tolerance = value
            self.tolerance_changed.emit(value)
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def center(self):
        return self.__center

    @center.setter
    def center(self, value: float):
        if self.__center != value:
            self.__center = value
            self.center_changed.emit(value)
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def center_spacing(self) -> float:
        return self.__center_spacing

    @center_spacing.setter
    def center_spacing(self, value: float):
        if self.__center_spacing != value:
            self.__center_spacing = value
            self.center_spacing_changed.emit(value)
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def center_thresholds(self):
        return self.get_thresholds_for_center(self.center)

    @property
    def pause_threshold(self) -> int:
        return self.__pause_threshold

    @pause_threshold.setter
    def pause_threshold(self, value: int):
        if self.__pause_threshold != value:
            self.__pause_threshold = value
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def costas_loop_bandwidth(self):
        return self.__costas_loop_bandwidth

    @costas_loop_bandwidth.setter
    def costas_loop_bandwidth(self, value: float):
        if self.__costas_loop_bandwidth != value:
            self.__costas_loop_bandwidth = value
            self._qad = None
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def message_length_divisor(self) -> int:
        return self.__message_length_divisor

    @message_length_divisor.setter
    def message_length_divisor(self, value: int):
        if self.__message_length_divisor != value:
            self.__message_length_divisor = value
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if value != self.__name:
            self.__name = value
            self.name_changed.emit(self.__name)

    @property
    def num_samples(self):
        return self.iq_array.num_samples

    @property
    def noise_threshold(self):
        return self._noise_threshold

    @noise_threshold.setter
    def noise_threshold(self, value):
        if value != self.noise_threshold:
            self._qad = None
            self.clear_parameter_cache()
            self._noise_threshold = value

            middle = 0.5*sum(IQArray.min_max_for_dtype(self.iq_array.dtype))
            a = self.max_amplitude * value / self.max_magnitude
            self.noise_min_plot = middle - a
            self.noise_max_plot = middle + a
            self.noise_threshold_changed.emit()
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def max_magnitude(self):
        mi, ma = IQArray.min_max_for_dtype(self.iq_array.dtype)
        return (2 * max(mi**2, ma**2))**0.5

    @property
    def max_amplitude(self):
        mi, ma = IQArray.min_max_for_dtype(self.iq_array.dtype)
        return 0.5 * (ma - mi)

    @property
    def noise_threshold_relative(self):
        return self.noise_threshold / self.max_magnitude

    @noise_threshold_relative.setter
    def noise_threshold_relative(self, value: float):
        self.noise_threshold = value * self.max_magnitude

    @property
    def qad(self):
        if self._qad is None:
            if self.already_demodulated:
                self._qad = np.ascontiguousarray(self.real_plot_data, dtype=self.real_plot_data.dtype)
            else:
                self._qad = self.quad_demod()

        return self._qad

    @property
    def real_plot_data(self):
        try:
            return self.iq_array.real
        except AttributeError:
            return np.zeros(0, dtype=np.float32)

    @property
    def changed(self) -> bool:
        """
        Determines whether the signal was changed (e.g. cropped/muted) and not saved yet

        :return:
        """
        return self.__changed

    @changed.setter
    def changed(self, val: bool):
        if val != self.__changed:
            self.__changed = val
            self.saved_status_changed.emit()

    def save(self):
        if self.changed:
            self.save_as(self.filename)

    def save_as(self, filename: str):
        QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        self.filename = filename
        FileOperator.save_signal(self)
        self.name = os.path.splitext(os.path.basename(filename))[0]
        self.changed = False
        QApplication.instance().restoreOverrideCursor()

    def quad_demod(self):
        return signal_functions.afp_demod(self.iq_array.data, self.noise_threshold,
                                          self.modulation_type, self.modulation_order,
                                          self.costas_loop_bandwidth)

    def calc_relative_noise_threshold_from_range(self, noise_start: int, noise_end: int):
        num_digits = 4
        noise_start, noise_end = int(noise_start), int(noise_end)

        if noise_start > noise_end:
            noise_start, noise_end = noise_end, noise_start

        try:
            maximum = np.max(self.iq_array.subarray(noise_start, noise_end).magnitudes_normalized)
            return np.ceil(maximum * 10 ** num_digits) / 10 ** num_digits
        except ValueError:
            logger.warning("Could not calculate noise threshold for range {}-{}".format(noise_start, noise_end))
            return self.noise_threshold_relative

    def create_new(self, start=0, end=0, new_data=None):
        new_signal = Signal("", "New " + self.name)

        if new_data is None:
            new_signal.iq_array = IQArray(self.iq_array[start:end])
        else:
            new_signal.iq_array = IQArray(new_data)

        new_signal._noise_threshold = self.noise_threshold
        new_signal.noise_min_plot = self.noise_min_plot
        new_signal.noise_max_plot = self.noise_max_plot
        new_signal.__samples_per_symbol = self.samples_per_symbol
        new_signal.__bits_per_symbol = self.bits_per_symbol
        new_signal.__center = self.center
        new_signal.wav_mode = self.wav_mode
        new_signal.__already_demodulated = self.__already_demodulated
        new_signal.changed = True
        return new_signal

    def get_thresholds_for_center(self, center: float, spacing=None):
        spacing = self.center_spacing if spacing is None else spacing
        return signal_functions.get_center_thresholds(center, spacing, self.modulation_order)

    def auto_detect(self, emit_update=True, detect_modulation=True, detect_noise=False) -> bool:
        kwargs = {"noise": None if detect_noise else self.noise_threshold,
                  "modulation": None if detect_modulation
                  else "OOK" if self.bits_per_symbol == 1 and self.modulation_type == "ASK"
                  else self.modulation_type}

        estimated_params = AutoInterpretation.estimate(self.iq_array, **kwargs)
        if estimated_params is None:
            return False

        orig_block = self.block_protocol_update
        self.block_protocol_update = True

        if detect_noise:
            self.noise_threshold = estimated_params["noise"]

        if detect_modulation:
            self.modulation_type = estimated_params["modulation_type"]

        self.center = estimated_params["center"]
        self.tolerance = estimated_params["tolerance"]
        self.samples_per_symbol = estimated_params["bit_length"]

        self.block_protocol_update = orig_block

        if emit_update and not self.block_protocol_update:
            self.protocol_needs_update.emit()

        return True

    def clear_parameter_cache(self):
        for mod in self.parameter_cache.keys():
            self.parameter_cache[mod]["samples_per_symbol"] = None
            self.parameter_cache[mod]["center"] = None

    def estimate_frequency(self, start: int, end: int, sample_rate: float):
        """
        Estimate the frequency of the baseband signal using FFT

        :param start: Start of the area that shall be investigated
        :param end: End of the area that shall be investigated
        :param sample_rate: Sample rate of the signal
        :return:
        """
        # ensure power of 2 for faster fft
        length = 2 ** int(math.log2(end - start))
        data = self.iq_array.as_complex64()[start:start + length]

        try:
            w = np.fft.fft(data)
            frequencies = np.fft.fftfreq(len(w))
            idx = np.argmax(np.abs(w))
            freq = frequencies[idx]
            freq_in_hertz = abs(freq * sample_rate)
        except ValueError:
            # No samples in window e.g. start == end, use a fallback
            freq_in_hertz = 100e3

        return freq_in_hertz

    def eliminate(self):
        self.iq_array = None
        self._qad = None
        self.parameter_cache.clear()

    def silent_set_modulation_type(self, mod_type: str):
        self.__modulation_type = mod_type

    def insert_data(self, index: int, data: np.ndarray):
        self.iq_array.insert_subarray(index, data)
        self._qad = None

        self.__invalidate_after_edit()

    def delete_range(self, start: int, end: int):
        mask = np.ones(self.num_samples, dtype=bool)
        mask[start:end] = False

        try:
            self.iq_array.apply_mask(mask)
            self._qad = self._qad[mask] if self._qad is not None else None
        except IndexError as e:
            logger.warning("Could not delete data: " + str(e))

        self.__invalidate_after_edit()

    def mute_range(self, start: int, end: int):
        self.iq_array[start:end] = 0
        if self._qad is not None:
            self._qad[start:end] = 0

        self.__invalidate_after_edit()

    def crop_to_range(self, start: int, end: int):
        self.iq_array = IQArray(self.iq_array[start:end])
        self._qad = self._qad[start:end] if self._qad is not None else None

        self.__invalidate_after_edit()

    def filter_range(self, start: int, end: int, fir_filter: Filter):
        self.iq_array[start:end] = fir_filter.work(self.iq_array[start:end])
        self._qad[start:end] = signal_functions.afp_demod(self.iq_array[start:end],
                                                          self.noise_threshold,
                                                          self.modulation_type,
                                                          self.modulation_order,
                                                          self.costas_loop_bandwidth)
        self.__invalidate_after_edit()

    def __invalidate_after_edit(self):
        self.clear_parameter_cache()
        self.changed = True
        self.data_edited.emit()
        self.protocol_needs_update.emit()

    @staticmethod
    def from_samples(samples: np.ndarray, name: str, sample_rate: float):
        signal = Signal("", name, sample_rate=sample_rate)
        signal.iq_array = IQArray(samples)

        return signal
