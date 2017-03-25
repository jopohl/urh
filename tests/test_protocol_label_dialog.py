import unittest

import tests.utils_testing
from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.controller.MainController import MainController
from urh.controller.ProtocolLabelController import ProtocolLabelController

app = tests.utils_testing.get_app()


class TestProtocolLabelDialog(unittest.TestCase):
    def setUp(self):
        constants.SETTINGS.setValue("align_labels", True)

        self.form = MainController()
        self.form.add_protocol_file(get_path_for_data_file("protocol.proto"))

        self.cframe = self.form.compare_frame_controller

        self.cframe.add_protocol_label(9, 19, 0, 0, edit_label_name=False)  # equals 10-20 in view
        self.cframe.add_protocol_label(39, 54, 1, 0, edit_label_name=False) # equals 40-55 in view

        self.assertEqual(len(self.cframe.proto_analyzer.protocol_labels), 2)
        self.dialog = ProtocolLabelController(preselected_index=1,
                                              message=self.cframe.proto_analyzer.messages[0],
                                              viewtype=0, parent=self.cframe)

    def tearDown(self):
        self.form.close_all()
        tests.utils_testing.short_wait()

    def test_protocol_label_dialog(self):
        self.assertIn(self.cframe.proto_analyzer.default_message_type.name, self.dialog.windowTitle())
        table_model = self.dialog.ui.tblViewProtoLabels.model()

        self.assertEqual(table_model.rowCount(), 2)
        label = table_model.message_type[0]
        table_model.setData(table_model.index(0, 0), "testname")
        self.assertEqual(label.name, "testname")
        table_model.setData(table_model.index(0, 1), 15)
        self.assertEqual(label.start, 15 - 1)
        table_model.setData(table_model.index(0, 2), 30)
        self.assertEqual(label.end, 30)
        table_model.setData(table_model.index(0, 3), 4)
        self.assertEqual(label.color_index, 4)
        table_model.setData(table_model.index(0, 4), False)
        self.assertEqual(label.apply_decoding, False)

    def test_change_view_type(self):
        table_model = self.dialog.ui.tblViewProtoLabels.model()

        # Bit View
        self.assertEqual(table_model.data(table_model.index(0, 1)), 10)
        self.assertEqual(table_model.data(table_model.index(0, 2)), 20)

        self.assertEqual(table_model.data(table_model.index(1, 1)), 40)
        self.assertEqual(table_model.data(table_model.index(1, 2)), 55)

        self.dialog.ui.cbProtoView.setCurrentIndex(1)
        self.assertEqual(table_model.data(table_model.index(0, 1)), 4)
        self.assertEqual(table_model.data(table_model.index(0, 2)), 6)

        self.assertEqual(table_model.data(table_model.index(1, 1)), 12)
        self.assertEqual(table_model.data(table_model.index(1, 2)), 15)

        label = table_model.message_type[0]
        table_model.setData(table_model.index(0, 1), 2)
        table_model.setData(table_model.index(0, 2), 5)

        self.assertEqual(label.start, 4)
        self.assertEqual(label.end, 17)
