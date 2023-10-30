import os
import tempfile
import time
from array import array

import numpy as np
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QMenu, QCompleter

from tests.QtTestCase import QtTestCase
from urh import settings
from urh.controller.MainController import MainController
from urh.controller.SimulatorTabController import SimulatorTabController
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import (
    NetworkSDRInterfacePlugin,
)
from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Participant import Participant
from urh.simulator.MessageItem import MessageItem
from urh.simulator.RuleItem import RuleItem
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorRule import ConditionType
from urh.ui.ExpressionLineEdit import ExpressionLineEdit
from urh.ui.RuleExpressionValidator import RuleExpressionValidator
from urh.util import util
from urh.util.Logger import logger


class TestSimulatorTabGUI(QtTestCase):
    def setUp(self):
        super().setUp()

        settings.OVERWRITE_RECEIVE_BUFFER_SIZE = 50000

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

        self.form.close_project()
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
        self.form.close_all_files()
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

        # constant value
        model.setData(model.index(0, 2), 0, role=Qt.EditRole)
        model.setData(model.index(0, 1), 0, role=Qt.EditRole)
        model.setData(model.index(0, 3), "11110000", role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "11110000")

        model.setData(model.index(0, 1), 1, role=Qt.EditRole)
        model.setData(model.index(0, 3), "ab", role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "ab")

        model.setData(model.index(0, 1), 2, role=Qt.EditRole)
        model.setData(model.index(0, 3), "=", role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "=")

        model.setData(model.index(0, 1), 3, role=Qt.EditRole)
        model.setData(model.index(0, 3), "240", role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "240")

        model.setData(model.index(0, 1), 4, role=Qt.EditRole)
        model.setData(model.index(0, 3), "55", role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "55")

        # get live during simulation
        model.setData(model.index(0, 2), 1, role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "-")
        stc.ui.tblViewFieldValues.openPersistentEditor(model.index(0, 3))

        # formula
        model.setData(model.index(0, 2), 2, role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3)), "")
        stc.ui.tblViewFieldValues.openPersistentEditor(model.index(0, 3))
        model.setData(model.index(0, 3), "4+5", role=Qt.EditRole)
        self.assertNotEqual(
            model.data(model.index(0, 3), role=Qt.BackgroundColorRole),
            settings.ERROR_BG_COLOR,
        )
        model.setData(model.index(0, 3), "item1.preamble + 42", role=Qt.EditRole)
        self.assertNotEqual(
            model.data(model.index(0, 3), role=Qt.BackgroundColorRole),
            settings.ERROR_BG_COLOR,
        )
        model.setData(model.index(0, 3), "item1.preamble + 42/", role=Qt.EditRole)
        self.assertEqual(
            model.data(model.index(0, 3), role=Qt.BackgroundColorRole),
            settings.ERROR_BG_COLOR,
        )

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

    def test_insert_column(self):
        self.__setup_project()
        self.add_all_signals_to_simulator()
        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        stc.ui.cbViewType.setCurrentText("Hex")

        lens = [len(msg) for msg in stc.simulator_message_table_model.protocol.messages]
        stc.ui.tblViewMessage.selectAll()
        stc.ui.tblViewMessage._insert_column(2)
        for i, l in enumerate(lens):
            self.assertEqual(
                lens[i] + 4, len(stc.simulator_message_table_model.protocol.messages[i])
            )

        stc.ui.cbViewType.setCurrentText("Bit")
        stc.ui.tblViewMessage.selectAll()
        stc.ui.tblViewMessage._insert_column(6)
        for i, l in enumerate(lens):
            self.assertEqual(
                lens[i] + 5, len(stc.simulator_message_table_model.protocol.messages[i])
            )

    def test_simulator_graphics_view(self):
        self.__setup_project()
        self.add_all_signals_to_simulator()
        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        self.assertGreater(len(stc.simulator_config.get_all_items()), 0)

        self.assertEqual(len(stc.simulator_scene.selectedItems()), 0)

        # select first message
        messages = stc.simulator_scene.get_all_message_items()
        pos = stc.ui.gvSimulator.mapFromScene(messages[0].scenePos())

        QTest.mouseClick(
            stc.ui.gvSimulator.viewport(), Qt.LeftButton, Qt.NoModifier, pos
        )

        self.assertEqual(len(stc.simulator_scene.selectedItems()), 1)
        self.assertIsInstance(stc.simulator_scene.selectedItems()[0], MessageItem)

        rules = [
            item for item in stc.simulator_scene.items() if isinstance(item, RuleItem)
        ]
        self.assertEqual(len(rules), 0)
        self.menus_to_ignore = [
            w for w in QApplication.topLevelWidgets() if isinstance(w, QMenu)
        ]
        timer = QTimer(self.form)
        timer.setInterval(1)
        timer.setSingleShot(True)
        timer.timeout.connect(
            self.__on_context_menu_simulator_graphics_view_timer_timeout
        )
        timer.start()

        stc.ui.gvSimulator.contextMenuEvent(
            QContextMenuEvent(QContextMenuEvent.Mouse, pos)
        )

        rules = [
            item for item in stc.simulator_scene.items() if isinstance(item, RuleItem)
        ]
        self.assertEqual(len(rules), 1)

    def test_simulator_message_table_context_menu(self):
        self.__setup_project()
        self.add_all_signals_to_simulator()
        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        stc.ui.tabWidget.setCurrentIndex(1)

        stc.simulator_scene.get_all_message_items()[0].setSelected(True)
        self.assertEqual(stc.simulator_message_field_model.rowCount(), 1)

        stc.ui.tblViewMessage.selectColumn(4)
        x, y = stc.ui.tblViewMessage.columnViewportPosition(
            4
        ), stc.ui.tblViewMessage.rowViewportPosition(0)
        pos = QPoint(x, y)
        stc.ui.tblViewMessage.context_menu_pos = pos
        menu = stc.ui.tblViewMessage.create_context_menu()

        names = [action.text() for action in menu.actions()]
        self.assertIn("Enforce encoding", names)
        add_label_action = next(
            action for action in menu.actions() if action.text() == "Create label..."
        )
        add_label_action.trigger()
        menu.close()
        stc.ui.tblViewMessage.selectRow(0)

        self.assertEqual(stc.simulator_message_field_model.rowCount(), 2)

    def test_expression_line_edit(self):
        e = ExpressionLineEdit()
        e.setCompleter(
            QCompleter(self.form.simulator_tab_controller.completer_model, e)
        )
        e.setValidator(
            RuleExpressionValidator(
                self.form.simulator_tab_controller.sim_expression_parser
            )
        )

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
        msg1 = SimulatorMessage(
            destination=alice,
            plain_bits=array("B", [1, 0, 1, 1]),
            pause=100,
            message_type=mt,
        )
        msg2 = SimulatorMessage(
            destination=bob,
            plain_bits=array("B", [1, 0, 1, 1]),
            pause=100,
            message_type=mt,
        )

        simulator_manager = self.form.simulator_tab_controller.simulator_config
        simulator_manager.add_items([msg1, msg2], 0, simulator_manager.rootItem)
        simulator_manager.add_label(
            5, 15, "test", parent_item=simulator_manager.rootItem.children[0]
        )

        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        model = stc.ui.listViewSimulate.model()
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.data(model.index(0, 0)), "Alice (A)")
        self.assertEqual(model.data(model.index(1, 0)), "Bob (B)")
        self.assertFalse(self.form.project_manager.participants[0].simulate)
        self.assertEqual(
            model.data(model.index(0, 0), role=Qt.CheckStateRole), Qt.Unchecked
        )
        self.assertFalse(self.form.project_manager.participants[1].simulate)
        self.assertEqual(
            model.data(model.index(1, 0), role=Qt.CheckStateRole), Qt.Unchecked
        )

        model.setData(model.index(0, 0), Qt.Checked, role=Qt.CheckStateRole)
        self.assertTrue(self.form.project_manager.participants[0].simulate)

    def test_valid_goto_targets(self):
        stc = self.form.simulator_tab_controller
        assert isinstance(stc, SimulatorTabController)
        self.__setup_project()
        self.add_all_signals_to_simulator()

        self.assertEqual(len(stc.simulator_config.get_all_messages()), 3)
        stc.ui.gvSimulator.on_add_goto_action_triggered()

        self.assertEqual(
            stc.ui.detail_view_widget.currentWidget(), stc.ui.page_goto_action
        )
        self.assertEqual(
            stc.ui.goto_combobox.count(), 3 + 1
        )  # select item... also in combobox

        stc.ui.gvSimulator.on_add_counter_action_triggered()
        stc.ui.gvSimulator.on_add_sleep_action_triggered()
        stc.ui.gvSimulator.on_add_goto_action_triggered()

        self.assertEqual(
            stc.ui.goto_combobox.count(), 5 + 1
        )  # select item... also in combobox

    def test_open_simulator_dialog_and_send_message(self):
        def __wait_for_simulator_log_message(dialog, log_message):
            n = 0
            while not any(log_message in msg for msg in dialog.simulator.log_messages):
                if n < 50:
                    time.sleep(0.5)
                else:
                    self.fail('Did not receive log message "{}"'.format(log_message))
                n += 1

        stc = self.form.simulator_tab_controller
        assert isinstance(stc, SimulatorTabController)

        self.__setup_project()
        self.add_all_signals_to_simulator()

        stc.simulator_scene.select_all_items()

        for msg in stc.simulator_scene.get_selected_messages():
            msg.destination = self.dennis
            stc.ui.gvSimulator.message_updated.emit(msg)

        list_model = stc.ui.listViewSimulate.model()
        self.assertEqual(list_model.rowCount(), 2)
        list_model.setData(
            list_model.createIndex(1, 0), Qt.Checked, role=Qt.CheckStateRole
        )

        dialog = stc.get_simulator_dialog()

        network_sdr_name = NetworkSDRInterfacePlugin.NETWORK_SDR_NAME
        dialog.device_settings_rx_widget.ui.cbDevice.setCurrentText(network_sdr_name)

        rcv_port = util.get_free_port()
        dialog.simulator.sniffer.rcv_device.set_server_port(rcv_port)

        dialog.simulator.sniffer.adaptive_noise = False
        dialog.simulator.sniffer.automatic_center = False

        dialog.ui.btnStartStop.click()

        __wait_for_simulator_log_message(dialog, "Waiting for message 1")

        modulator = dialog.project_manager.modulators[0]  # type: Modulator
        sender = NetworkSDRInterfacePlugin(raw_mode=True, sending=True)
        sender.client_port = rcv_port

        sender.send_raw_data(modulator.modulate("1" * 352), 1)
        time.sleep(0.5)
        sender.send_raw_data(IQArray(None, np.float32, 2000), 1)
        time.sleep(0.5)

        dialog.on_timer_timeout()  # enforce writing to text view
        simulator_log = dialog.ui.textEditSimulation.toPlainText()
        self.assertIn("Received message 1", simulator_log)
        self.assertIn("preamble: 11111111", simulator_log)

        dialog.close()

    def __on_context_menu_simulator_graphics_view_timer_timeout(self):
        menu = next(
            w
            for w in QApplication.topLevelWidgets()
            if isinstance(w, QMenu)
            and w.parent() is None
            and w not in self.menus_to_ignore
        )
        names = [action.text() for action in menu.actions()]
        self.assertIn("Source", names)
        add_rule_action = next(
            action for action in menu.actions() if action.text() == "Add rule"
        )
        add_rule_action.trigger()
        menu.close()

    def __setup_project(self):
        assert isinstance(self.form, MainController)
        directory = self.project_folder
        if not os.path.isdir(directory):
            os.mkdir(directory)

        if os.path.isfile(os.path.join(directory, "URHProject.xml")):
            os.remove(os.path.join(directory, "URHProject.xml"))

        self.form.project_manager.set_project_folder(
            directory, ask_for_new_project=False
        )
        self.form.project_manager.participants[:] = self.participants
        self.form.project_manager.project_updated.emit()
        self.add_signal_to_form("esaver.complex16s")
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)
        self.assertEqual(
            self.form.compare_frame_controller.participant_list_model.rowCount(), 3
        )

        for i in range(3):
            self.form.compare_frame_controller.proto_analyzer.messages[
                i
            ].participant = self.carl

        self.form.compare_frame_controller.add_protocol_label(8, 15, 0, 0, False)
        self.assertEqual(
            self.form.compare_frame_controller.label_value_model.rowCount(), 1
        )
