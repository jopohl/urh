import unittest
import tests.utils_testing
from urh import constants
from urh.controller.MainController import MainController
from urh.ui.SimulatorScene import RuleItem
from urh.ui.SimulatorScene import ParticipantItem

from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.Message import Message

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
        self.sim_frame.ui.gvSimulator.scene().add_protocols(None, 0, [self.sframe.proto_analyzer])
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().sim_items), len(self.sframe.proto_analyzer.messages))

    def test_add_rule(self):
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().sim_items), 1)
        self.assertEqual(type(self.sim_frame.ui.gvSimulator.scene().sim_items[0]), RuleItem)

    def test_message_context_menu(self):
        self.sim_frame.ui.gvSimulator.scene().add_message(None, 0)
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        rule = self.sim_frame.ui.gvSimulator.scene().sim_items[1]
        if_cond = rule.conditions[0]
        menu = if_cond.create_context_menu()
        add_message_action = next(action for action in menu.actions() if action.text() == "Add empty message")
        add_message_action.trigger()
        self.assertEqual(len(rule.conditions), 1)
        self.assertEqual(len(if_cond.sim_items), 1)

        part_a = ParticipantItem("A")
        self.sim_frame.ui.gvSimulator.scene().participants.append(part_a)
        self.sim_frame.ui.gvSimulator.scene().addItem(part_a)

        part_b = ParticipantItem("B")
        self.sim_frame.ui.gvSimulator.scene().participants.append(part_b)
        self.sim_frame.ui.gvSimulator.scene().addItem(part_b)

        message = self.sim_frame.ui.gvSimulator.scene().sim_items[0]
        menu = message.create_context_menu()
        source_menu = menu.findChildren(QMenu)[0]
        a_part_action = next(action for action in source_menu.actions() if action.text() == "A")
        a_part_action.trigger()
        self.assertEqual(message.source, part_a)

        menu = message.create_context_menu()
        destination_menu = menu.findChildren(QMenu)[1]
        b_part_action = next(action for action in destination_menu.actions() if action.text() == "B")
        b_part_action.trigger()
        self.assertEqual(message.destination, part_b)

        menu = message.create_context_menu()
        swap_part_action = next(action for action in menu.actions() if action.text() == "Swap source and destination")
        swap_part_action.trigger()
        self.assertEqual(message.source, part_b)
        self.assertEqual(message.destination, part_a)

        menu = if_cond.sim_items[0].create_context_menu()
        del_action = next(action for action in menu.actions() if action.text() == "Delete message")
        del_action.trigger()
        self.assertEqual(len(if_cond.sim_items), 0)

        menu = self.sim_frame.ui.gvSimulator.scene().sim_items[0].create_context_menu()
        del_action = next(action for action in menu.actions() if action.text() == "Delete message")
        del_action.trigger()

        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().sim_items), 1)

    def test_rule_context_menu(self):
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        rule = self.sim_frame.ui.gvSimulator.scene().sim_items[0]
        if_cond = rule.conditions[0]

        menu = if_cond.create_context_menu()
        self.assertIsNone(next((action for action in menu.actions() if action.text() == "Remove else if block"), None))
        self.assertIsNone(next((action for action in menu.actions() if action.text() == "Remove else block"), None))
        message_type_menu = menu.findChildren(QMenu)[0]
        default_msg_type_action = next(action for action in message_type_menu.actions() if action.text() == "default")
        default_msg_type_action.trigger()
        self.assertEqual(len(if_cond.sim_items), 1)

        menu = if_cond.create_context_menu()
        add_else_if_cond_action = next(action for action in menu.actions() if action.text() == "Add else if block")
        add_else_if_cond_action.trigger()
        self.assertEqual(len(rule.conditions), 2)

        menu = if_cond.create_context_menu()
        add_else_cond_action = next(action for action in menu.actions() if action.text() == "Add else block")
        add_else_cond_action.trigger()
        self.assertEqual(len(rule.conditions), 3)

        else_if_cond = rule.conditions[1]
        menu = else_if_cond.create_context_menu()
        remove_else_if_cond_action = next(action for action in menu.actions() if action.text() == "Remove else if block")
        remove_else_if_cond_action.trigger()
        self.assertEqual(len(rule.conditions), 2)

        else_cond = rule.conditions[1]
        menu = else_cond.create_context_menu()
        remove_else_cond_action = next(action for action in menu.actions() if action.text() == "Remove else block")
        remove_else_cond_action.trigger()
        self.assertEqual(len(rule.conditions), 1)

        menu = if_cond.create_context_menu()
        remove_rule_action = next(action for action in menu.actions() if action.text() == "Remove rule")
        remove_rule_action.trigger()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().sim_items), 0)

    def test_select_all(self):
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        rule = self.sim_frame.ui.gvSimulator.scene().sim_items[0]
        if_cond = rule.conditions[0]
        menu = if_cond.create_context_menu()
        add_else_if_cond_action = next(action for action in menu.actions() if action.text() == "Add else if block")
        add_else_if_cond_action.trigger()
        else_if_cond = rule.conditions[1]
        self.sim_frame.ui.gvSimulator.scene().add_message(None, 1)
        self.sim_frame.ui.gvSimulator.scene().select_all_items()
        self.assertTrue(if_cond.isSelected())
        self.assertTrue(else_if_cond.isSelected())
        self.assertTrue(self.sim_frame.ui.gvSimulator.scene().sim_items[1].isSelected())

    def test_delete_selected_items(self):
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        rule = self.sim_frame.ui.gvSimulator.scene().sim_items[0]
        if_cond = rule.conditions[0]
        if_cond.on_add_else_cond_action_triggered()
        menu = if_cond.create_context_menu()
        add_message_action = next(action for action in menu.actions() if action.text() == "Add empty message")
        add_message_action.trigger()
        if_cond.sim_items[0].setSelected(True)
        else_cond = rule.conditions[1]
        else_cond.setSelected(True)
        self.sim_frame.ui.gvSimulator.scene().add_message(None, 1)
        self.sim_frame.ui.gvSimulator.scene().sim_items[1].setSelected(True)
        self.sim_frame.ui.gvSimulator.scene().delete_selected_items()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().sim_items), 1)
        self.assertEqual(len(if_cond.sim_items), 0)
        self.assertEqual(len(rule.conditions), 1)
        if_cond.setSelected(True)
        self.sim_frame.ui.gvSimulator.scene().delete_selected_items()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().sim_items), 0)

    def test_clear_all(self):
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        self.sim_frame.ui.gvSimulator.scene().add_message(None, 0)
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().sim_items), 2)
        self.sim_frame.ui.gvSimulator.scene().clear_all()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().sim_items), 0)

    def test_update_participants(self):
        participants = self.sim_frame.project_manager.participants
        part_a = Participant("Device A", shortname="A", color_index=0)
        part_b = Participant("Device B", shortname="B", color_index=1)

        participants.append(part_a)
        self.sim_frame.ui.gvSimulator.scene().update_participants(participants)
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().participants_dict), 1)
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().participants), 3)

        participants.append(part_b)
        self.sim_frame.ui.gvSimulator.scene().update_participants(participants)
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().participants_dict), 2)
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().participants), 4)

        participants.remove(part_a)
        self.sim_frame.ui.gvSimulator.scene().update_participants(participants)
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().participants_dict), 1)
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().participants), 3)

    def test_detect_source_destination(self):
        participants = self.sim_frame.project_manager.participants
        proto_analyzer = self.sframe.proto_analyzer

        part_a = Participant("Device A", shortname="A", color_index=0)
        participants.append(part_a)
        self.sim_frame.ui.gvSimulator.scene().update_participants(participants)

        msg = Message([True] * 100, pause=1000, message_type=proto_analyzer.default_message_type)
        source, destination = self.sim_frame.ui.gvSimulator.scene().detect_source_destination(msg)
        self.assertEqual(source, self.sim_frame.ui.gvSimulator.scene().participants_dict[part_a])
        self.assertEqual(destination, self.sim_frame.ui.gvSimulator.scene().broadcast_part)

        part_b = Participant("Device B", shortname="B", color_index=1)
        participants.append(part_b)
        self.sim_frame.ui.gvSimulator.scene().update_participants(participants)

        source, destination = self.sim_frame.ui.gvSimulator.scene().detect_source_destination(msg)
        self.assertEqual(source, self.sim_frame.ui.gvSimulator.scene().participants_dict[part_a])
        self.assertEqual(destination, self.sim_frame.ui.gvSimulator.scene().participants_dict[part_b])

        msg.participant = part_b
        source, destination = self.sim_frame.ui.gvSimulator.scene().detect_source_destination(msg)
        self.assertEqual(source, self.sim_frame.ui.gvSimulator.scene().participants_dict[part_b])
        self.assertEqual(destination, self.sim_frame.ui.gvSimulator.scene().participants_dict[part_a])