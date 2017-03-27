from tests.QtTestCase import QtTestCase


class TestMaincontrollerGUI(QtTestCase):
    def test_open_recent(self):
        # Ensure we have at least one recent action
        self.add_signal_to_form("esaver.complex")
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 1)

        self.form.recentFileActionList[0].trigger()
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 2)

    def test_update_decodings(self):
        self.form.update_decodings()
        self.assertTrue(True)

    def test_options_changed(self):
        self.add_signal_to_form("esaver.complex")
        self.form.on_options_changed({"rel_symbol_length": 0, "show_pause_as_time": True, "default_view": 0})
        self.assertEqual(self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.currentIndex(), 0)
