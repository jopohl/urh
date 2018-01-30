import csv

import os
import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog, QInputDialog, QApplication, QCompleter, QDirModel, QFileDialog

from urh.ui.ui_csv_wizard import Ui_DialogCSVImport
from urh.util import FileOperator, util
from urh.util.Errors import Errors


class CSVImportDialog(QDialog):
    data_imported = pyqtSignal(str, float)  # Complex Filename + Sample Rate


    PREVIEW_ROWS = 100
    COLUMNS = {"T": 0, "I": 1, "Q": 2}

    def __init__(self, filename="", parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogCSVImport()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui.btnAutoDefault.hide()

        completer = QCompleter()
        completer.setModel(QDirModel(completer))
        self.ui.lineEditFilename.setCompleter(completer)

        self.filename = None  # type: str
        self.ui.lineEditFilename.setText(filename)
        self.update_file()

        self.ui.tableWidgetPreview.setColumnHidden(self.COLUMNS["T"], True)
        self.update_preview()

        self.create_connects()

    def create_connects(self):
        self.accepted.connect(self.on_accepted)
        self.ui.lineEditFilename.editingFinished.connect(self.on_line_edit_filename_editing_finished)
        self.ui.btnChooseFile.clicked.connect(self.on_btn_choose_file_clicked)
        self.ui.btnAddSeparator.clicked.connect(self.on_btn_add_separator_clicked)
        self.ui.comboBoxCSVSeparator.currentIndexChanged.connect(self.on_combobox_csv_separator_current_index_changed)
        self.ui.spinBoxIDataColumn.valueChanged.connect(self.on_spinbox_i_data_column_value_changed)
        self.ui.spinBoxQDataColumn.valueChanged.connect(self.on_spinbox_q_data_column_value_changed)
        self.ui.spinBoxTimestampColumn.valueChanged.connect(self.on_spinbox_timestamp_value_changed)

    def update_file(self):
        filename = self.ui.lineEditFilename.text()
        self.filename = filename

        enable = util.file_can_be_opened(filename)
        if enable:
            with open(self.filename, encoding="utf-8-sig") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= self.PREVIEW_ROWS:
                        break
                    lines.append(line.strip())
                self.ui.plainTextEditFilePreview.setPlainText("\n".join(lines))
        else:
            self.ui.plainTextEditFilePreview.clear()

        self.ui.plainTextEditFilePreview.setEnabled(enable)
        self.ui.comboBoxCSVSeparator.setEnabled(enable)
        self.ui.spinBoxIDataColumn.setEnabled(enable)
        self.ui.spinBoxQDataColumn.setEnabled(enable)
        self.ui.spinBoxTimestampColumn.setEnabled(enable)
        self.ui.tableWidgetPreview.setEnabled(enable)
        self.ui.labelFileNotFound.setVisible(not enable)

    def update_preview(self):
        if not util.file_can_be_opened(self.filename):
            self.update_file()
            return

        i_data_col = self.ui.spinBoxIDataColumn.value() - 1
        q_data_col = self.ui.spinBoxQDataColumn.value() - 1
        timestamp_col = self.ui.spinBoxTimestampColumn.value() - 1

        self.ui.tableWidgetPreview.setRowCount(self.PREVIEW_ROWS)

        with open(self.filename, encoding="utf-8-sig") as f:
            csv_reader = csv.reader(f, delimiter=self.ui.comboBoxCSVSeparator.currentText())
            row = -1

            for line in csv_reader:
                row += 1
                result = self.parse_csv_line(line, i_data_col, q_data_col, timestamp_col)
                if result is not None:
                    for key, value in result.items():
                        self.ui.tableWidgetPreview.setItem(row, self.COLUMNS[key], util.create_table_item(value))
                else:
                    for col in self.COLUMNS.values():
                        self.ui.tableWidgetPreview.setItem(row, col, util.create_table_item("Invalid"))

                if row >= self.PREVIEW_ROWS - 1:
                    break

            self.ui.tableWidgetPreview.setRowCount(row + 1)

    @staticmethod
    def parse_csv_line(csv_line: str, i_data_col: int, q_data_col: int, timestamp_col: int):
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

    @staticmethod
    def parse_csv_file(filename: str, separator: str, i_data_col: int, q_data_col=-1, t_data_col=-1):
        iq_data = []
        timestamps = [] if t_data_col > -1 else None
        with open(filename, encoding="utf-8-sig") as f:
            csv_reader = csv.reader(f, delimiter=separator)
            for line in csv_reader:
                parsed = CSVImportDialog.parse_csv_line(line, i_data_col, q_data_col, t_data_col)
                if parsed is None:
                    continue

                iq_data.append(complex(parsed["I"], parsed["Q"]))
                if timestamps is not None:
                    timestamps.append(parsed["T"])

        iq_data = np.asarray(iq_data, dtype=np.complex64)
        sample_rate = CSVImportDialog.estimate_sample_rate(timestamps)
        return iq_data / abs(iq_data.max()), sample_rate

    @staticmethod
    def estimate_sample_rate(timestamps):
        if timestamps is None or len(timestamps) < 2:
            return None

        previous_timestamp = timestamps[0]
        durations = []

        for timestamp in timestamps[1:CSVImportDialog.PREVIEW_ROWS]:
            durations.append(abs(timestamp-previous_timestamp))
            previous_timestamp = timestamp

        return 1 / (sum(durations) / len(durations))

    @pyqtSlot()
    def on_line_edit_filename_editing_finished(self):
        self.update_file()
        self.update_preview()

    @pyqtSlot()
    def on_btn_choose_file_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("Choose file"), directory=FileOperator.RECENT_PATH,
                                                  filter="CSV files (*.csv);;All files (*.*)")

        if filename:
            self.ui.lineEditFilename.setText(filename)
            self.ui.lineEditFilename.editingFinished.emit()

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
    def on_spinbox_i_data_column_value_changed(self, value: int):
        self.update_preview()

    @pyqtSlot(int)
    def on_spinbox_q_data_column_value_changed(self, value: int):
        self.update_preview()

    @pyqtSlot(int)
    def on_spinbox_timestamp_value_changed(self, value: int):
        self.ui.tableWidgetPreview.setColumnHidden(self.COLUMNS["T"], value == 0)
        self.update_preview()

    @pyqtSlot()
    def on_accepted(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        iq_data, sample_rate = self.parse_csv_file(self.filename, self.ui.comboBoxCSVSeparator.currentText(),
                                                   self.ui.spinBoxIDataColumn.value()-1,
                                                   self.ui.spinBoxQDataColumn.value()-1,
                                                   self.ui.spinBoxTimestampColumn.value()-1)

        target_filename = self.filename.rstrip(".csv")
        if os.path.exists(target_filename + ".complex"):
            i = 1
            while os.path.exists(target_filename + "_" + str(i) + ".complex"):
                i += 1
        else:
            i = None

        target_filename = target_filename if not i else target_filename + "_" + str(i)
        target_filename += ".complex"

        iq_data.tofile(target_filename)

        self.data_imported.emit(target_filename, sample_rate if sample_rate is not None else 0)
        QApplication.restoreOverrideCursor()

if __name__ == '__main__':
    app = QApplication(["urh"])
    csv_dia = CSVImportDialog()
    csv_dia.exec_()
