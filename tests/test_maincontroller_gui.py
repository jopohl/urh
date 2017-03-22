import unittest

import tests.utils_testing
from urh.controller.MainController import MainController

app = tests.utils_testing.get_app()


class TestMaincontrollerGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()

    def test_open_recent(self):
        self.form.add_signalfile(tests.utils_testing.get_path_for_data_file("esaver.complex"))
        tests.utils_testing.short_wait()
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 1)

        self.form.close_all()
        tests.utils_testing.short_wait(interval=10)

        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 0)
        self.form.recentFileActionList[0].trigger()
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 1)

    def test_update_decodings(self):
        self.form.update_decodings()
        self.assertTrue(True)

    def test_options_changed(self):
        self.form.add_signalfile(tests.utils_testing.get_path_for_data_file("esaver.complex"))
        self.form.on_options_changed({"rel_symbol_length": 0, "show_pause_as_time": True, "default_view": 0})
        self.assertEqual(self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.currentIndex(), 0)
