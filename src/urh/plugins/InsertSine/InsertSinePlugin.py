import logging
import os

import numpy as np
from PyQt5 import uic
from PyQt5.QtCore import QRegExp, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QColor, QPen, QRegExpValidator
from PyQt5.QtWidgets import QApplication, QDialog

from urh.plugins.Plugin import SignalEditorPlugin
from urh.signalprocessing.IQArray import IQArray
from urh.ui.painting.SceneManager import SceneManager
from urh.util.Formatter import Formatter
from urh.util.Logger import logger


class InsertSinePlugin(SignalEditorPlugin):
    insert_sine_wave_clicked = pyqtSignal()

    INSERT_INDICATOR_COLOR = QColor(0, 255, 0, 80)

    def __init__(self):
        self.__dialog_ui = None  # type: QDialog
        self.complex_wave = None

        self.__amplitude = 0.5
        self.__frequency = 10
        self.__phase = 0
        self.__sample_rate = 1e6
        self.__num_samples = int(1e6)

        self.original_data = None
        self.draw_data = None
        self.position = 0

        super().__init__(name="InsertSine")

    @property
    def dialog_ui(self) -> QDialog:
        if self.__dialog_ui is None:
            dir_name = (
                os.path.dirname(os.readlink(__file__))
                if os.path.islink(__file__)
                else os.path.dirname(__file__)
            )

            logging.getLogger().setLevel(logging.WARNING)
            self.__dialog_ui = uic.loadUi(
                os.path.realpath(os.path.join(dir_name, "insert_sine_dialog.ui"))
            )
            logging.getLogger().setLevel(logger.level)

            self.__dialog_ui.setAttribute(Qt.WA_DeleteOnClose)
            self.__dialog_ui.setModal(True)
            self.__dialog_ui.doubleSpinBoxAmplitude.setValue(self.__amplitude)
            self.__dialog_ui.doubleSpinBoxFrequency.setValue(self.__frequency)
            self.__dialog_ui.doubleSpinBoxPhase.setValue(self.__phase)
            self.__dialog_ui.doubleSpinBoxSampleRate.setValue(self.__sample_rate)
            self.__dialog_ui.doubleSpinBoxNSamples.setValue(self.__num_samples)
            self.__dialog_ui.lineEditTime.setValidator(
                QRegExpValidator(QRegExp(r"[0-9]+([nmµ]?|([\.,][0-9]{1,3}[nmµ]?))?$"))
            )

            scene_manager = SceneManager(self.dialog_ui.graphicsViewSineWave)
            self.__dialog_ui.graphicsViewSineWave.scene_manager = scene_manager
            self.insert_indicator = scene_manager.scene.addRect(
                0,
                -2,
                0,
                4,
                QPen(QColor(Qt.transparent), 0),
                QBrush(self.INSERT_INDICATOR_COLOR),
            )
            self.insert_indicator.stackBefore(scene_manager.scene.selection_area)

            self.set_time()

        return self.__dialog_ui

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

    def create_dialog_connects(self):
        self.dialog_ui.doubleSpinBoxAmplitude.editingFinished.connect(
            self.on_double_spin_box_amplitude_editing_finished
        )
        self.dialog_ui.doubleSpinBoxFrequency.editingFinished.connect(
            self.on_double_spin_box_frequency_editing_finished
        )
        self.dialog_ui.doubleSpinBoxPhase.editingFinished.connect(
            self.on_double_spin_box_phase_editing_finished
        )
        self.dialog_ui.doubleSpinBoxSampleRate.editingFinished.connect(
            self.on_double_spin_box_sample_rate_editing_finished
        )
        self.dialog_ui.doubleSpinBoxNSamples.editingFinished.connect(
            self.on_spin_box_n_samples_editing_finished
        )
        self.dialog_ui.lineEditTime.editingFinished.connect(
            self.on_line_edit_time_editing_finished
        )
        self.dialog_ui.buttonBox.accepted.connect(self.on_button_box_accept)
        self.dialog_ui.buttonBox.rejected.connect(self.on_button_box_reject)
        self.__dialog_ui.finished.connect(self.on_dialog_finished)

    def get_insert_sine_dialog(
        self, original_data, position, sample_rate=None, num_samples=None
    ) -> QDialog:
        if sample_rate is not None:
            self.__sample_rate = sample_rate
            self.dialog_ui.doubleSpinBoxSampleRate.setValue(sample_rate)

        if num_samples is not None:
            self.__num_samples = int(num_samples)
            self.dialog_ui.doubleSpinBoxNSamples.setValue(num_samples)

        self.original_data = original_data
        self.position = position

        self.set_time()
        self.draw_sine_wave()
        self.create_dialog_connects()

        return self.dialog_ui

    def draw_sine_wave(self):
        if self.dialog_ui.graphicsViewSineWave.scene_manager:
            self.dialog_ui.graphicsViewSineWave.scene_manager.clear_path()

        QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        self.__set_status_of_editable_elements(enabled=False)

        t = np.arange(0, self.num_samples) / self.sample_rate
        arg = 2 * np.pi * self.frequency * t + self.phase

        self.complex_wave = np.empty(len(arg), dtype=np.complex64)
        self.complex_wave.real = np.cos(arg)
        self.complex_wave.imag = np.sin(arg)
        self.complex_wave = IQArray(self.amplitude * self.complex_wave).convert_to(
            self.original_data.dtype
        )

        self.draw_data = np.insert(
            self.original_data[:, 0], self.position, self.complex_wave[:, 0]
        )
        y, h = (
            self.dialog_ui.graphicsViewSineWave.view_rect().y(),
            self.dialog_ui.graphicsViewSineWave.view_rect().height(),
        )
        self.insert_indicator.setRect(
            self.position, y - h, self.num_samples, 2 * h + abs(y)
        )

        self.__set_status_of_editable_elements(enabled=True)
        QApplication.instance().restoreOverrideCursor()
        self.dialog_ui.graphicsViewSineWave.plot_data(self.draw_data)
        self.dialog_ui.graphicsViewSineWave.show_full_scene()

    def __set_status_of_editable_elements(self, enabled: bool):
        for obj in (
            "doubleSpinBoxAmplitude",
            "doubleSpinBoxFrequency",
            "doubleSpinBoxPhase",
            "doubleSpinBoxSampleRate",
            "doubleSpinBoxNSamples",
            "lineEditTime",
            "buttonBox",
        ):
            getattr(self.dialog_ui, obj).setEnabled(enabled)

    def set_time(self):
        self.dialog_ui.lineEditTime.setText(
            Formatter.science_time(
                self.num_samples / self.sample_rate,
                decimals=3,
                append_seconds=False,
                remove_spaces=True,
            )
        )

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

        factor = (
            10**-9
            if suffix == "n"
            else 10**-6
            if suffix == "µ"
            else 10**-3
            if suffix == "m"
            else 1
        )
        time_val = t * factor

        if self.sample_rate * time_val >= 1:
            self.dialog_ui.doubleSpinBoxNSamples.setValue(self.sample_rate * time_val)
            self.dialog_ui.doubleSpinBoxNSamples.editingFinished.emit()
        else:
            self.set_time()

    @pyqtSlot()
    def on_button_box_reject(self):
        self.dialog_ui.reject()

    @pyqtSlot()
    def on_button_box_accept(self):
        self.insert_sine_wave_clicked.emit()
        self.dialog_ui.accept()

    @pyqtSlot()
    def on_dialog_finished(self):
        self.sender().graphicsViewSineWave.eliminate()
        self.__dialog_ui = None
