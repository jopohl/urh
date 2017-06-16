from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView

from urh.signalprocessing.CRCLabel import CRCLabel
from urh.ui.ui_crc_options_widget import Ui_CRCOptions


class CRCWidgetController(QWidget):

    def __init__(self, crc_label: CRCLabel, parent=None):
        super().__init__(parent)
        self.ui = Ui_CRCOptions()
        self.ui.setupUi(self)
        self.crc_label = crc_label
        self.display_crc_data_ranges_in_table()
        self.ui.tableWidgetDataRanges.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.create_connects()

    def create_connects(self):
        self.ui.comboBoxCRCFunction.currentIndexChanged.connect(self.on_combobox_crc_function_current_index_changed)
        self.ui.btnAddRange.clicked.connect(self.on_btn_add_range_clicked)
        self.ui.btnRemoveRange.clicked.connect(self.on_btn_remove_range_clicked)

    def display_crc_data_ranges_in_table(self):
        for i, rng in enumerate(self.crc_label.data_ranges):
            if i >= self.ui.tableWidgetDataRanges.rowCount():
                self.ui.tableWidgetDataRanges.insertRow(i)

            self.ui.tableWidgetDataRanges.setItem(i, 0, QTableWidgetItem(str(rng[0])))
            self.ui.tableWidgetDataRanges.setItem(i, 1, QTableWidgetItem(str(rng[1])))

    @pyqtSlot()
    def on_btn_add_range_clicked(self):
        self.ui.tableWidgetDataRanges.insertRow(self.ui.tableWidgetDataRanges.rowCount())

    @pyqtSlot()
    def on_btn_remove_range_clicked(self):
        if self.ui.tableWidgetDataRanges.rowCount() > 1:
            self.ui.tableWidgetDataRanges.removeRow(self.ui.tableWidgetDataRanges.rowCount()-1)

    @pyqtSlot(int)
    def on_combobox_crc_function_current_index_changed(self, index: int):
        print(index)

