import sys
import unittest

import sip
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.utils_testing import get_path_for_data_file
from urh.controller.MainController import MainController
from urh.util.Logger import logger


class TestTextEditProtocolView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)
    
    def test_create_context_menu(self):
        form = MainController()
        form.add_signalfile(get_path_for_data_file("esaver.complex"))
        form.signal_tab_controller.signal_frames[0].ui.cbProtoView.setCurrentIndex(2)

        logger.debug("Get text edit")
        text_edit = form.signal_tab_controller.signal_frames[0].ui.txtEdProto

        menu = text_edit.create_context_menu()
        QApplication.instance().processEvents()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        checked = line_wrap_action.isChecked()
        line_wrap_action.trigger()

        menu = text_edit.create_context_menu()
        QApplication.instance().processEvents()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        self.assertNotEqual(checked, line_wrap_action.isChecked())

        form.close_all()
        QApplication.instance().processEvents()
        QTest.qWait(1)
