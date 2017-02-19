import unittest

from PyQt5.QtTest import QTest

import tests.utils_testing
from urh.controller.MainController import MainController
from tests.utils_testing import get_path_for_data_file
from urh.ui.views.TextEditProtocolView import TextEditProtocolView
app = tests.utils_testing.app


class TestTextEditProtocolView(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.setCurrentIndex(2)
        self.text_edit = self.form.signal_tab_controller.signal_frames[0].ui.txtEdProto

    def test_create_context_menu(self):
        menu = self.text_edit.create_context_menu()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        checked = line_wrap_action.isChecked()
        line_wrap_action.trigger()

        menu = self.text_edit.create_context_menu()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        self.assertNotEqual(checked, line_wrap_action.isChecked())
