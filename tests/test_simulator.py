import unittest
import tests.utils_testing
from urh import constants
from urh.controller.MainController import MainController
from urh.ui.SimulatorScene import RuleItem

from tests.utils_testing import get_path_for_data_file

app = tests.utils_testing.app


class TestSimulator(unittest.TestCase):
    def setUp(self):
        self.old_sym_len = constants.SETTINGS.value('rel_symbol_length', type=int)
        constants.SETTINGS.setValue('rel_symbol_length', 0)  # Disable Symbols for this Test

        self.form = MainController()
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.sframe = self.form.signal_tab_controller.signal_frames[0]
        self.sim_frame = self.form.simulator_tab_controller
        self.form.ui.tabWidget.setCurrentIndex(3)

    def tearDown(self):
        constants.SETTINGS.setValue('rel_symbol_length', self.old_sym_len) # Restore Symbol Length

    def test_add_signal(self):
        self.sim_frame.ui.gvSimulator.scene().add_protocols([self.sframe.proto_analyzer])
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().items), len(self.sframe.proto_analyzer.messages))

    def test_add_rule(self):
        self.sim_frame.ui.gvSimulator.scene().clear_all()
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().items), 1)
        self.assertEqual(type(self.sim_frame.ui.gvSimulator.scene().items[0]), RuleItem)

    def test_create_context_menu(self):
        self.sim_frame.ui.gvSimulator.scene().clear_all()
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        rule = self.sim_frame.ui.gvSimulator.scene().items[0]
        if_cond = rule.conditions[0]
        menu = if_cond.create_context_menu()
        self.assertIsNone(next((action for action in menu.actions() if action.text() == "Remove else if block"), None))
        self.assertIsNone(next((action for action in menu.actions() if action.text() == "Remove else block"), None))

    def test_select_all(self):
        self.sim_frame.ui.gvSimulator.scene().clear_all()
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        rule = self.sim_frame.ui.gvSimulator.scene().items[0]
        if_cond = rule.conditions[0]
        if_cond.on_add_else_if_cond_action_triggered()
        else_cond = rule.conditions[1]
        #else_cond.on_add_message_action_triggered()
        self.sim_frame.ui.gvSimulator.scene().add_message()
        self.sim_frame.ui.gvSimulator.scene().select_all_items()
        self.assertEqual(if_cond.isSelected(), True)
        self.assertEqual(else_cond.isSelected(), True)
        #self.assertEqual(else_cond.items[0].isSelected(), True)
        self.assertEqual(self.sim_frame.ui.gvSimulator.scene().items[1].isSelected(), True)

    def test_delete_selected_items(self):
        self.sim_frame.ui.gvSimulator.scene().clear_all()
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        rule = self.sim_frame.ui.gvSimulator.scene().items[0]
        if_cond = rule.conditions[0]
        if_cond.on_add_else_cond_action_triggered()
        if_cond.on_add_message_action_triggered()
        if_cond.items[0].setSelected(True)
        else_cond = rule.conditions[1]
        else_cond.setSelected(True)
        self.sim_frame.ui.gvSimulator.scene().add_message()
        self.sim_frame.ui.gvSimulator.scene().items[1].setSelected(True)
        self.sim_frame.ui.gvSimulator.scene().delete_selected_items()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().items), 1)
        self.assertEqual(len(if_cond.items), 0)
        self.assertEqual(len(rule.conditions), 1)
        if_cond.setSelected(True)
        self.sim_frame.ui.gvSimulator.scene().delete_selected_items()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().items), 0)