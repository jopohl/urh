import locale
import os
import time

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog

from urh import settings
from urh.ui.ui_signal_details import Ui_SignalDetails
from urh.util.Formatter import Formatter


class SignalDetailsDialog(QDialog):
    def __init__(self, signal, parent=None):
        super().__init__(parent)
        self.signal = signal
        self.ui = Ui_SignalDetails()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window)

        file = self.signal.filename

        self.ui.lblName.setText(self.signal.name)

        if os.path.isfile(file):
            self.ui.lblFile.setText(file)
            self.ui.lblFileSize.setText(
                locale.format_string("%.2fMB", os.path.getsize(file) / (1024**2))
            )
            self.ui.lFileCreated.setText(time.ctime(os.path.getctime(file)))
        else:
            self.ui.lblFile.setText(self.tr("signal file not found"))
            self.ui.lblFileSize.setText("-")
            self.ui.lFileCreated.setText("-")

        self.ui.lblSamplesTotal.setText(
            "{0:n}".format(self.signal.num_samples).replace(",", " ")
        )
        self.ui.dsb_sample_rate.setValue(self.signal.sample_rate)
        self.set_duration()

        self.ui.dsb_sample_rate.valueChanged.connect(
            self.on_dsb_sample_rate_value_changed
        )
        self.restoreGeometry(
            settings.read("{}/geometry".format(self.__class__.__name__), type=bytes)
        )

    def closeEvent(self, event: QCloseEvent):
        settings.write(
            "{}/geometry".format(self.__class__.__name__), self.saveGeometry()
        )
        super().closeEvent(event)

    @pyqtSlot(float)
    def on_dsb_sample_rate_value_changed(self, value: float):
        self.signal.sample_rate = value
        self.set_duration()

    def set_duration(self):
        dur = self.signal.num_samples / self.signal.sample_rate
        self.ui.lDuration.setText(Formatter.science_time(dur))
