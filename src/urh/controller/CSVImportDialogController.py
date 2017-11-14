import csv

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QInputDialog, QApplication, QTableWidgetItem

from urh.ui.ui_csv_wizard import Ui_DialogCSVImport
from urh.util.Errors import Errors


class CSVImportDialogController(QDialog):
    PREVIEW_ROWS = 100

    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.ui = Ui_DialogCSVImport()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        with open(self.filename, encoding="utf-8-sig") as f:
            self.ui.plainTextEditFilePreview.setPlainText("".join(next(f) for _ in range(self.PREVIEW_ROWS)))

        self.ui.tableWidgetPreview.setColumnHidden(2, True)
        self.update_preview()

        self.create_connects()

    def create_connects(self):
        self.ui.btnAddSeparator.clicked.connect(self.on_btn_add_separator_clicked)
        self.ui.comboBoxCSVSeparator.currentIndexChanged.connect(self.on_combobox_csv_separator_current_index_changed)
        self.ui.spinBoxIDataColumn.valueChanged.connect(self.on_spinbox_i_data_column_value_changed)
        self.ui.spinBoxQDataColumn.valueChanged.connect(self.on_spinbox_q_data_column_value_changed)
        self.ui.spinBoxTimestampColumn.valueChanged.connect(self.on_spinbox_timestamp_value_changed)

    def __is_number(self, number_str: str) -> bool:
        try:
            float(number_str)
            return True
        except:
            return False

    def parse_csv_line(self, csv_line: str, i_data_col: int, q_data_col: int, timestamp_col: int):
        result = dict()

        if i_data_col >= 0:
            try:
                result["I"] = float(csv_line[i_data_col])
            except:
                return None
        else:
            result["I"] = 0.0

        if q_data_col >= 0:
            try:
                result["Q"] = float(csv_line[q_data_col])
            except:
                return None
        else:
            result["Q"] = 0.0

        if timestamp_col >= 0:
            try:
                result["T"] = float(csv_line[timestamp_col])
            except:
                return None

        return result

    def __create_item(self, content):
        item = QTableWidgetItem(str(content))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def update_preview(self):
        i_data_col = self.ui.spinBoxIDataColumn.value() - 1
        q_data_col = self.ui.spinBoxQDataColumn.value() - 1
        timestamp_col = self.ui.spinBoxTimestampColumn.value() - 1

        self.ui.tableWidgetPreview.setRowCount(self.PREVIEW_ROWS)

        table_header_cols = {"I": 0, "Q": 1, "T": 2}

        with open(self.filename, encoding="utf-8-sig") as f:
            csv_reader = csv.reader(f, delimiter=self.ui.comboBoxCSVSeparator.currentText())
            row = -1

            for line in csv_reader:
                row += 1
                result = self.parse_csv_line(line, i_data_col, q_data_col, timestamp_col)
                if result is not None:
                    for key, value in result.items():
                        self.ui.tableWidgetPreview.setItem(row, table_header_cols[key], self.__create_item(value))
                else:
                    for col in table_header_cols.values():
                        self.ui.tableWidgetPreview.setItem(row, col, self.__create_item("Invalid"))

                if row >= self.PREVIEW_ROWS:
                    break

            self.ui.tableWidgetPreview.setRowCount(row)

    @pyqtSlot()
    def on_btn_add_separator_clicked(self):
        sep, ok = QInputDialog.getText(self, "Enter Separator", "Separator:", text=",")
        if ok and sep not in (self.ui.comboBoxCSVSeparator.itemText(i) for i in
                              range(self.ui.comboBoxCSVSeparator.count())):
            if len(sep) == 1:
                self.ui.comboBoxCSVSeparator.addItem(sep)
            else:
                Errors.generic_error("Invalid Separator", "Separator must be exactly one character.")

    @pyqtSlot(int)
    def on_combobox_csv_separator_current_index_changed(self, index: int):
        self.update_preview()

    @pyqtSlot(int)
    def on_spinbox_i_data_column_value_changed(self, index: int):
        self.update_preview()

    @pyqtSlot(int)
    def on_spinbox_q_data_column_value_changed(self, index: int):
        self.update_preview()

    @pyqtSlot(int)
    def on_spinbox_timestamp_value_changed(self, index: int):
        self.ui.tableWidgetPreview.setColumnHidden(2, index == 0)
        self.update_preview()


if __name__ == '__main__':
    app = QApplication(["urh"])
    csv_dia = CSVImportDialogController("/tmp/Agilient-DSO-X-2002A.csv")
    csv_dia.exec_()
