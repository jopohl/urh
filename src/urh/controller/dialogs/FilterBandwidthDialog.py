from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog, QLabel, QRadioButton

from urh import settings
from urh.signalprocessing.Filter import Filter
from urh.ui.ui_filter_bandwidth_dialog import Ui_DialogFilterBandwidth


class FilterBandwidthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogFilterBandwidth()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)

        bw_type = settings.read("bandpass_filter_bw_type", "Medium", str)
        custom_bw = settings.read("bandpass_filter_custom_bw", 0.1, float)

        for item in dir(self.ui):
            item = getattr(self.ui, item)
            if isinstance(item, QLabel):
                name = item.objectName().replace("label", "")
                key = next((key for key in Filter.BANDWIDTHS.keys() if name.startswith(key.replace(" ", ""))), None)
                if key is not None and name.endswith("Bandwidth"):
                    item.setText("{0:n}".format(Filter.BANDWIDTHS[key]))
                elif key is not None and name.endswith("KernelLength"):
                    item.setText(str(Filter.get_filter_length_from_bandwidth(Filter.BANDWIDTHS[key])))
            elif isinstance(item, QRadioButton):
                item.setChecked(bw_type.replace(" ", "_") == item.objectName().replace("radioButton", ""))

        self.ui.doubleSpinBoxCustomBandwidth.setValue(custom_bw)
        self.ui.spinBoxCustomKernelLength.setValue(Filter.get_filter_length_from_bandwidth(custom_bw))

        self.create_connects()

    def create_connects(self):
        self.ui.doubleSpinBoxCustomBandwidth.valueChanged.connect(self.on_spin_box_custom_bandwidth_value_changed)
        self.ui.spinBoxCustomKernelLength.valueChanged.connect(self.on_spin_box_custom_kernel_length_value_changed)
        self.ui.buttonBox.accepted.connect(self.on_accepted)

    @property
    def checked_radiobutton(self):
        for rb in dir(self.ui):
            radio_button = getattr(self.ui, rb)
            if isinstance(radio_button, QRadioButton) and radio_button.isChecked():
                return radio_button
        return None

    @pyqtSlot(float)
    def on_spin_box_custom_bandwidth_value_changed(self, bw: float):
        self.ui.spinBoxCustomKernelLength.blockSignals(True)
        self.ui.spinBoxCustomKernelLength.setValue(Filter.get_filter_length_from_bandwidth(bw))
        self.ui.spinBoxCustomKernelLength.blockSignals(False)

    @pyqtSlot(int)
    def on_spin_box_custom_kernel_length_value_changed(self, filter_len: int):
        self.ui.doubleSpinBoxCustomBandwidth.blockSignals(True)
        self.ui.doubleSpinBoxCustomBandwidth.setValue(Filter.get_bandwidth_from_filter_length(filter_len))
        self.ui.doubleSpinBoxCustomBandwidth.blockSignals(False)

    @pyqtSlot()
    def on_accepted(self):
        if self.checked_radiobutton is not None:
            bw_type = self.checked_radiobutton.objectName().replace("radioButton", "").replace("_", " ")
            settings.write("bandpass_filter_bw_type", bw_type)

        settings.write("bandpass_filter_custom_bw", self.ui.doubleSpinBoxCustomBandwidth.value())
