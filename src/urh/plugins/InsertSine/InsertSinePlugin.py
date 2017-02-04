import os

import numpy as np
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from urh.plugins.Plugin import SignalEditorPlugin
from urh.util.Formatter import Formatter


class InsertSinePlugin(SignalEditorPlugin):
    def __init__(self):
        dirname = os.path.dirname(os.readlink(__file__)) if os.path.islink(__file__) else os.path.dirname(__file__)
        self.dialog_ui = uic.loadUi(os.path.realpath(os.path.join(dirname, "insert_sine_dialog.ui")))  # type: QDialog

        self.amplitude = 1
        self.frequency = 10
        self.phase = 0
        self.sample_rate = 1e6
        self.num_samples = 1e6

        self.dialog_ui.doubleSpinBoxAmplitude.setValue(self.amplitude)
        self.dialog_ui.doubleSpinBoxFrequency.setValue(self.frequency)
        self.dialog_ui.doubleSpinBoxPhase.setValue(self.phase)
        self.dialog_ui.doubleSpinBoxSampleRate.setValue(self.sample_rate)
        self.dialog_ui.doubleSpinBoxNSamples.setValue(self.num_samples)
        self.dialog_ui.labelTime.setText(Formatter.science_time(self.num_samples/self.sample_rate, decimals=3))

        super().__init__(name="InsertSine")

    def create_connects(self):
        pass

    def __create_dialog_connects(self):
        self.dialog_ui.doubleSpinBoxAmplitude.valueChanged.connect(self.on_double_spin_box_amplitude_value_changed)
        self.dialog_ui.doubleSpinBoxFrequency.valueChanged.connect(self.on_double_spin_box_frequency_value_changed)
        self.dialog_ui.doubleSpinBoxPhase.valueChanged.connect(self.on_double_spin_box_phase_value_changed)
        self.dialog_ui.doubleSpinBoxSampleRate.valueChanged.connect(self.on_double_spin_box_sample_rate_value_changed)
        self.dialog_ui.doubleSpinBoxNSamples.valueChanged.connect(self.on_spin_box_n_samples_value_changed)

    def show_insert_sine_dialog(self):
        self.dialog_ui.show()
        self.__create_dialog_connects()
        self.draw_sine_wave()

    def draw_sine_wave(self):
        self.complex_wave = np.empty(int(self.num_samples), dtype=np.complex64)
        t = (np.arange(0, self.num_samples) / self.sample_rate)
        self.complex_wave.real = self.amplitude * np.cos(2 * np.pi * self.frequency * t + self.phase)
        self.complex_wave.imag = self.amplitude * np.sin(2 * np.pi * self.frequency * t + self.phase)

        self.dialog_ui.graphicsViewSineWave.plot_data(self.complex_wave.imag.astype(np.float32))
        self.dialog_ui.graphicsViewSineWave.draw_full()

    @pyqtSlot(float)
    def on_double_spin_box_amplitude_value_changed(self, value: float):
        self.amplitude = value
        self.draw_sine_wave()

    @pyqtSlot(float)
    def on_double_spin_box_frequency_value_changed(self, value: float):
        self.frequency = value
        self.draw_sine_wave()

    @pyqtSlot(float)
    def on_double_spin_box_phase_value_changed(self, value: float):
        self.phase = value
        self.draw_sine_wave()

    @pyqtSlot(float)
    def on_double_spin_box_sample_rate_value_changed(self, value: float):
        self.sample_rate = value
        self.dialog_ui.labelTime.setText(Formatter.science_time(self.num_samples / self.sample_rate, decimals=3))
        self.draw_sine_wave()

    @pyqtSlot(float)
    def on_spin_box_n_samples_value_changed(self, value: float):
        self.num_samples = int(value)
        self.dialog_ui.labelTime.setText(Formatter.science_time(self.num_samples / self.sample_rate, decimals=3))
        self.draw_sine_wave()
