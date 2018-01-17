import os
import tempfile
from xml.dom import minidom
import xml.etree.ElementTree as ET

from tests.QtTestCase import QtTestCase
from urh.controller.MainController import MainController
from urh.controller.SimulatorTabController import SimulatorTabController
from urh.signalprocessing.Participant import Participant
from urh.simulator.SimulatorRule import ConditionType


class TestSimulatorTabGUI(QtTestCase):
    def setUp(self):
        super().setUp()
        self.carl = Participant("Carl", "C")
        self.dennis = Participant("Dennis", "D")
        self.participants = [self.carl, self.dennis]

    def test_save_and_load(self):
        stc = self.form.simulator_tab_controller  # type: SimulatorTabController
        self.__setup_project()
        self.assertEqual(len(stc.simulator_config.get_all_items()), 0)
        self.add_all_signals_to_simulator()
        self.assertGreater(len(stc.simulator_config.get_all_items()), 0)
        self.assertEqual(stc.simulator_message_table_model.rowCount(), 3)

        rule = stc.simulator_scene.add_rule(ref_item=None, position=0)
        stc.simulator_scene.add_rule_condition(rule, ConditionType.ELSE_IF)

        stc.simulator_scene.add_goto_action(None, 0)

        messages = stc.simulator_config.get_all_messages()
        self.assertEqual(len(messages), 3)
        for i, msg in enumerate(messages):
            self.assertEqual(msg.source, self.carl, msg=str(i))

        # select items
        self.assertEqual(stc.simulator_message_field_model.rowCount(), 0)
        stc.simulator_scene.select_all_items()
        self.assertEqual(stc.simulator_message_field_model.rowCount(), 1)

        xml_tag = stc.simulator_config.save_simulator_config_to_xml()
        xml_str = minidom.parseString(ET.tostring(xml_tag)).toprettyxml(indent="  ")

        print(xml_str)

        for child in xml_tag:
            print(stc.simulator_config.load_simulator_item_from_xml(child, []))

    def __setup_project(self):
        assert isinstance(self.form, MainController)
        directory = os.path.join(tempfile.gettempdir(), "simulator_project")
        if not os.path.isdir(directory):
            os.mkdir(directory)

        if os.path.isfile(os.path.join(directory, "URHProject.xml")):
            os.remove(os.path.join(directory, "URHProject.xml"))

        self.form.project_manager.set_project_folder(directory, ask_for_new_project=False)
        self.form.project_manager.participants = self.participants
        self.form.project_manager.project_updated.emit()
        self.add_signal_to_form("esaver.complex")
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)
        self.assertEqual(self.form.compare_frame_controller.participant_list_model.rowCount(), 3)

        for i in range(3):
            self.form.compare_frame_controller.proto_analyzer.messages[i].participant = self.carl

        self.form.compare_frame_controller.add_protocol_label(8, 16, 0, 0, False)
        self.assertEqual(self.form.compare_frame_controller.label_value_model.rowCount(), 1)