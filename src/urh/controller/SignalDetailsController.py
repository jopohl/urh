import locale
import os
import time

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QMessageBox

from urh.ui.ui_signal_details import Ui_SignalDetails
from urh.util.Formatter import Formatter
from urh.util import FileOperator

class SignalDetailsController(QDialog):
    def __init__(self, signal, parent=None):
        super().__init__(parent)
        self.signal = signal
        if not os.path.isfile(self.signal.filename):
            self.save_signal_as()
        self.ui = Ui_SignalDetails()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        file = self.signal.filename

        self.ui.lblName.setText(self.signal.name)

        if os.path.isfile(file):
            self.ui.lblFile.setText(file)
            self.ui.lblFileSize.setText(locale.format_string("%.2fMB", os.path.getsize(file) / (1024 ** 2)))
            self.ui.lFileCreated.setText(time.ctime(os.path.getctime(file)))
        else:
            self.ui.lblFile.setText(self.tr("signal file not found"))
            self.ui.lblFileSize.setText("-")
            self.ui.lFileCreated.setText("-")

        self.ui.lblSamplesTotal.setText("{0:n}".format(self.signal.num_samples).replace(",", " "))
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

    def save_signal_as(self):
        filename = FileOperator.get_save_file_name(self.signal.filename, wav_only=self.signal.wav_mode)
        if filename:
            try:
                self.signal.save_as(filename)
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error saving signal"), e.args[0])

                                                            
