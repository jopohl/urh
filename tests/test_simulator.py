import unittest
import tests.utils_testing
from urh import constants
from urh.controller.MainController import MainController
from urh.ui.SimulatorScene import RuleItem

from PyQt5.QtWidgets import QMenu

from tests.utils_testing import get_path_for_data_file

app = tests.utils_testing.app


class TestSimulator(unittest.TestCase):
    def setUp(self):
        self.old_sym_len = constants.SETTINGS.value('rel_symbol_length', type=int)
        constants.SETTINGS.setValue('rel_symbol_length', 0)  # Disable Symbols for this Test

        self.form = MainController()
        self.cfc = self.form.compare_frame_controller
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.sframe = self.form.signal_tab_controller.signal_frames[0]
        self.sim_frame = self.form.simulator_tab_controller
        self.form.ui.tabWidget.setCurrentIndex(3)
        self.cfc.proto_analyzer.auto_assign_labels()

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
        message_type_menu = menu.findChildren(QMenu)[0]
        default_msg_type_action = next(action for action in message_type_menu.actions() if action.text().startswith("default"))
        default_msg_type_action.trigger()
        self.assertEqual(len(if_cond.items), 1)

        menu = if_cond.create_context_menu()
        add_else_if_cond_action = next(action for action in menu.actions() if action.text().startswith("Add else if block"))
        add_else_if_cond_action.trigger()
        self.assertEqual(len(rule.conditions), 2)

        menu = if_cond.create_context_menu()
        add_else_cond_action = next(action for action in menu.actions() if action.text().startswith("Add else block"))
        add_else_cond_action.trigger()
        self.assertEqual(len(rule.conditions), 3)

        else_if_cond = rule.conditions[1]
        menu = else_if_cond.create_context_menu()
        remove_else_if_cond_action = next(action for action in menu.actions() if action.text().startswith("Remove else if block"))
        remove_else_if_cond_action.trigger()
        self.assertEqual(len(rule.conditions), 2)

        else_cond = rule.conditions[1]
        menu = else_cond.create_context_menu()
        remove_else_cond_action = next(action for action in menu.actions() if action.text().startswith("Remove else block"))
        remove_else_cond_action.trigger()
        self.assertEqual(len(rule.conditions), 1)

        menu = if_cond.create_context_menu()
        remove_rule_action = next(action for action in menu.actions() if action.text().startswith("Remove rule"))
        remove_rule_action.trigger()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().items), 0)

    def test_select_all(self):
        self.sim_frame.ui.gvSimulator.scene().clear_all()
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        rule = self.sim_frame.ui.gvSimulator.scene().items[0]
        if_cond = rule.conditions[0]
        menu = if_cond.create_context_menu()
        add_else_if_cond_action = next(action for action in menu.actions() if action.text().startswith("Add else if block"))
        add_else_if_cond_action.trigger()
        else_if_cond = rule.conditions[1]
        self.sim_frame.ui.gvSimulator.scene().add_message()
        self.sim_frame.ui.gvSimulator.scene().select_all_items()
        self.assertEqual(if_cond.isSelected(), True)
        self.assertEqual(else_if_cond.isSelected(), True)
        self.assertEqual(self.sim_frame.ui.gvSimulator.scene().items[1].isSelected(), True)

    def test_delete_selected_items(self):
        self.sim_frame.ui.gvSimulator.scene().clear_all()
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        rule = self.sim_frame.ui.gvSimulator.scene().items[0]
        if_cond = rule.conditions[0]
        if_cond.on_add_else_cond_action_triggered()
        menu = if_cond.create_context_menu()
        add_message_action = next(action for action in menu.actions() if action.text().startswith("Add empty message"))
        add_message_action.trigger()
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