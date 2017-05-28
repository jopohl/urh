import os
import struct
import tarfile
import wave

import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject, QDir, Qt
from PyQt5.QtWidgets import QApplication

import urh.cythonext.signalFunctions as signal_functions
from urh import constants
from urh.signalprocessing.Filter import Filter
from urh.util import FileOperator
from urh.util.Logger import logger


class Signal(QObject):
    """
    Representation of a loaded signal (complex file).
    """


    MODULATION_TYPES = ["ASK", "FSK", "PSK", "QAM"]

    bit_len_changed = pyqtSignal(int)
    tolerance_changed = pyqtSignal(int)
    noise_threshold_changed = pyqtSignal()
    qad_center_changed = pyqtSignal(float)
    name_changed = pyqtSignal(str)
    sample_rate_changed = pyqtSignal(float)
    modulation_type_changed = pyqtSignal()

    saved_status_changed = pyqtSignal()
    protocol_needs_update = pyqtSignal()
    data_edited = pyqtSignal()  # On Crop/Mute/Delete etc.

    def __init__(self, filename: str, name: str, wav_is_qad_demod=False,
                 modulation: str = None, sample_rate: float = 1e6, parent=None):
        super().__init__(parent)
        self.__name = name
        self.__tolerance = 5
        self.__bit_len = 100
        self._qad = None
        self.__qad_center = 0
        self._noise_threshold = 0
        self.__sample_rate = sample_rate
        self.noise_min_plot = 0
        self.noise_max_plot = 0
        self.block_protocol_update = False

        self.auto_detect_on_modulation_changed = True
        self.wav_mode = filename.endswith(".wav")
        self.__changed = False
        self.qad_demod_file_loaded = wav_is_qad_demod
        if modulation is None:
            modulation = "FSK"
        self.__modulation_type = self.MODULATION_TYPES.index(modulation)
        self.__parameter_cache = {mod: {"qad_center": None, "bit_len": None} for mod in self.MODULATION_TYPES}

        if len(filename) > 0:
            # Daten auslesen
            if not self.wav_mode:
                if not filename.endswith(".coco"):
                    if filename.endswith(".complex16u"):
                        # two 8 bit unsigned integers
                        raw = np.fromfile(filename, dtype=[('r', np.uint8), ('i', np.uint8)])
                        self._fulldata = np.empty(raw.shape[0], dtype=np.complex64)
                        self._fulldata.real = (raw['r'] / 127.5) - 1.0
                        self._fulldata.imag = (raw['i'] / 127.5) - 1.0
                    elif filename.endswith(".complex16s"):
                        # two 8 bit signed integers
                        raw = np.fromfile(filename, dtype=[('r', np.int8), ('i', np.int8)])
                        self._fulldata = np.empty(raw.shape[0], dtype=np.complex64)
                        self._fulldata.real = (raw['r'] + 0.5) / 127.5
                        self._fulldata.imag = (raw['i'] + 0.5) / 127.5
                    else:
                        self._fulldata = np.fromfile(filename, dtype=np.complex64)  # Uncompressed
                else:
                    obj = tarfile.open(filename, "r")
                    members = obj.getmembers()
                    obj.extract(members[0], QDir.tempPath())
                    extracted_filename = os.path.join(QDir.tempPath(), obj.getnames()[0])
                    self._fulldata = np.fromfile(extracted_filename, dtype=np.complex64)
                    os.remove(extracted_filename)

                self._fulldata = np.ascontiguousarray(self._fulldata, dtype=np.complex64)  # type: np.ndarray
            else:
                f = wave.open(filename, "r")
                n = f.getnframes()
                unsigned_bytes = struct.unpack('<{0:d}B'.format(n), f.readframes(n))
                if not self.qad_demod_file_loaded:
                    # Complex To Real WAV File load
                    self._fulldata = np.empty(n, dtype=np.complex64, order="C")
                    self._fulldata.real = np.multiply(1/256, np.subtract(unsigned_bytes, 128))
                    self._fulldata.imag = [-1/128] * n
                else:
                    self._fulldata = np.multiply(1 / 256, np.subtract(unsigned_bytes, 128).astype(np.int8)).astype(
                        np.float32)
                    self._fulldata = np.ascontiguousarray(self._fulldata, dtype=np.float32)

                f.close()

            self.filename = filename

            if not self.qad_demod_file_loaded:
                self.noise_threshold = self.calc_noise_threshold(int(0.99 * self.num_samples), self.num_samples)

        else:
            self.filename = ""

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
        Caching bit_len and qad_center for modulations, so they do not need
        to be recalculated every time.

        :return:
        """
        return self.__parameter_cache

    @parameter_cache.setter
    def parameter_cache(self, val):
        self.__parameter_cache = val

    @property
    def modulation_type(self):
        return self.__modulation_type

    @modulation_type.setter
    def modulation_type(self, value: str):
        """
        0 - "ASK", 1 - "FSK", 2 - "PSK", 3 - "APSK (QAM)"

        :param value:
        :return:
        """
        if self.__modulation_type != value:
            self.__modulation_type = value
            self._qad = None

            if self.auto_detect_on_modulation_changed:
                self.auto_detect(emit_update=False)

            self.modulation_type_changed.emit()
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def modulation_type_str(self):
        return self.MODULATION_TYPES[self.modulation_type]

    @property
    def bit_len(self):
        return self.__bit_len

    @bit_len.setter
    def bit_len(self, value):
        if self.__bit_len != value:
            self.__bit_len = value
            self.bit_len_changed.emit(value)
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def tolerance(self):
        return self.__tolerance

    @tolerance.setter
    def tolerance(self, value):
        if self.__tolerance != value:
            self.__tolerance = value
            self.tolerance_changed.emit(value)
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def qad_center(self):
        return self.__qad_center

    @qad_center.setter
    def qad_center(self, value: float):
        if self.__qad_center != value:
            self.__qad_center = value
            self.qad_center_changed.emit(value)
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
        return len(self.data)

    @property
    def noise_threshold(self):
        return self._noise_threshold

    @noise_threshold.setter
    def noise_threshold(self, value):
        if value != self.noise_threshold:
            self._qad = None
            self.clear_parameter_cache()
            self._noise_threshold = value
            self.noise_min_plot = -value
            self.noise_max_plot = value
            self.noise_threshold_changed.emit()
            if not self.block_protocol_update:
                self.protocol_needs_update.emit()

    @property
    def qad(self):
        if self._qad is None:
            self._qad = self.data if self.qad_demod_file_loaded else self.quad_demod()

        return self._qad

    @property
    def data(self) -> np.ndarray:
        return self._fulldata

    @property
    def real_plot_data(self):
        try:
            return self.data.real
        except AttributeError:
            return np.zeros(0, dtype=np.float32)
    @property
    def wave_data(self):
        return bytearray(np.multiply(-1, (np.round(self.data.real * 127)).astype(np.int8)))

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

    def get_signal_start(self) -> int:
        """
        Index ab dem das Signal losgeht (Nach Übersteuern + Pause am Anfang)

        """
        return signal_functions.find_signal_start(self.qad, self.modulation_type)

    def get_signal_end(self):
        return signal_functions.find_signal_end(self.qad, self.modulation_type)

    def quad_demod(self):
        return signal_functions.afp_demod(self.data, self.noise_threshold, self.modulation_type)

    def calc_noise_threshold(self, noise_start: int, noise_end: int):
        num_digits = 4
        noise_start, noise_end = int(noise_start), int(noise_end)
        try:
            magnitudes = np.absolute(self.data[noise_start:noise_end])
            maximum = np.max(magnitudes)
            return np.ceil(maximum * 10 ** num_digits) / 10 ** num_digits
        except ValueError:
            logger.warning("Could not calculate noise threshold for range {}-{}".format(noise_start, noise_end))
            return self.noise_threshold

    def estimate_bitlen(self) -> int:
        bit_len = self.__parameter_cache[self.modulation_type_str]["bit_len"]
        if bit_len is None:
            bit_len = signal_functions.estimate_bit_len(self.qad, self.qad_center, self.tolerance, self.modulation_type)
            self.__parameter_cache[self.modulation_type_str]["bit_len"] = bit_len
        return bit_len

    def estimate_qad_center(self) -> float:
        center = self.__parameter_cache[self.modulation_type_str]["qad_center"]
        if center is None:
            noise_value = signal_functions.get_noise_for_mod_type(int(self.modulation_type))
            qad = self.qad[np.where(self.qad > noise_value)] if noise_value < 0 else self.qad
            center = signal_functions.estimate_qad_center(qad, constants.NUM_CENTERS)
            self.__parameter_cache[self.modulation_type_str]["qad_center"] = center
        return center

    def create_new(self, start:int, end:int):
        new_signal = Signal("", "New " + self.name)
        new_signal._fulldata = self.data[start:end]
        new_signal._noise_threshold = self.noise_threshold
        new_signal.noise_min_plot = self.noise_min_plot
        new_signal.noise_max_plot = self.noise_max_plot
        new_signal.__bit_len = self.bit_len
        new_signal.history = [("Crop", 0, len(self._fulldata))]
        new_signal.cur_history_index = 0
        new_signal.__qad_center = self.qad_center
        new_signal.changed = True
        return new_signal

    def auto_detect(self, emit_update=True):
        needs_update = False
        old_qad_center = self.__qad_center
        self.__qad_center = self.estimate_qad_center()
        if self.__qad_center != old_qad_center:
            self.qad_center_changed.emit(self.__qad_center)
            needs_update = True

        old_bit_len = self.__bit_len
        self.__bit_len = self.estimate_bitlen()
        if self.__bit_len != old_bit_len:
            self.bit_len_changed.emit(self.__bit_len)
            needs_update = True

        if emit_update and needs_update and not self.block_protocol_update:
            self.protocol_needs_update.emit()

    def clear_parameter_cache(self):
        for mod in self.parameter_cache.keys():
            self.parameter_cache[mod]["bit_len"] = None
            self.parameter_cache[mod]["qad_center"] = None

    def estimate_frequency(self, start: int, end: int, sample_rate: float):
        """
        Estimate the frequency of the baseband signal using FFT

        :param start: Start of the area that shall be investigated
        :param end: End of the area that shall be investigated
        :param sample_rate: Sample rate of the signal
        :return:
        """
        data = self.data[start:end]

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
        self._fulldata = None
        self._qad = None
        self.parameter_cache.clear()

    def silent_set_modulation_type(self, mod_type: int):
        self.__modulation_type = mod_type

    def insert_data(self, index: int, data: np.ndarray):
        self._fulldata = np.insert(self._fulldata, index, data)
        self._qad = None

        self.__invalidate_after_edit()

    def delete_range(self, start: int, end: int):
        mask = np.ones(self.num_samples, dtype=bool)
        mask[start:end] = False

        try:
            self._fulldata = self._fulldata[mask]
            self._qad = self._qad[mask] if self._qad is not None else None
        except IndexError as e:
            logger.warning("Could not delete data: " + str(e))

        self.__invalidate_after_edit()

    def mute_range(self, start: int, end: int):
        self._fulldata[start:end] = 0
        if self._qad is not None:
            self._qad[start:end] = 0

        self.__invalidate_after_edit()

    def crop_to_range(self, start: int, end: int):
        self._fulldata = self._fulldata[start:end]
        self._qad = self._qad[start:end] if self._qad is not None else None

        self.__invalidate_after_edit()

    def filter_range(self, start: int, end: int, fir_filter: Filter):
        self._fulldata[start:end] = fir_filter.apply_fir_filter(self._fulldata[start:end])
        self._qad[start:end] = signal_functions.afp_demod(self.data[start:end],
                                                          self.noise_threshold, self.modulation_type)
        self.__invalidate_after_edit()

    def __invalidate_after_edit(self):
        self.clear_parameter_cache()
        self.changed = True
        self.data_edited.emit()
        self.protocol_needs_update.emit()

    @staticmethod
    def from_samples(samples: np.ndarray, name: str, sample_rate: float):
        signal = Signal("", name, sample_rate=sample_rate)
        signal._fulldata = samples

        return signal
