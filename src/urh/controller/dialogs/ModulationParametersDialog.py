import math

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QTableWidgetItem

from urh.ui.delegates.KillerSpinBoxDelegate import KillerSpinBoxDelegate
from urh.ui.delegates.SpinBoxDelegate import SpinBoxDelegate
from urh.ui.ui_modulation_parameters_dialog import Ui_DialogModulationParameters


class ModulationParametersDialog(QDialog):
    def __init__(self, parameters: list, modulation_type: str, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogModulationParameters()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Window)

        self.parameters = parameters
        self.num_bits = int(math.log2(len(parameters)))

        if "FSK" in modulation_type:
            self.ui.tblSymbolParameters.setItemDelegateForColumn(
                1, KillerSpinBoxDelegate(-1e12, 1e12, self)
            )
            self.ui.tblSymbolParameters.horizontalHeaderItem(1).setText(
                "Frequency in Hz"
            )
        elif "ASK" in modulation_type:
            self.ui.tblSymbolParameters.horizontalHeaderItem(1).setText("Amplitude")
            self.ui.tblSymbolParameters.setItemDelegateForColumn(
                1, SpinBoxDelegate(0, 100, self, "%")
            )
        elif "PSK" in modulation_type:
            self.ui.tblSymbolParameters.setItemDelegateForColumn(
                1, SpinBoxDelegate(-360, 360, self, "°")
            )
            self.ui.tblSymbolParameters.horizontalHeaderItem(1).setText("Phase")

        fmt = "{0:0" + str(self.num_bits) + "b}"
        self.ui.tblSymbolParameters.setRowCount(len(parameters))
        for i, parameter in enumerate(parameters):
            item = QTableWidgetItem(fmt.format(i))
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setFlags(Qt.ItemIsEnabled)
            self.ui.tblSymbolParameters.setItem(i, 0, item)

            item = QTableWidgetItem()
            item.setData(Qt.DisplayRole, self.parameters[i])
            self.ui.tblSymbolParameters.setItem(i, 1, item)
            self.ui.tblSymbolParameters.openPersistentEditor(
                self.ui.tblSymbolParameters.item(i, 1)
            )

        self.create_connects()

    def create_connects(self):
        self.ui.buttonBox.accepted.connect(self.on_accepted)
        self.ui.buttonBox.rejected.connect(self.reject)

    @pyqtSlot()
    def on_accepted(self):
        for i in range(self.ui.tblSymbolParameters.rowCount()):
            self.parameters[i] = float(self.ui.tblSymbolParameters.item(i, 1).text())

        self.accept()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(["urh"])

    dialog = ModulationParametersDialog([0, 100.0], "ASK")
    dialog.show()

    app.exec_()
