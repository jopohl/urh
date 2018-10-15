from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog

from urh.signalprocessing.Filter import Filter, FilterType
from urh.ui.ui_filter_dialog import Ui_FilterDialog


class FilterDialog(QDialog):
    filter_accepted = pyqtSignal(Filter)

    def __init__(self, dsp_filter: Filter, parent=None):
        super().__init__(parent)
        self.ui = Ui_FilterDialog()
        self.ui.setupUi(self)

        self.error_message = ""

        self.set_dsp_filter_status(dsp_filter.filter_type)
        self.create_connects()

    def set_dsp_filter_status(self, dsp_filter_type: FilterType):
        if dsp_filter_type == FilterType.moving_average:
            self.ui.radioButtonMovingAverage.setChecked(True)
            self.ui.lineEditCustomTaps.setEnabled(False)
            self.ui.spinBoxNumTaps.setEnabled(True)
        elif dsp_filter_type == FilterType.dc_correction:
            self.ui.radioButtonDCcorrection.setChecked(True)
            self.ui.lineEditCustomTaps.setEnabled(False)
            self.ui.spinBoxNumTaps.setEnabled(False)
        else:
            self.ui.radioButtonCustomTaps.setChecked(True)
            self.ui.spinBoxNumTaps.setEnabled(True)
            self.ui.lineEditCustomTaps.setEnabled(True)

    def create_connects(self):
        self.ui.radioButtonMovingAverage.clicked.connect(self.on_radio_button_moving_average_clicked)
        self.ui.radioButtonCustomTaps.clicked.connect(self.on_radio_button_custom_taps_clicked)
        self.ui.radioButtonDCcorrection.clicked.connect(self.on_radio_button_dc_correction_clicked)

        self.ui.spinBoxNumTaps.valueChanged.connect(self.set_error_status)
        self.ui.lineEditCustomTaps.textEdited.connect(self.set_error_status)
        self.ui.buttonBox.accepted.connect(self.on_accept_clicked)
        self.ui.buttonBox.rejected.connect(self.reject)

    def build_filter(self) -> Filter:
        if self.ui.radioButtonMovingAverage.isChecked():
            n = self.ui.spinBoxNumTaps.value()
            return Filter([1/n for _ in range(n)], filter_type=FilterType.moving_average)
        elif self.ui.radioButtonDCcorrection.isChecked():
            return Filter([], filter_type=FilterType.dc_correction)
        else:
            # custom filter
            try:
                taps = eval(self.ui.lineEditCustomTaps.text())
                try:
                    taps = list(map(float, taps))
                    self.error_message = ""
                    return Filter(taps)
                except (ValueError, TypeError) as e:
                    self.error_message = "Error casting taps:\n" + str(e)
                    return None

            except SyntaxError as e:
                self.error_message = "Error parsing taps:\n" + str(e)
                return None

    def set_error_status(self):
        dsp_filter = self.build_filter()
        if dsp_filter is None:
            self.ui.lineEditCustomTaps.setStyleSheet("background: red")
            self.ui.lineEditCustomTaps.setToolTip(self.error_message)
        elif len(dsp_filter.taps) != self.ui.spinBoxNumTaps.value():
            self.ui.lineEditCustomTaps.setStyleSheet("background: yellow")
            self.ui.lineEditCustomTaps.setToolTip("The number of the filter taps does not match the configured number of taps. I will use your configured filter taps.")
        else:
            self.ui.lineEditCustomTaps.setStyleSheet("")
            self.ui.lineEditCustomTaps.setToolTip("")

    @pyqtSlot(bool)
    def on_radio_button_moving_average_clicked(self, checked: bool):
        if checked:
            self.set_dsp_filter_status(FilterType.moving_average)

    @pyqtSlot(bool)
    def on_radio_button_custom_taps_clicked(self, checked: bool):
        if checked:
            self.set_dsp_filter_status(FilterType.custom)
            self.set_error_status()

    @pyqtSlot(bool)
    def on_radio_button_dc_correction_clicked(self, checked: bool):
        if checked:
            self.set_dsp_filter_status(FilterType.dc_correction)

    @pyqtSlot()
    def on_accept_clicked(self):
        dsp_filter = self.build_filter()
        self.filter_accepted.emit(dsp_filter)
        self.accept()
