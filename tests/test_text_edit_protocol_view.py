from tests.QtTestCase import QtTestCase
from urh.controller.MainController import MainController
from urh.signalprocessing.Participant import Participant
from urh.util.Logger import logger


class TestTextEditProtocolView(QtTestCase):
    def test_create_context_menu(self):
        assert isinstance(self.form, MainController)

        self.add_signal_to_form("esaver.complex")
        self.form.signal_tab_controller.signal_frames[0].ui.cbProtoView.setCurrentIndex(2)

        logger.debug("Get text edit")
        text_edit = self.form.signal_tab_controller.signal_frames[0].ui.txtEdProto

        menu = text_edit.create_context_menu()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        checked = line_wrap_action.isChecked()
        line_wrap_action.trigger()

        menu = text_edit.create_context_menu()
        line_wrap_action = next(action for action in menu.actions() if action.text().startswith("Linewrap"))
        self.assertNotEqual(checked, line_wrap_action.isChecked())

        self.assertEqual(len([action for action in menu.actions() if action.text() == "Participant"]), 0)
        self.form.project_manager.participants.append(Participant("Alice", "A"))
        text_edit.selectAll()
        menu = text_edit.create_context_menu()
        self.assertEqual(len([action for action in menu.actions() if action.text() == "Participant"]), 1)
