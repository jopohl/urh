import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

import tests.utils_testing
from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.controller.MainController import MainController
from urh.util.Logger import logger

app = tests.utils_testing.get_app()


class TestLabels(unittest.TestCase):
    def setUp(self):
        self.old_sym_len = constants.SETTINGS.value('rel_symbol_length', type=int)
        constants.SETTINGS.setValue('rel_symbol_length', 0) # Disable Symbols for this Test

        logger.debug("Init form")
        self.form = MainController()
        logger.debug("Intiliazed form")
        app.processEvents()
        logger.debug("Add signal")
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        logger.debug("Added signal")
        self.sframe = self.form.signal_tab_controller.signal_frames[0]
        self.cframe = self.form.compare_frame_controller
        self.cframe.ui.cbProtoView.setCurrentIndex(0)
        self.gframe = self.form.generator_tab_controller
        self.gframe.ui.cbViewType.setCurrentIndex(0)

        # Create two labels on Compare Frame
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.cframe.add_protocol_label(start=0, end=40, messagenr=1, proto_view=0, edit_label_name = False)  # Sync
        self.cframe.add_protocol_label(start=43, end=43, messagenr=2, proto_view=0, edit_label_name = False)  # FuzzBit

        self.assertEqual(len(self.cframe.active_message_type), 2)

    def tearDown(self):
        self.form.close_all()
        tests.utils_testing.short_wait()

    def test_show_labels_only(self):
        self.cframe.ui.chkBoxOnlyShowLabelsInProtocol.setChecked(True)
        for i in range(0, 40):
            self.assertFalse(self.cframe.ui.tblViewProtocol.isColumnHidden(i), msg = "Bit " + str(i))
        self.assertFalse(self.cframe.ui.tblViewProtocol.isColumnHidden(43), msg = "Bit 43")
        for i in range(44, self.cframe.protocol_model.col_count):
            self.assertTrue(self.cframe.ui.tblViewProtocol.isColumnHidden(i), msg = "Bit " + str(i))

        self.cframe.ui.cbProtoView.setCurrentIndex(1)  # Hex View
        for i in range(0, 10):
            self.assertFalse(self.cframe.ui.tblViewProtocol.isColumnHidden(i), msg = "Hex " + str(i))
        for i in range(13, self.cframe.protocol_model.col_count):
            self.assertTrue(self.cframe.ui.tblViewProtocol.isColumnHidden(i), msg = "Hex " + str(i))

    def test_generator_label(self):
        labels = self.cframe.proto_analyzer.protocol_labels
        self.assertEqual(len(labels), 2)

        # Open Protocol in Generator
        self.form.ui.tabWidget.setCurrentIndex(2)
        item = self.gframe.tree_model.rootItem.children[0].children[0]
        index = self.gframe.tree_model.createIndex(0, 0, item)
        rect = self.gframe.ui.treeProtocols.visualRect(index)
        self.assertEqual(len(self.gframe.ui.treeProtocols.selectedIndexes()), 0)
        QTest.mousePress(self.gframe.ui.treeProtocols.viewport(), Qt.LeftButton, pos=rect.center())
        self.assertEqual(self.gframe.ui.treeProtocols.selectedIndexes()[0], index)
        mimedata = self.gframe.tree_model.mimeData(self.gframe.ui.treeProtocols.selectedIndexes())
        self.gframe.table_model.dropMimeData(mimedata, 1, -1, -1, self.gframe.table_model.createIndex(0, 0))
        self.assertEqual(self.gframe.table_model.row_count, 3)

        # Check Label in Generator
        labels = self.gframe.table_model.protocol.protocol_labels
        self.assertEqual(len(labels), 2)

        # Fuzz Label
        lbl = self.gframe.table_model.protocol.messages[0].message_type[1]
        lbl.fuzz_values.append("1")
        lbl.add_fuzz_value()
        lbl.add_fuzz_value()
        lbl.add_fuzz_value()
        lbl.add_fuzz_value()
        lbl.fuzz_me = Qt.Checked
        self.assertEqual(len(lbl.fuzz_values), 5)
        self.gframe.refresh_label_list()
        self.gframe.refresh_table()
        self.gframe.ui.btnFuzz.setEnabled(True)
        self.gframe.ui.btnFuzz.click()
        self.assertTrue(lbl.active_fuzzing)
        self.assertIn(lbl, self.gframe.table_model.protocol.messages[0].message_type)
        self.assertEqual(self.gframe.table_model.row_count, 4 + 3)

        # Check if Background for fuzzed labels is drawn correctly
        self.__check_background_is_drawn(lbl, 43, 43)

        # Delete a line
        old_row_count = self.gframe.table_model.row_count
        self.gframe.ui.tableMessages.selectRow(2)
        QTest.keyClick(self.gframe.ui.tableMessages, Qt.Key_Delete)
        self.assertEqual(self.gframe.table_model.row_count, old_row_count - 1)

        self.__check_background_is_drawn(lbl, 43, 43)

        # Remove everything
        for i in range(old_row_count):
            self.gframe.ui.tableMessages.selectRow(0)
            QTest.keyClick(self.gframe.ui.tableMessages, Qt.Key_Delete)

        self.assertEqual(self.gframe.table_model.row_count, 0)

    def __check_background_is_drawn(self, lbl, lbl_start, lbl_end):
        pac = self.gframe.table_model.protocol
        for i in range(self.gframe.table_model.row_count):
            labels_for_message = pac.messages[i].message_type
            self.assertIn(lbl, labels_for_message)
            start, end = pac.messages[i].get_label_range(lbl, self.gframe.table_model.proto_view, False)
            self.assertEqual(start, lbl_start)
            self.assertEqual(end, lbl_end + 1)
