from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog

from urh.ui.ui_costa import Ui_DialogCosta


class CostaOptionsDialog(QDialog):
    def __init__(self, loop_bandwidth, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogCosta()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window)

        self.costas_loop_bandwidth = loop_bandwidth
        self.ui.doubleSpinBoxLoopBandwidth.setValue(self.costas_loop_bandwidth)

        self.create_connects()

    def create_connects(self):
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.doubleSpinBoxLoopBandwidth.valueChanged.connect(
            self.on_spinbox_loop_bandwidth_value_changed
        )

    @pyqtSlot(float)
    def on_spinbox_loop_bandwidth_value_changed(self, value):
        self.costas_loop_bandwidth = value
