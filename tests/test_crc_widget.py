from tests.QtTestCase import QtTestCase
from urh.controller.CRCWidgetController import CRCWidgetController
from urh.signalprocessing.CRCLabel import CRCLabel
from urh.signalprocessing.FieldType import FieldType


class TestCRCWidget(QtTestCase):
    def test_configure_crc_ranges(self):
        crc_label = CRCLabel("crc_label", 50, 100, 0, FieldType("crc", FieldType.Function.CRC))

        crc_widget_controller = CRCWidgetController(crc_label)
        self.assertEqual(crc_widget_controller.ui.tableWidgetDataRanges.item(0, 0).text(), "0")
        self.assertEqual(crc_widget_controller.ui.tableWidgetDataRanges.item(0, 1).text(), "50")
        self.assertEqual(crc_widget_controller.ui.tableWidgetDataRanges.rowCount(), 1)

        crc_widget_controller.ui.btnAddRange.click()
        self.assertEqual(crc_widget_controller.ui.tableWidgetDataRanges.rowCount(), 2)
        crc_widget_controller.ui.btnAddRange.click()
        self.assertEqual(crc_widget_controller.ui.tableWidgetDataRanges.rowCount(), 3)

        crc_widget_controller.ui.btnRemoveRange.click()
        self.assertEqual(crc_widget_controller.ui.tableWidgetDataRanges.rowCount(), 2)
        crc_widget_controller.ui.btnRemoveRange.click()
        self.assertEqual(crc_widget_controller.ui.tableWidgetDataRanges.rowCount(), 1)
        crc_widget_controller.ui.btnRemoveRange.click()
        self.assertEqual(crc_widget_controller.ui.tableWidgetDataRanges.rowCount(), 1)
