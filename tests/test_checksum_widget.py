import array

from tests.QtTestCase import QtTestCase
from urh.controller.widgets.ChecksumWidget import ChecksumWidget
from urh.controller.dialogs.ProtocolLabelDialog import ProtocolLabelDialog
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.util import util
from urh.util.GenericCRC import GenericCRC
from urh.util.WSPChecksum import WSPChecksum


class TestChecksumWidget(QtTestCase):
    def test_configure_crc_ranges(self):
        checksum_label = ChecksumLabel("checksum_label", 50, 100, 0, FieldType("crc", FieldType.Function.CHECKSUM))

        crc_widget_controller = ChecksumWidget(checksum_label, Message([0] * 100, 0, MessageType("test")), 0)
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

    def test_configure_crc_parameters(self):
        crc_label = ChecksumLabel("crc_label", 25, 120, 0, FieldType("crc", FieldType.Function.CHECKSUM))

        crc_widget_controller = ChecksumWidget(crc_label, Message([0] * 150, 0, MessageType("test")), 0)

        crc = GenericCRC(polynomial=list(GenericCRC.DEFAULT_POLYNOMIALS.keys())[0])
        self.assertEqual(crc_widget_controller.ui.lineEditCRCPolynomial.text(), crc.polynomial_as_hex_str)
        self.assertEqual(crc_widget_controller.ui.lineEditStartValue.text(), util.bit2hex(crc.start_value))
        self.assertEqual(crc_widget_controller.ui.lineEditFinalXOR.text(), util.bit2hex(crc.final_xor))

        crc_widget_controller.ui.comboBoxCRCFunction.setCurrentIndex(2)
        crc.polynomial = crc.choose_polynomial(2)
        self.assertEqual(crc_widget_controller.ui.lineEditCRCPolynomial.text(), crc.polynomial_as_hex_str)

        crc_widget_controller.ui.lineEditCRCPolynomial.setText("abcde")
        crc_widget_controller.ui.lineEditCRCPolynomial.editingFinished.emit()
        self.assertEqual(crc_label.checksum.polynomial, array.array("B", [1]) + util.hex2bit("abcde"))

        crc_widget_controller.ui.lineEditStartValue.setText("12345")
        crc_widget_controller.ui.lineEditStartValue.editingFinished.emit()
        self.assertEqual(util.bit2hex(crc_label.checksum.start_value), "12345")

        crc_widget_controller.ui.lineEditFinalXOR.setText("cccaa")
        crc_widget_controller.ui.lineEditFinalXOR.editingFinished.emit()
        self.assertEqual(util.bit2hex(crc_label.checksum.final_xor), "cccaa")

    def test_default_crcs(self):
        crc_label = ChecksumLabel("crc_label", 25, 120, 0, FieldType("crc", FieldType.Function.CHECKSUM))
        crc_widget_controller = ChecksumWidget(crc_label, Message([0] * 150, 0, MessageType("test")), 0)

        default_crc_polynomials = GenericCRC.DEFAULT_POLYNOMIALS
        special_crcs = ChecksumWidget.SPECIAL_CRCS

        self.assertEqual(len(default_crc_polynomials) + len(special_crcs),
                         crc_widget_controller.ui.comboBoxCRCFunction.count())
        for i, default_polynomial_name in enumerate(default_crc_polynomials):
            self.assertEqual(default_polynomial_name, crc_widget_controller.ui.comboBoxCRCFunction.itemText(i))

        for i, special_crc in enumerate(special_crcs):
            self.assertEqual(special_crc, crc_widget_controller.ui.comboBoxCRCFunction.itemText(i+len(default_crc_polynomials)))

        crc_widget_controller.ui.comboBoxCRCFunction.setCurrentIndex(1)
        self.assertNotEqual(crc_widget_controller.ui.comboBoxCRCFunction.currentText(), "8_standard")
        crc_widget_controller.ui.comboBoxCRCFunction.setCurrentText("8_standard")
        self.assertEqual(crc_widget_controller.ui.comboBoxCRCFunction.currentText(), "8_standard")
        self.assertEqual(crc_widget_controller.ui.lineEditCRCPolynomial.text(), "d5")

    def test_crc_widget_in_protocol_label_dialog(self):
        mt = MessageType("test")
        mt.append(ChecksumLabel("test_crc", 8, 16, 0, FieldType("test_crc", FieldType.Function.CHECKSUM)))

        self.dialog = ProtocolLabelDialog(0, Message([0] * 100, 0, mt), 0)
        self.assertEqual(self.dialog.ui.tabWidgetAdvancedSettings.count(), 1)
        self.assertEqual(self.dialog.ui.tabWidgetAdvancedSettings.tabText(0), "test_crc")

    def test_enocean_checksum(self):
        checksum_label = ChecksumLabel("checksum_label", 50, 100, 0, FieldType("crc", FieldType.Function.CHECKSUM))
        crc_widget_controller = ChecksumWidget(checksum_label, Message([0] * 100, 0, MessageType("test")), 0)

        crc_widget_controller.ui.comboBoxCategory.setCurrentIndex(1)
        self.assertEqual(crc_widget_controller.ui.stackedWidget.currentWidget(), crc_widget_controller.ui.page_wsp)

        self.assertTrue(crc_widget_controller.ui.radioButtonWSPAuto.isChecked())

        crc_widget_controller.ui.radioButtonWSPChecksum8.click()

        self.assertEqual(checksum_label.checksum.mode, WSPChecksum.ChecksumMode.checksum8)
