import sys
import unittest

import sip
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests import utils_testing
from urh.controller.MessageTypeDialogController import MessageTypeDialogController
from urh.signalprocessing.MessageType import MessageType

utils_testing.write_settings()



class TestMessageTypeOptionsGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)

    def setUp(self):
        self.message_type = MessageType(name="Test")
        self.dialog = MessageTypeDialogController(self.message_type)

    def tearDown(self):
        self.dialog.close()
        QApplication.instance().processEvents()
        QTest.qWait(1)

    def test_message_type_dialog_parameters(self):
        self.assertEqual(self.message_type.name, self.dialog.windowTitle())
        self.assertEqual(self.message_type.assign_manually, not self.dialog.ui.rbAssignAutomatically.isChecked())
        self.assertEqual(self.message_type.assign_manually, self.dialog.ui.rbAssignManually.isChecked())

        self.assertEqual(self.message_type.assign_manually, not self.dialog.ui.btnAddRule.isEnabled())
        self.assertEqual(self.message_type.assign_manually, not self.dialog.ui.btnRemoveRule.isEnabled())
        self.assertEqual(self.message_type.assign_manually, not self.dialog.ui.tblViewRuleset.isEnabled())
        self.assertEqual(self.message_type.assign_manually, not self.dialog.ui.cbRulesetMode.isEnabled())

    def test_edit_rules(self):
        num_rules = len(self.message_type.ruleset)
        self.assertEqual(num_rules, self.dialog.ruleset_table_model.rowCount())
        self.dialog.ui.rbAssignAutomatically.click()
        self.assertFalse(self.message_type.assign_manually)
        self.dialog.ui.rbAssignManually.click()
        self.assertTrue(self.message_type.assign_manually)

        self.dialog.ui.rbAssignAutomatically.click()
        self.assertTrue(self.dialog.ui.btnAddRule.isEnabled())
        self.dialog.ui.btnAddRule.click()
        self.assertEqual(num_rules + 1, len(self.message_type.ruleset))
        self.assertEqual(num_rules + 1, self.dialog.ruleset_table_model.rowCount())

        model = self.dialog.ruleset_table_model
        model.setData(model.index(0, 0), 10, role=Qt.EditRole)
        self.assertEqual(self.message_type.ruleset[0].start, 9)
        model.setData(model.index(0, 1), 20, role=Qt.EditRole)
        self.assertEqual(self.message_type.ruleset[0].end, 20)
        model.setData(model.index(0, 2), 2, role=Qt.EditRole)
        self.assertEqual(self.message_type.ruleset[0].value_type, 2)
        model.setData(model.index(0, 3), 2, role=Qt.EditRole)
        model.setData(model.index(0, 4), "10101", role=Qt.EditRole)
        self.assertEqual(self.message_type.ruleset[0].target_value, "10101")

        for i in range(model.rowCount()):
            for j in range(model.columnCount()):
                self.assertEqual(model.flags(model.index(i, j)), Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

        self.dialog.ui.btnRemoveRule.click()
        self.assertEqual(num_rules, len(self.message_type.ruleset))
        self.assertEqual(num_rules, self.dialog.ruleset_table_model.rowCount())
