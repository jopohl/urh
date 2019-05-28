from PySide2.QtCore import Slot, Signal, Qt
from PySide2.QtWidgets import QDialog

from urh.ui.ui_advanced_modulation_settings import Ui_DialogAdvancedModSettings


class AdvancedModulationOptionsDialog(QDialog):
    pause_threshold_edited = Signal(int)
    message_length_divisor_edited = Signal(int)

    def __init__(self, pause_threshold: int, message_length_divisor: int, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogAdvancedModSettings()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window)

        self.pause_threshold = pause_threshold
        self.message_length_divisor = message_length_divisor

        self.ui.spinBoxPauseThreshold.setValue(pause_threshold)
        self.ui.spinBoxMessageLengthDivisor.setValue(message_length_divisor)

        self.create_connects()

    def create_connects(self):
        self.ui.buttonBox.accepted.connect(self.on_accept_clicked)
        self.ui.buttonBox.rejected.connect(self.reject)

    @Slot()
    def on_accept_clicked(self):
        if self.pause_threshold != self.ui.spinBoxPauseThreshold.value():
            self.pause_threshold_edited.emit(self.ui.spinBoxPauseThreshold.value())

        if self.message_length_divisor != self.ui.spinBoxMessageLengthDivisor.value():
            self.message_length_divisor_edited.emit(self.ui.spinBoxMessageLengthDivisor.value())

        self.accept()
