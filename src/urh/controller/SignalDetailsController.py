import locale
import os
import time

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog

from urh.ui.ui_signal_details import Ui_SignalDetails
from urh.util.Formatter import Formatter


class SignalDetailsController(QDialog):
    def __init__(self, signal, parent=None):
        super().__init__(parent)
        self.signal = signal
        self.ui = Ui_SignalDetails()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        file = self.signal.filename
        self.ui.lblFile.setText(file)
        self.ui.lblName.setText(self.signal.name)
        self.ui.lblFileSize.setText(locale.format_string("%.2fMB", os.path.getsize(file) / (1024 ** 2)))
        self.ui.lblSamplesTotal.setText("{0:n}".format(self.signal.num_samples).replace(",", " "))
        self.ui.lFileCreated.setText(time.ctime(os.path.getctime(file)))
        self.ui.dsb_sample_rate.setValue(self.signal.sample_rate)
        self.set_duration()

        self.ui.dsb_sample_rate.valueChanged.connect(self.on_dsb_sample_rate_value_changed)

    @pyqtSlot(float)
    def on_dsb_sample_rate_value_changed(self, value: float):
        self.signal.sample_rate = value
        self.set_duration()

    def set_duration(self):
        dur = self.signal.num_samples / self.signal.sample_rate
        self.ui.lDuration.setText(Formatter.science_time(dur))
