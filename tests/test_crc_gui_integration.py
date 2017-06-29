from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from tests.QtTestCase import QtTestCase
from urh import constants
from urh.controller.ChecksumWidgetController import ChecksumWidgetController
from urh.signalprocessing.Encoding import Encoding
from urh.util import util


class TestCRCGUIIntegration(QtTestCase):
    def test_wsp_crc(self):
        self.__add_wsp_signal()
        self.__set_wsp_encoding()

        self.form.compare_frame_controller.add_protocol_label(14, 14, 0, 1, edit_label_name=False)
        checksum_fieldtype = next(
            ft for ft in self.form.compare_frame_controller.field_types if ft.function == ft.Function.CHECKSUM)

        label_value_model = self.form.compare_frame_controller.label_value_model

        # Configure Normal Checksum and verify its wrong
        proto_label_dialog = self.form.compare_frame_controller.create_protocol_label_dialog(0)
        self.assertEqual(proto_label_dialog.ui.tabWidgetAdvancedSettings.count(), 0)
        proto_label_dialog.model.setData(proto_label_dialog.model.index(0, 0), checksum_fieldtype.caption)
        self.assertEqual(proto_label_dialog.ui.tabWidgetAdvancedSettings.count(), 1)
        checksum_tab = proto_label_dialog.ui.tabWidgetAdvancedSettings.widget(0)  # type: ChecksumWidgetController
        self.assertNotIn("WSP", checksum_tab.ui.comboBoxCategory.currentText())
        checksum_tab.ui.radioButtonWSPAuto.click()

        self.form.compare_frame_controller.ui.tblViewProtocol.clearSelection()
        self.form.compare_frame_controller.ui.tblViewProtocol.selectRow(0)

        self.assertEqual(label_value_model.data(label_value_model.index(0, 2), Qt.BackgroundColorRole),
                         constants.BG_COLOR_WRONG)

        # Configure WSP and verify its correct
        proto_label_dialog = self.form.compare_frame_controller.create_protocol_label_dialog(0)
        self.assertEqual(proto_label_dialog.ui.tabWidgetAdvancedSettings.count(), 1)
        checksum_tab = proto_label_dialog.ui.tabWidgetAdvancedSettings.widget(0)  # type: ChecksumWidgetController
        checksum_tab.ui.comboBoxCategory.setCurrentIndex(1)
        self.assertIn("WSP", checksum_tab.ui.comboBoxCategory.currentText())
        checksum_tab.ui.radioButtonWSPAuto.click()
        self.assertTrue(checksum_tab.ui.radioButtonWSPAuto.isChecked())
        proto_label_dialog.ui.btnConfirm.click()

        self.form.compare_frame_controller.ui.tblViewProtocol.clearSelection()
        self.form.compare_frame_controller.ui.tblViewProtocol.selectRow(0)

        self.assertEqual(label_value_model.data(label_value_model.index(0, 2), Qt.BackgroundColorRole),
                         constants.BG_COLOR_CORRECT)

    def test_cc1101_crc(self):
        self.__add_cc1101_signal()
        self.__set_cc1101_encoding()

        self.form.compare_frame_controller.add_protocol_label(24, 27, 0, 1, edit_label_name=False)
        checksum_fieldtype = next(
            ft for ft in self.form.compare_frame_controller.field_types if ft.function == ft.Function.CHECKSUM)

        label_value_model = self.form.compare_frame_controller.label_value_model

        # Configure Normal Checksum and verify its wrong
        proto_label_dialog = self.form.compare_frame_controller.create_protocol_label_dialog(0)
        self.assertEqual(proto_label_dialog.ui.tabWidgetAdvancedSettings.count(), 0)
        proto_label_dialog.model.setData(proto_label_dialog.model.index(0, 0), checksum_fieldtype.caption)
        self.assertEqual(proto_label_dialog.ui.tabWidgetAdvancedSettings.count(), 1)
        checksum_tab = proto_label_dialog.ui.tabWidgetAdvancedSettings.widget(0)  # type: ChecksumWidgetController
        self.assertEqual("generic", checksum_tab.ui.comboBoxCategory.currentText())
        self.assertNotEqual("CC1101", checksum_tab.ui.comboBoxCRCFunction.currentText())

        proto_label_dialog.ui.btnConfirm.click()

        self.form.compare_frame_controller.ui.tblViewProtocol.clearSelection()
        self.form.compare_frame_controller.ui.tblViewProtocol.selectRow(0)

        self.assertEqual(label_value_model.data(label_value_model.index(0, 2), Qt.BackgroundColorRole),
                         constants.BG_COLOR_WRONG)

        # Configure CC1101 and verify its correct
        proto_label_dialog = self.form.compare_frame_controller.create_protocol_label_dialog(0)
        self.assertEqual(proto_label_dialog.ui.tabWidgetAdvancedSettings.count(), 1)
        checksum_tab = proto_label_dialog.ui.tabWidgetAdvancedSettings.widget(0)  # type: ChecksumWidgetController
        checksum_tab.ui.comboBoxCRCFunction.setCurrentText("CC1101")
        self.assertEqual(checksum_tab.ui.lineEditCRCPolynomial.text(), "8005")
        self.assertEqual(checksum_tab.ui.lineEditFinalXOR.text(), "0000")
        self.assertEqual(checksum_tab.ui.lineEditStartValue.text(), "ffff")

        model = checksum_tab.ui.tableViewDataRanges.model()
        model.setData(model.index(0, 0), "17")
        self.assertEqual(model.data(model.index(0,0)), 17)

        proto_label_dialog.ui.btnConfirm.click()

        self.form.compare_frame_controller.ui.tblViewProtocol.clearSelection()
        self.form.compare_frame_controller.ui.tblViewProtocol.selectRow(0)

        self.assertEqual(label_value_model.data(label_value_model.index(0, 2), Qt.BackgroundColorRole),
                         constants.BG_COLOR_CORRECT)

    def __add_wsp_signal(self):
        self.add_signal_to_form("wsp.complex")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.cbModulationType.setCurrentText("ASK")
        signal_frame.ui.spinBoxNoiseTreshold.setValue(0.0400)
        signal_frame.ui.spinBoxNoiseTreshold.editingFinished.emit()
        signal_frame.ui.spinBoxCenterOffset.setValue(0.3480)
        signal_frame.ui.spinBoxCenterOffset.editingFinished.emit()
        signal_frame.ui.spinBoxInfoLen.setValue(20)
        signal_frame.ui.spinBoxInfoLen.editingFinished.emit()
        signal_frame.ui.spinBoxTolerance.setValue(2)
        signal_frame.ui.spinBoxTolerance.editingFinished.emit()

        self.assertEqual(len(signal_frame.proto_analyzer.plain_hex_str), 3)
        self.assertEqual(signal_frame.proto_analyzer.plain_hex_str[0], "0aad3d5ddddcc5d45ddbba0000000")
        self.assertEqual(signal_frame.proto_analyzer.plain_hex_str[1], "aad3d5ddddcc5d45ddbba00000000000")
        self.assertEqual(signal_frame.proto_analyzer.plain_hex_str[2], "aad3d5ddddcc5d45ddbba0000000")

    def __add_cc1101_signal(self):
        self.add_signal_to_form("cc1101.complex")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.cbModulationType.setCurrentText("FSK")
        signal_frame.ui.spinBoxNoiseTreshold.setValue(0.0600)
        signal_frame.ui.spinBoxNoiseTreshold.editingFinished.emit()
        signal_frame.ui.spinBoxCenterOffset.setValue(0)
        signal_frame.ui.spinBoxCenterOffset.editingFinished.emit()
        signal_frame.ui.spinBoxInfoLen.setValue(100)
        signal_frame.ui.spinBoxInfoLen.editingFinished.emit()
        signal_frame.ui.spinBoxTolerance.setValue(5)
        signal_frame.ui.spinBoxTolerance.editingFinished.emit()

        self.assertEqual(len(signal_frame.proto_analyzer.plain_hex_str), 1)
        self.assertEqual(signal_frame.proto_analyzer.plain_hex_str[0], "aaaaaaaa9a7d9a7dfc99ff1398fb8")

    def __set_wsp_encoding(self):
        self.form.compare_frame_controller.ui.cbProtoView.setCurrentText("Hex")
        decoding = Encoding(["WSP", constants.DECODING_ENOCEAN])
        self.form.compare_frame_controller.decodings.append(decoding)
        self.form.compare_frame_controller.fill_decoding_combobox()
        self.form.compare_frame_controller.ui.tblViewProtocol.selectAll()
        self.form.compare_frame_controller.ui.cbDecoding.setCurrentText("WSP")
        model = self.form.compare_frame_controller.protocol_model
        self.assertEqual(len(model.display_data), 3)
        msg = "aa9610002c1c024b"
        for i in range(3):
            for j, hex_char in enumerate(msg):
                self.assertEqual(model.data(model.index(i, j)), hex_char)

    def __set_cc1101_encoding(self):
        self.form.compare_frame_controller.ui.cbProtoView.setCurrentText("Hex")
        decoding = Encoding(["CC1101", constants.DECODING_DATAWHITENING, "0x9a7d9a7d;0x21;0x0"])

        self.form.compare_frame_controller.decodings.append(decoding)
        self.form.compare_frame_controller.fill_decoding_combobox()
        self.form.compare_frame_controller.ui.tblViewProtocol.selectAll()
        self.form.compare_frame_controller.ui.cbDecoding.setCurrentText("CC1101")
        model = self.form.compare_frame_controller.protocol_model
        self.assertEqual(len(model.display_data), 1)
        msg = "aaaaaaaa9a7d9a7d0378e289757e"
        for j, hex_char in enumerate(msg):
            self.assertEqual(model.data(model.index(0, j)), hex_char, msg=str(j))
