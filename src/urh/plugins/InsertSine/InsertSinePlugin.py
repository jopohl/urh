import os

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
        self.frequency = 1e6
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

    @pyqtSlot(float)
    def on_double_spin_box_amplitude_value_changed(self, value: float):
        self.amplitude = value

    @pyqtSlot(float)
    def on_double_spin_box_frequency_value_changed(self, value: float):
        self.frequency = value

    @pyqtSlot(float)
    def on_double_spin_box_phase_value_changed(self, value: float):
        self.phase = value

    @pyqtSlot(float)
    def on_double_spin_box_sample_rate_value_changed(self, value: float):
        self.sample_rate = value
        self.dialog_ui.labelTime.setText(Formatter.science_time(self.num_samples / self.sample_rate, decimals=3))

    @pyqtSlot(float)
    def on_spin_box_n_samples_value_changed(self, value: float):
        self.num_samples = int(value)
        self.dialog_ui.labelTime.setText(Formatter.science_time(self.num_samples / self.sample_rate, decimals=3))
