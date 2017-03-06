import unittest

from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

import tests.utils_testing
from urh import constants
from urh.controller.MainController import MainController

from tests.utils_testing import get_path_for_data_file

app = tests.utils_testing.app


class TestAnalysisTabGUI(unittest.TestCase):
    def setUp(self):
        constants.SETTINGS.setValue("not_show_close_dialog", True)  # prevent interactive close questions
        self.form = MainController()
        self.cfc = self.form.compare_frame_controller
        self.form.add_signalfile(get_path_for_data_file("two_participants.complex"))
        self.signal = self.form.signal_tab_controller.signal_frames[0].signal
        self.signal.noise_threshold = 0.0175
        self.signal.qad_center = 0
        self.signal.bit_len = 100
        self.signal.tolerance = 5

    def test_analyze_button_fsk(self):
        self.form.add_signalfile(get_path_for_data_file("fsk.complex"))
        self.cfc.ui.btnAnalyze.click()
        self.assertTrue(True)

    def test_analyze_button_enocean(self):
        self.form.add_signalfile(get_path_for_data_file("enocean.complex"))
        w = self.form.signal_tab_controller.signal_frames[1].ui.spinBoxCenterOffset
        w.setValue(0)
        QTest.keyClick(w, Qt.Key_Enter)
        w = self.form.signal_tab_controller.signal_frames[1].ui.spinBoxNoiseTreshold
        w.setValue(0.0111)
        QTest.keyClick(w, Qt.Key_Enter)
        self.cfc.ui.btnAnalyze.click()
        self.assertTrue(True)

    def test_table_selection(self):
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.cfc.ui.cbProtoView.setCurrentIndex(0)
        self.cfc.ui.btnAnalyze.click()

        self.cfc.ui.tblViewProtocol.selectRow(1)
        app.processEvents()
        self.assertEqual(self.cfc.ui.lBitsSelection.text(), self.cfc.proto_analyzer.messages[1].plain_bits_str)

        self.cfc.ui.tblViewProtocol.clearSelection()
        app.processEvents()
        self.assertEqual("", self.cfc.ui.lBitsSelection.text())

        self.cfc.ui.tblViewProtocol.select(0, 0, 0, 3)
        app.processEvents()
        self.assertEqual("1010", self.cfc.ui.lBitsSelection.text())
        self.cfc.ui.cbProtoView.setCurrentIndex(1)
        min_row, max_row, start, end = self.cfc.ui.tblViewProtocol.selection_range()
        self.assertEqual(min_row, 0)
        self.assertEqual(max_row, 0)
        self.assertEqual(start, 0)
        self.assertEqual(end, 1)

    def test_search(self):
        search_str = "100110001"
        self.cfc.ui.cbProtoView.setCurrentIndex(0)
        self.cfc.ui.tblViewProtocol.clearSelection()
        self.cfc.ui.lineEditSearch.setText(search_str)
        self.cfc.ui.btnSearchSelectFilter.click()

        selected_now = self.cfc.ui.tblViewProtocol.selectedIndexes()
        self.assertEqual(len(self.cfc.ui.tblViewProtocol.selectedIndexes()), len(search_str))

        self.cfc.ui.btnNextSearch.click()
        self.assertNotEqual(selected_now, self.cfc.ui.tblViewProtocol.selectedIndexes())

        self.cfc.ui.btnPrevSearch.click()
        self.assertEqual(selected_now, self.cfc.ui.tblViewProtocol.selectedIndexes())

        self.cfc.select_action.trigger()
        self.assertEqual(self.cfc.ui.btnSearchSelectFilter.text(), "Select all")
        self.cfc.ui.btnSearchSelectFilter.click()
        self.assertGreater(len(self.cfc.ui.tblViewProtocol.selectedIndexes()), len(selected_now))

        self.cfc.filter_action.trigger()
        self.assertEqual(self.cfc.ui.btnSearchSelectFilter.text(), "Filter")
        self.cfc.ui.btnSearchSelectFilter.click()
        hidden_rows = [i for i in range(self.cfc.protocol_model.row_count)
                       if self.cfc.ui.tblViewProtocol.isRowHidden(i)]

        self.assertEqual(hidden_rows, [0, 5, 6, 10, 13, 14, 16, 17])

    def test_show_diff(self):
        hidden_columns_before = [i for i in range(self.cfc.protocol_model.col_count)
                                 if self.cfc.ui.tblViewProtocol.isColumnHidden(i)]
        self.assertEqual(len(hidden_columns_before), 0)

        self.cfc.ui.chkBoxShowOnlyDiffs.click()
        self.assertTrue(self.cfc.ui.cbShowDiffs.isChecked())

        hidden_columns_now = [i for i in range(self.cfc.protocol_model.col_count)
                              if self.cfc.ui.tblViewProtocol.isColumnHidden(i)]

        self.assertNotEqual(hidden_columns_before, hidden_columns_now)

        self.cfc.ui.chkBoxOnlyShowLabelsInProtocol.click()

        hidden_columns_now = [i for i in range(self.cfc.protocol_model.col_count)
                              if self.cfc.ui.tblViewProtocol.isColumnHidden(i)]

        self.assertEqual(len(hidden_columns_now), self.cfc.protocol_model.col_count)

    def test_add_message_type(self):
        self.assertEqual(len(self.cfc.proto_analyzer.message_types), 1)
        self.cfc.ui.btnAddMessagetype.click()
        self.assertEqual(len(self.cfc.proto_analyzer.message_types), 2)

    def test_create_context_menu(self):
        # Add protocol label should be disabled if table is empty
        self.form.close_all()
        app.processEvents()
        QTest.qWait(300)
        self.assertEqual(self.cfc.protocol_model.rowCount(), 0)
        self.cfc.ui.tblViewProtocol.context_menu_pos = QPoint(0, 0)
        menu = self.cfc.ui.tblViewProtocol.create_context_menu()

        create_label_action = next(a for a in menu.actions() if a.text() == "Add protocol label")
        self.assertFalse(create_label_action.isEnabled())

    def test_show_in_interpretation(self):
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.assertEqual(self.form.ui.tabWidget.currentIndex(), 1)
        self.cfc.ui.cbProtoView.setCurrentIndex(0)

        self.cfc.ui.tblViewProtocol.selectRow(1)
        min_row, max_row, start, end = self.cfc.ui.tblViewProtocol.selection_range()
        self.cfc.ui.tblViewProtocol.show_interpretation_clicked.emit(min_row, max_row, start, end - 1)
        self.assertEqual(self.form.ui.tabWidget.currentIndex(), 0)

    def test_hide_row(self):
        num_messages = len(self.cfc.proto_analyzer.messages)
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.assertGreater(num_messages, 0)
        self.assertEqual(self.cfc.protocol_model.rowCount(), num_messages)
        self.cfc.ui.tblViewProtocol.hide_row(0)
        self.assertTrue(self.cfc.ui.tblViewProtocol.isRowHidden(0))
        self.assertEqual(len(self.cfc.protocol_model.hidden_rows), 1)

        for msg in range(1, num_messages):
            self.assertFalse(self.cfc.ui.tblViewProtocol.isRowHidden(msg))

        self.form.ui.tabWidget.setCurrentIndex(2)
        app.processEvents()
        QTest.qWait(100)
        self.form.ui.tabWidget.setCurrentIndex(1)
        app.processEvents()
        QTest.qWait(100)
        self.assertEqual(self.cfc.protocol_model.rowCount(), num_messages)
        self.assertTrue(self.cfc.ui.tblViewProtocol.isRowHidden(0))

        for msg in range(1, num_messages):
            self.assertFalse(self.cfc.ui.tblViewProtocol.isRowHidden(msg))

        self.assertEqual(len(self.cfc.protocol_model.hidden_rows), 1)

