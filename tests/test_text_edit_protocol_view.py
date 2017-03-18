import unittest

from PyQt5.QtTest import QTest

import tests.utils_testing
from urh.controller.MainController import MainController
from tests.utils_testing import get_path_for_data_file
from urh.util.Logger import logger

app = tests.utils_testing.get_app()


class TestTextEditProtocolView(unittest.TestCase):
    def test_create_context_menu(self):
        logger.debug("Init form")
        self.form = MainController()
        app.processEvents()
        QTest.qWait(10)
        logger.debug("Intialized form")
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        logger.debug("added signalfile")
        app.processEvents()
        self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.setCurrentIndex(2)
        app.processEvents()

        logger.debug("Get text edit")
        text_edit = self.form.signal_tab_controller.signal_frames[0].ui.txtEdProto

        menu = text_edit.create_context_menu()
        app.processEvents()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        checked = line_wrap_action.isChecked()
        line_wrap_action.trigger()

        menu = text_edit.create_context_menu()
        app.processEvents()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        self.assertNotEqual(checked, line_wrap_action.isChecked())
