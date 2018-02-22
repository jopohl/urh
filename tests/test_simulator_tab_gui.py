import os
import tempfile
from array import array

from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QMenu, QCompleter

from tests.QtTestCase import QtTestCase
from urh import constants
from urh.controller.MainController import MainController
from urh.controller.SimulatorTabController import SimulatorTabController
from urh.signalprocessing.Participant import Participant
from urh.simulator.MessageItem import MessageItem
from urh.simulator.RuleItem import RuleItem
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorRule import ConditionType
from urh.ui.ExpressionLineEdit import ExpressionLineEdit
from urh.ui.RuleExpressionValidator import RuleExpressionValidator


class TestSimulatorTabGUI(QtTestCase):
    def setUp(self):
        super().setUp()
        self.carl = Participant("Carl", "C")
        self.dennis = Participant("Dennis", "D")
        self.participants = [self.carl, self.dennis]
        self.project_folder = os.path.join(tempfile.gettempdir(), "simulator_project")

        self.menus_to_ignore = []

    def test_save_and_load(self):
        assert isinstance(self.form, MainController)
        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        self.__setup_project()
        self.assertEqual(len(stc.simulator_config.get_all_items()), 0)
        self.add_all_signals_to_simulator()
        self.assertGreater(len(stc.simulator_config.get_all_items()), 0)
        self.assertEqual(stc.simulator_message_table_model.rowCount(), 3)

        rule = stc.simulator_scene.add_rule(ref_item=None, position=0)
        stc.simulator_scene.add_rule_condition(rule, ConditionType.ELSE_IF)

        stc.simulator_scene.add_goto_action(None, 0)
        stc.simulator_scene.add_trigger_command_action(None, 0)

        messages = stc.simulator_config.get_all_messages()
        self.assertEqual(len(messages), 3)
        for i, msg in enumerate(messages):
            self.assertEqual(msg.source, self.carl, msg=str(i))

        # select items
        self.assertEqual(stc.simulator_message_field_model.rowCount(), 0)
        stc.simulator_scene.select_all_items()
        self.assertEqual(stc.simulator_message_field_model.rowCount(), 1)

        self.form.close_all()
        self.assertEqual(len(stc.simulator_config.get_all_items()), 0)
        stc.simulator_scene.select_all_items()
        self.assertEqual(stc.simulator_message_field_model.rowCount(), 0)

        self.form.project_manager.set_project_folder(self.project_folder)

        self.assertEqual(stc.simulator_message_table_model.rowCount(), 3)
        self.assertGreater(len(stc.simulator_config.get_all_items()), 0)
        stc.simulator_scene.select_all_items()
        self.assertEqual(stc.simulator_message_field_model.rowCount(), 1)

    def test_save_and_load_standalone(self):
        assert isinstance(self.form, MainController)
        self.__setup_project()
        stc = self.form.simulator_tab_controller

        self.assertEqual(len(stc.simulator_config.get_all_items()), 0)
        self.add_all_signals_to_simulator()
        self.assertGreater(len(stc.simulator_config.get_all_items()), 0)
        self.assertEqual(stc.simulator_message_table_model.rowCount(), 3)

        self.assertEqual(stc.participant_table_model.rowCount(), 2)

        filename = os.path.join(tempfile.gettempdir(), "test.sim.xml")
        if os.path.isfile(filename):
            os.remove(filename)
        self.form.simulator_tab_controller.save_simulator_file(filename)
        self.form.close_all()
        self.form.project_manager.participants.clear()
        self.form.project_manager.project_updated.emit()

        self.assertEqual(len(stc.simulator_config.get_all_items()), 0)
        self.assertEqual(stc.simulator_message_table_model.rowCount(), 0)
        self.assertEqual(stc.participant_table_model.rowCount(), 0)
        self.form.add_files([filename])
        self.assertGreater(len(stc.simulator_config.get_all_items()), 0)
        self.assertEqual(stc.simulator_message_table_model.rowCount(), 3)
        self.assertEqual(stc.participant_table_model.rowCount(), 2)

    def test_edit_simulator_label_table(self):
        self.__setup_project()
        self.add_all_signals_to_simulator()
        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        stc.simulator_scene.select_all_items()
        model = stc.simulator_message_field_model
        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.data(model.index(0, 3)), "1" * 8)

        # get live during simulation
        model.setData(model.index(0, 2), 1, role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "-")
        stc.ui.tblViewFieldValues.openPersistentEditor(model.index(0, 3))

        # formula
        model.setData(model.index(0, 2), 2, role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "")
        stc.ui.tblViewFieldValues.openPersistentEditor(model.index(0, 3))
        model.setData(model.index(0, 3), "4+5", role=Qt.EditRole)
        self.assertNotEqual(model.data(model.index(0, 3), role=Qt.BackgroundColorRole), constants.ERROR_BG_COLOR)
        model.setData(model.index(0, 3), "item1.preamble + 42", role=Qt.EditRole)
        self.assertNotEqual(model.data(model.index(0, 3), role=Qt.BackgroundColorRole), constants.ERROR_BG_COLOR)
        model.setData(model.index(0, 3), "item1.preamble + 42/", role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3), role=Qt.BackgroundColorRole), constants.ERROR_BG_COLOR)

        # external program
        model.setData(model.index(0, 2), 3, role=Qt.EditRole)
        stc.ui.tblViewFieldValues.openPersistentEditor(model.index(0, 3))
        self.assertEqual(model.data(model.index(0, 3)), "")

        # random value
        model.setData(model.index(0, 2), 4, role=Qt.EditRole)
        stc.ui.tblViewFieldValues.openPersistentEditor(model.index(0, 3))
        self.assertTrue(model.data(model.index(0, 3)).startswith("Range (Decimal):"))
        model.setData(model.index(0, 3), (42, 1337), role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "Range (Decimal): 42 - 1337")

    def test_simulator_graphics_view(self):
        self.__setup_project()
        self.add_all_signals_to_simulator()
        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        self.assertGreater(len(stc.simulator_config.get_all_items()), 0)

        self.assertEqual(len(stc.simulator_scene.selectedItems()), 0)

        # select first message
        messages = stc.simulator_scene.get_all_message_items()
        pos = stc.ui.gvSimulator.mapFromScene(messages[0].scenePos())

        QTest.mouseClick(stc.ui.gvSimulator.viewport(), Qt.LeftButton, Qt.NoModifier, pos)

        self.assertEqual(len(stc.simulator_scene.selectedItems()), 1)
        self.assertIsInstance(stc.simulator_scene.selectedItems()[0], MessageItem)

        rules = [item for item in stc.simulator_scene.items() if isinstance(item, RuleItem)]
        self.assertEqual(len(rules), 0)
        self.menus_to_ignore = [w for w in QApplication.topLevelWidgets() if isinstance(w, QMenu)]
        timer = QTimer(self.form)
        timer.setInterval(1)
        timer.setSingleShot(True)
        timer.timeout.connect(self.__on_context_menu_simulator_graphics_view_timer_timeout)
        timer.start()

        stc.ui.gvSimulator.contextMenuEvent(QContextMenuEvent(QContextMenuEvent.Mouse, pos))

        rules = [item for item in stc.simulator_scene.items() if isinstance(item, RuleItem)]
        self.assertEqual(len(rules), 1)

    def test_simulator_message_table_context_menu(self):
        self.__setup_project()
        self.add_all_signals_to_simulator()
        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        stc.ui.tabWidget.setCurrentIndex(1)

        stc.simulator_scene.get_all_message_items()[0].setSelected(True)
        self.assertEqual(stc.simulator_message_field_model.rowCount(), 1)

        stc.ui.tblViewMessage.selectColumn(2)
        x, y = stc.ui.tblViewMessage.columnViewportPosition(2), stc.ui.tblViewMessage.rowViewportPosition(0)
        pos = QPoint(x, y)
        stc.ui.tblViewMessage.context_menu_pos = pos
        menu = stc.ui.tblViewMessage.create_context_menu()

        names = [action.text() for action in menu.actions()]
        self.assertIn("Enforce encoding", names)
        add_label_action = next(action for action in menu.actions() if action.text() == "Add protocol label")
        add_label_action.trigger()
        menu.close()
        stc.ui.tblViewMessage.selectRow(0)

        self.assertEqual(stc.simulator_message_field_model.rowCount(), 2)

    def test_expression_line_edit(self):
        e = ExpressionLineEdit()
        e.setCompleter(QCompleter(self.form.simulator_tab_controller.completer_model, e))
        e.setValidator(RuleExpressionValidator(self.form.simulator_tab_controller.sim_expression_parser))

        self.assertEqual(e.text(), "")
        QTest.keyClick(e, Qt.Key_R, Qt.NoModifier)
        self.assertEqual(e.text(), "r")

    def test_participant_table(self):
        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        stc.ui.tabWidget.setCurrentIndex(2)
        self.assertEqual(stc.participant_table_model.rowCount(), 0)

        for i in range(3):
            stc.ui.btnAddParticipant.click()

        QApplication.processEvents()
        self.assertEqual(stc.participant_table_model.rowCount(), 3)

        participants = stc.project_manager.participants
        self.assertEqual(participants[0].name, "Alice")
        self.assertEqual(participants[1].name, "Bob")
        self.assertEqual(participants[2].name, "Carl")

        stc.ui.tableViewParticipants.selectRow(1)
        stc.ui.btnUp.click()

        self.assertEqual(participants[0].name, "Bob")
        self.assertEqual(participants[1].name, "Alice")
        self.assertEqual(participants[2].name, "Carl")

        stc.ui.btnDown.click()

        self.assertEqual(participants[0].name, "Alice")
        self.assertEqual(participants[1].name, "Bob")
        self.assertEqual(participants[2].name, "Carl")

        stc.ui.btnDown.click()

        self.assertEqual(participants[0].name, "Alice")
        self.assertEqual(participants[1].name, "Carl")
        self.assertEqual(participants[2].name, "Bob")

    def test_participants_list(self):
        alice = Participant("Alice", "A")
        bob = Participant("Bob", "B")
        self.form.project_manager.participants.append(alice)
        self.form.project_manager.participants.append(bob)
        self.form.project_manager.project_updated.emit()

        mt = self.form.compare_frame_controller.proto_analyzer.default_message_type
        msg1 = SimulatorMessage(destination=alice, plain_bits=array("B", [1, 0, 1, 1]), pause=100, message_type=mt)
        msg2 = SimulatorMessage(destination=bob, plain_bits=array("B", [1, 0, 1, 1]), pause=100, message_type=mt)

        simulator_manager = self.form.simulator_tab_controller.simulator_config
        simulator_manager.add_items([msg1, msg2], 0, simulator_manager.rootItem)
        simulator_manager.add_label(5, 15, "test", parent_item=simulator_manager.rootItem.children[0])

        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        model = stc.ui.listViewSimulate.model()
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.data(model.index(0, 0)), "Alice (A)")
        self.assertEqual(model.data(model.index(1, 0)), "Bob (B)")
        self.assertFalse(self.form.project_manager.participants[0].simulate)
        self.assertEqual(model.data(model.index(0, 0), role=Qt.CheckStateRole), Qt.Unchecked)
        self.assertFalse(self.form.project_manager.participants[1].simulate)
        self.assertEqual(model.data(model.index(1, 0), role=Qt.CheckStateRole), Qt.Unchecked)

        model.setData(model.index(0, 0), Qt.Checked, role=Qt.CheckStateRole)
        self.assertTrue(self.form.project_manager.participants[0].simulate)

    def __on_context_menu_simulator_graphics_view_timer_timeout(self):
        menu = next(w for w in QApplication.topLevelWidgets() if isinstance(w, QMenu)
                    and w.parent() is None and w not in self.menus_to_ignore)
        names = [action.text() for action in menu.actions()]
        self.assertIn("Source", names)
        add_rule_action = next(action for action in menu.actions() if action.text() == "Add rule")
        add_rule_action.trigger()
        menu.close()

    def __setup_project(self):
        assert isinstance(self.form, MainController)
        directory = self.project_folder
        if not os.path.isdir(directory):
            os.mkdir(directory)

        if os.path.isfile(os.path.join(directory, "URHProject.xml")):
            os.remove(os.path.join(directory, "URHProject.xml"))

        self.form.project_manager.set_project_folder(directory, ask_for_new_project=False)
        self.form.project_manager.participants[:] = self.participants
        self.form.project_manager.project_updated.emit()
        self.add_signal_to_form("esaver.complex")
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)
        self.assertEqual(self.form.compare_frame_controller.participant_list_model.rowCount(), 3)

        for i in range(3):
            self.form.compare_frame_controller.proto_analyzer.messages[i].participant = self.carl

        self.form.compare_frame_controller.add_protocol_label(8, 15, 0, 0, False)
        self.assertEqual(self.form.compare_frame_controller.label_value_model.rowCount(), 1)
