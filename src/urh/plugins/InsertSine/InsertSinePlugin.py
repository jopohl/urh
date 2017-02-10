import os

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

    def __init__(self):
        dirname = os.path.dirname(os.readlink(__file__)) if os.path.islink(__file__) else os.path.dirname(__file__)
        self.dialog_ui = uic.loadUi(os.path.realpath(os.path.join(dirname, "insert_sine_dialog.ui")))  # type: QDialog

        self.complex_wave = None
        self.amplitude = 0.5
        self.frequency = 10
        self.phase = 0
        self.sample_rate = 1e6
        self.num_samples = 1e6

        self.dialog_ui.doubleSpinBoxAmplitude.setValue(self.amplitude)
        self.dialog_ui.doubleSpinBoxFrequency.setValue(self.frequency)
        self.dialog_ui.doubleSpinBoxPhase.setValue(self.phase)
        self.dialog_ui.doubleSpinBoxSampleRate.setValue(self.sample_rate)
        self.dialog_ui.doubleSpinBoxNSamples.setValue(self.num_samples)
        self.dialog_ui.lineEditTime.setValidator(QRegExpValidator(QRegExp("[0-9]([nmµ]|([\.,][0-9]{1,3}[nmµ]))?$")))
        self.dialog_ui.lineEditTime.setText(Formatter.science_time(self.num_samples/self.sample_rate, decimals=3,
                                                                   append_seconds=False, remove_spaces=True))

        super().__init__(name="InsertSine")

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

    def show_insert_sine_dialog(self, sample_rate=None):
        self.dialog_ui.show()
        self.__create_dialog_connects()
        if sample_rate is not None:
            self.sample_rate = sample_rate
            self.dialog_ui.doubleSpinBoxSampleRate.setValue(sample_rate)
        self.draw_sine_wave()

    def draw_sine_wave(self):
        self.complex_wave = np.empty(int(self.num_samples), dtype=np.complex64)
        t = (np.arange(0, self.num_samples) / self.sample_rate)
        self.complex_wave.real = self.amplitude * np.cos(2 * np.pi * self.frequency * t + self.phase)
        self.complex_wave.imag = self.amplitude * np.sin(2 * np.pi * self.frequency * t + self.phase)

        self.dialog_ui.graphicsViewSineWave.plot_data(self.complex_wave.imag.astype(np.float32))
        self.dialog_ui.graphicsViewSineWave.draw_full()

    @pyqtSlot()
    def on_double_spin_box_amplitude_editing_finished(self):
        self.amplitude = self.dialog_ui.doubleSpinBoxAmplitude.value()
        self.draw_sine_wave()

    @pyqtSlot()
    def on_double_spin_box_frequency_editing_finished(self):
        self.frequency = self.dialog_ui.doubleSpinBoxFrequency.value()
        self.draw_sine_wave()

    @pyqtSlot()
    def on_double_spin_box_phase_editing_finished(self):
        self.phase = self.dialog_ui.doubleSpinBoxPhase.value()
        self.draw_sine_wave()

    @pyqtSlot()
    def on_double_spin_box_sample_rate_editing_finished(self):
        self.sample_rate = self.dialog_ui.doubleSpinBoxSampleRate.value()
        self.dialog_ui.lineEditTime.setText(Formatter.science_time(self.num_samples / self.sample_rate, decimals=3,
                                                                   append_seconds=False, remove_spaces=True))
        self.draw_sine_wave()

    @pyqtSlot()
    def on_spin_box_n_samples_editing_finished(self):
        self.num_samples = self.dialog_ui.doubleSpinBoxNSamples.value()
        self.dialog_ui.lineEditTime.setText(Formatter.science_time(self.num_samples / self.sample_rate, decimals=3,
                                                                   append_seconds=False, remove_spaces=True))
        self.draw_sine_wave()

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
            self.num_samples = self.sample_rate * time_val
            self.dialog_ui.doubleSpinBoxNSamples.setValue(self.num_samples)

            self.draw_sine_wave()

        self.dialog_ui.lineEditTime.setText(Formatter.science_time(self.num_samples / self.sample_rate, decimals=3,
                                                                   append_seconds=False, remove_spaces=True))

    @pyqtSlot()
    def on_btn_abort_clicked(self):
        self.dialog_ui.close()

    @pyqtSlot()
    def on_btn_ok_clicked(self):
        self.insert_sine_wave_clicked.emit()
        self.dialog_ui.close()
