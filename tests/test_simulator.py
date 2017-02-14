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
        number_of_items = len(self.sim_frame.ui.gvSimulator.scene().items)
        self.sim_frame.ui.gvSimulator.scene().add_rule()
        self.assertEqual(len(self.sim_frame.ui.gvSimulator.scene().items), number_of_items + 1)
        self.assertEqual(type(self.sim_frame.ui.gvSimulator.scene().items[number_of_items]), RuleItem)