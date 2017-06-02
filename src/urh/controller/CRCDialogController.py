from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from urh.ui.ui_crc_dialog import Ui_DialogCRC


class CRCDialogController(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogCRC()
        self.ui.setupUi(self)
        self.create_connects()

    def create_connects(self):
        self.ui.spinBoxDataStart.valueChanged.connect(self.on_spin_box_data_start_value_changed)
        self.ui.spinBoxDataEnd.valueChanged.connect(self.on_spin_box_data_end_value_changed)
        self.ui.comboBoxCRCFunction.currentIndexChanged.connect(self.on_combobox_crc_function_current_index_changed)

    @pyqtSlot(int)
    def on_spin_box_data_start_value_changed(self, value: int):
        print(value)

    @pyqtSlot(int)
    def on_spin_box_data_end_value_changed(self, value: int):
        print(value)

    @pyqtSlot(int)
    def on_combobox_crc_function_current_index_changed(self, index: int):
        print(index)

