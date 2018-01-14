import os
import random
import tempfile

from tests.QtTestCase import QtTestCase
from urh.controller.dialogs.CSVImportDialog import CSVImportDialog


class TestCSVImportDialog(QtTestCase):
    def setUp(self):
        super().setUp()
        self.dialog = CSVImportDialog()

        if self.SHOW:
            self.dialog.show()

        self.i_column = self.dialog.COLUMNS["I"]
        self.q_column = self.dialog.COLUMNS["Q"]
        self.t_column = self.dialog.COLUMNS["T"]

    def test_invalid_file(self):
        if self.SHOW:
            self.assertTrue(self.dialog.ui.labelFileNotFound.isVisible())

        self.dialog.ui.lineEditFilename.setText("/this/file/does/not/exist")
        self.dialog.ui.lineEditFilename.editingFinished.emit()
        self.assertEqual(self.dialog.ui.plainTextEditFilePreview.toPlainText(), "")
        self.assertEqual(self.dialog.ui.tableWidgetPreview.rowCount(), 0)

    def test_comma_separated_file(self):
        filename = os.path.join(tempfile.gettempdir(), "comma.csv")
        with open(filename, "w") as f:
            f.write("this is a comment\n")
            f.write("format is\n")
            f.write("Timestamp I Q Trash\n")

            for i in range(150):
                f.write("{},{},{},{}\n".format(i / 1e6, i, random.uniform(0, 1), 42 * i))

        self.dialog.ui.lineEditFilename.setText(filename)
        self.dialog.ui.lineEditFilename.editingFinished.emit()

        self.dialog.ui.spinBoxIDataColumn.setValue(2)
        self.dialog.ui.spinBoxTimestampColumn.setValue(1)
        self.dialog.ui.spinBoxQDataColumn.setValue(3)

        for i in range(3):
            for j in range(3):
                self.assertEqual(self.dialog.ui.tableWidgetPreview.item(i, j).text(), "Invalid")

        file_preview = self.dialog.ui.plainTextEditFilePreview.toPlainText()
        self.assertEqual(len(file_preview.split("\n")), 100)

        self.assertEqual(self.dialog.ui.tableWidgetPreview.rowCount(), 100)
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(3, self.i_column).text(), "0.0")
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(99, self.i_column).text(), "96.0")

        last_preview_line = file_preview.split("\n")[-1]
        t, i, q, _ = map(float, last_preview_line.split(","))
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(99, self.i_column).text(), str(i))
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(99, self.q_column).text(), str(q))
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(99, self.t_column).text(), str(t))

    def test_semicolon_separated_file(self):
        filename = os.path.join(tempfile.gettempdir(), "semicolon.csv")
        with open(filename, "w") as f:
            f.write("I;Trash\n")

            for i in range(20):
                f.write("{};{}\n".format(i, 24 * i))

        self.dialog.ui.lineEditFilename.setText(filename)
        self.dialog.ui.lineEditFilename.editingFinished.emit()
        self.dialog.ui.comboBoxCSVSeparator.setCurrentText(";")

        self.assertTrue(self.dialog.ui.tableWidgetPreview.isColumnHidden(self.t_column))
        self.assertEqual(self.dialog.ui.tableWidgetPreview.rowCount(), 21)
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(0, self.i_column).text(), "Invalid")
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(0, self.q_column).text(), "Invalid")
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(1, self.i_column).text(), "0.0")
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(1, self.q_column).text(), "0.0")
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(2, self.i_column).text(), "1.0")
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(2, self.q_column).text(), "0.0")

        file_preview = self.dialog.ui.plainTextEditFilePreview.toPlainText()
        last_preview_line = file_preview.split("\n")[-1]
        i, _ = map(float, last_preview_line.split(";"))
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(20, self.i_column).text(), str(i))
        self.assertEqual(self.dialog.ui.tableWidgetPreview.item(20, self.q_column).text(), "0.0")
