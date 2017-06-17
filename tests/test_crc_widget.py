from tests.QtTestCase import QtTestCase
from urh.controller.CRCWidgetController import CRCWidgetController
from urh.controller.ProtocolLabelController import ProtocolLabelController
from urh.signalprocessing.CRCLabel import CRCLabel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType


class TestCRCWidget(QtTestCase):
    def test_configure_crc_ranges(self):
        crc_label = CRCLabel("crc_label", 50, 100, 0, FieldType("crc", FieldType.Function.CRC))

        crc_widget_controller = CRCWidgetController(crc_label, Message([0]*100, 0, MessageType("test")), 0)
        model = crc_widget_controller.data_range_table_model
        self.assertEqual(model.data(model.index(0, 0)), 1)
        self.assertEqual(model.data(model.index(0, 1)), 50)
        self.assertEqual(model.rowCount(), 1)

        crc_widget_controller.ui.btnAddRange.click()
        self.assertEqual(model.rowCount(), 2)
        crc_widget_controller.ui.btnAddRange.click()
        self.assertEqual(model.rowCount(), 3)

        crc_widget_controller.ui.btnRemoveRange.click()
        self.assertEqual(model.rowCount(), 2)
        crc_widget_controller.ui.btnRemoveRange.click()
        self.assertEqual(model.rowCount(), 1)
        crc_widget_controller.ui.btnRemoveRange.click()
        self.assertEqual(model.rowCount(), 1)

    def test_crc_widget_in_protocol_label_dialog(self):
        mt = MessageType("test")
        mt.append(CRCLabel("test_crc", 8, 16, 0, FieldType("test_crc", FieldType.Function.CRC)))

        dialog = ProtocolLabelController(0, Message([0]*100, 0, mt), 0)
        self.assertEqual(dialog.ui.tabWidgetAdvancedSettings.count(), 1)
        self.assertEqual(dialog.ui.tabWidgetAdvancedSettings.tabText(0), "test_crc")
