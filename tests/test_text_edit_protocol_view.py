from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh.util.Logger import logger

class TestTextEditProtocolView(QtTestCase):
    def test_create_context_menu(self):
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.setCurrentIndex(2)

        logger.debug("Get text edit")
        text_edit = self.form.signal_tab_controller.signal_frames[0].ui.txtEdProto

        menu = text_edit.create_context_menu()
        QApplication.instance().processEvents()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        checked = line_wrap_action.isChecked()
        line_wrap_action.trigger()

        menu = text_edit.create_context_menu()
        QApplication.instance().processEvents()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        self.assertNotEqual(checked, line_wrap_action.isChecked())
