import os
import threading

import numpy as np
from PyQt5 import uic
from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog

from urh.plugins.Plugin import SignalEditorPlugin
from urh.util.Formatter import Formatter


class InsertSinePlugin(SignalEditorPlugin):
    insert_sine_wave_clicked = pyqtSignal()
    sine_wave_updated = pyqtSignal()

    def __init__(self):
        dirname = os.path.dirname(os.readlink(__file__)) if os.path.islink(__file__) else os.path.dirname(__file__)
        self.dialog_ui = uic.loadUi(os.path.realpath(os.path.join(dirname, "insert_sine_dialog.ui")))  # type: QDialog

        self.complex_wave = None
        self.__amplitude = 0.5
        self.__frequency = 10
        self.__phase = 0
        self.__sample_rate = 1e6
        self.__num_samples = int(1e6)

        self.dialog_ui.doubleSpinBoxAmplitude.setValue(self.__amplitude)
        self.dialog_ui.doubleSpinBoxFrequency.setValue(self.__frequency)
        self.dialog_ui.doubleSpinBoxPhase.setValue(self.__phase)
        self.dialog_ui.doubleSpinBoxSampleRate.setValue(self.__sample_rate)
        self.dialog_ui.doubleSpinBoxNSamples.setValue(self.__num_samples)
        self.dialog_ui.lineEditTime.setValidator(QRegExpValidator(QRegExp("[0-9]([nmµ]|([\.,][0-9]{1,3}[nmµ]))?$")))
        self.set_time()

        super().__init__(name="InsertSine")

    @property
    def amplitude(self) -> float:
        return self.__amplitude

    @amplitude.setter
    def amplitude(self, value: float):
        if value != self.amplitude:
            self.__amplitude = value
            self.draw_sine_wave()

    @property
    def frequency(self) -> float:
        return self.__frequency

    @frequency.setter
    def frequency(self, value: float):
        if value != self.frequency:
            self.__frequency = value
            self.draw_sine_wave()

    @property
    def phase(self) -> float:
        return self.__phase

    @phase.setter
    def phase(self, value: float):
        if value != self.phase:
            self.__phase = value
            self.draw_sine_wave()

    @property
    def sample_rate(self) -> float:
        return self.__sample_rate

    @sample_rate.setter
    def sample_rate(self, value: float):
        if value != self.sample_rate:
            self.__sample_rate = value
            self.set_time()
            self.draw_sine_wave()

    @property
    def num_samples(self) -> int:
        return self.__num_samples

    @num_samples.setter
    def num_samples(self, value: int):
        value = int(value)
        if value != self.num_samples:
            self.__num_samples = value
            self.set_time()
            self.draw_sine_wave()

    def create_connects(self):
        pass

    def __create_dialog_connects(self):
        self.dialog_ui.doubleSpinBoxAmplitude.editingFinished.connect(self.on_double_spin_box_amplitude_editing_finished)
        self.dialog_ui.doubleSpinBoxFrequency.editingFinished.connect(self.on_double_spin_box_frequency_editing_finished)
        self.dialog_ui.doubleSpinBoxPhase.editingFinished.connect(self.on_double_spin_box_phase_editing_finished)
        self.dialog_ui.doubleSpinBoxSampleRate.editingFinished.connect(self.on_double_spin_box_sample_rate_editing_finished)
        self.dialog_ui.doubleSpinBoxNSamples.editingFinished.connect(self.on_spin_box_n_samples_editing_finished)
        self.dialog_ui.lineEditTime.editingFinished.connect(self.on_line_edit_time_editing_finished)
        self.dialog_ui.btnAbort.clicked.connect(self.on_btn_abort_clicked)
        self.dialog_ui.btnOK.clicked.connect(self.on_btn_ok_clicked)
        self.sine_wave_updated.connect(self.on_sine_wave_updated)

    def show_insert_sine_dialog(self, sample_rate=None, num_samples=None):
        self.dialog_ui.show()
        self.__create_dialog_connects()
        if sample_rate is not None:
            self.sample_rate = sample_rate
            self.dialog_ui.doubleSpinBoxSampleRate.setValue(sample_rate)

        if num_samples is not None:
            self.num_samples = int(num_samples)
            self.dialog_ui.doubleSpinBoxNSamples.setValue(num_samples)

        self.set_time()
        self.draw_sine_wave()

    def draw_sine_wave(self):
        if self.dialog_ui.graphicsViewSineWave.scene_creator:
            self.dialog_ui.graphicsViewSineWave.scene_creator.clear_path()

        sine_thread = threading.Thread(target=self.__update_sine_wave)
        sine_thread.setDaemon(True)
        sine_thread.start()

        for obj in ("doubleSpinBoxAmplitude", "doubleSpinBoxFrequency", "doubleSpinBoxPhase", "doubleSpinBoxSampleRate",
                    "doubleSpinBoxNSamples", "lineEditTime", "btnOK"):
            getattr(self.dialog_ui, obj).setEnabled(False)

    def __update_sine_wave(self):
        self.complex_wave = np.empty(self.num_samples, dtype=np.complex64)
        t = (np.arange(0, self.num_samples) / self.sample_rate)
        self.complex_wave.real = self.amplitude * np.cos(2 * np.pi * self.frequency * t + self.phase)
        self.complex_wave.imag = self.amplitude * np.sin(2 * np.pi * self.frequency * t + self.phase)
        self.sine_wave_updated.emit()

    def on_sine_wave_updated(self):
        for obj in ("doubleSpinBoxAmplitude", "doubleSpinBoxFrequency", "doubleSpinBoxPhase", "doubleSpinBoxSampleRate",
                    "doubleSpinBoxNSamples", "lineEditTime", "btnOK"):
            getattr(self.dialog_ui, obj).setEnabled(True)

        self.dialog_ui.graphicsViewSineWave.plot_data(self.complex_wave.imag.astype(np.float32))
        self.dialog_ui.graphicsViewSineWave.draw_full()

    @pyqtSlot()
    def on_double_spin_box_amplitude_editing_finished(self):
        self.amplitude = self.dialog_ui.doubleSpinBoxAmplitude.value()

    @pyqtSlot()
    def on_double_spin_box_frequency_editing_finished(self):
        self.frequency = self.dialog_ui.doubleSpinBoxFrequency.value()

    @pyqtSlot()
    def on_double_spin_box_phase_editing_finished(self):
        self.phase = self.dialog_ui.doubleSpinBoxPhase.value()

    @pyqtSlot()
    def on_double_spin_box_sample_rate_editing_finished(self):
        self.sample_rate = self.dialog_ui.doubleSpinBoxSampleRate.value()

    @pyqtSlot()
    def on_spin_box_n_samples_editing_finished(self):
        self.num_samples = self.dialog_ui.doubleSpinBoxNSamples.value()

    @pyqtSlot()
    def on_line_edit_time_editing_finished(self):
        time_str = self.dialog_ui.lineEditTime.text().replace(",", ".")
        suffix = ""
        try:
            t = float(time_str)
        except ValueError:
            suffix = time_str[-1]
            try:
                t = float(time_str[:-1])
            except ValueError:
                return

        factor = 10 ** -9 if suffix == "n" else 10 ** -6 if suffix == "µ" else 10 ** -3 if suffix == "m" else 1
        time_val = t * factor

        if self.sample_rate * time_val >= 1:
            self.dialog_ui.doubleSpinBoxNSamples.setValue(self.num_samples)
            self.num_samples = self.sample_rate * time_val
        else:
            self.set_time()

    @pyqtSlot()
    def on_btn_abort_clicked(self):
        self.dialog_ui.close()

    @pyqtSlot()
    def on_btn_ok_clicked(self):
        self.insert_sine_wave_clicked.emit()
        self.dialog_ui.close()

    def set_time(self):
        self.dialog_ui.lineEditTime.setText(Formatter.science_time(self.num_samples/self.sample_rate, decimals=3,
                                                                   append_seconds=False, remove_spaces=True))

