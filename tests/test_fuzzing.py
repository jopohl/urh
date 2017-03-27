from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.controller.FuzzingDialogController import FuzzingDialogController
from urh.signalprocessing.encoder import Encoder


class TestFuzzing(QtTestCase):
    def setUp(self):
        super().setUp()
        self.form.add_signalfile(get_path_for_data_file("steckdose_anlernen.complex"))
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxNoiseTreshold.setValue(0.06)
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxNoiseTreshold.editingFinished.emit()
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxCenterOffset.setValue(-0.0127)
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxCenterOffset.editingFinished.emit()
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxInfoLen.setValue(100)
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxInfoLen.editingFinished.emit()

        self.gframe = self.form.generator_tab_controller

        # Dewhitening mit SyncByte 0x9a7d9a7d, Data Whitening Poly 0x21, Compute and apply CRC16 via X0r,
        # Rest auf False anlegen und setzen
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.form.compare_frame_controller.ui.cbProtoView.setCurrentIndex(1)  # Hex
        decoding = Encoder(["Data Whitening", constants.DECODING_DATAWHITENING, "0x9a7d9a7d;0x21;0x8"])
        self.form.compare_frame_controller.decodings.append(decoding)
        self.form.compare_frame_controller.ui.cbDecoding.addItem(decoding.name)
        self.form.compare_frame_controller.set_decoding(decoding)

        # CRC Check
        self.assertEqual(self.form.compare_frame_controller.protocol_model.display_data[0][-4:], "0000")

        # Serial Part 1: Bits 207-226 (Dezimal: 91412) (20 Bits)
        self.form.compare_frame_controller.add_protocol_label(start=206, end=225, messagenr=0, proto_view=0,
                                                              edit_label_name=False)

        # Zeros: Bits 227-244 (18 Bits)
        self.form.compare_frame_controller.add_protocol_label(start=226, end=243, messagenr=0, proto_view=0,
                                                              edit_label_name=False)

        # Serial Part 2: Bit 245 - 264 (Dezimal: 1034678) (20 Bits)
        self.form.compare_frame_controller.add_protocol_label(start=244, end=263, messagenr=0, proto_view=0,
                                                              edit_label_name=False)

        self.form.ui.tabWidget.setCurrentIndex(2)
        item = self.gframe.tree_model.rootItem.children[0].children[0]
        index = self.gframe.tree_model.createIndex(0, 0, item)
        rect = self.gframe.ui.treeProtocols.visualRect(index)

        self.assertEqual(len(self.gframe.ui.treeProtocols.selectedIndexes()), 0)
        QTest.mousePress(self.gframe.ui.treeProtocols.viewport(), Qt.LeftButton, pos = rect.center())
        self.assertEqual(self.gframe.ui.treeProtocols.selectedIndexes()[0], index)
        mimedata = self.gframe.tree_model.mimeData(self.gframe.ui.treeProtocols.selectedIndexes())
        self.gframe.table_model.dropMimeData(mimedata, 1, -1, -1, self.gframe.table_model.createIndex(0, 0))

        self.assertEqual(self.gframe.table_model.row_count, 1)
        self.assertEqual(len(self.gframe.table_model.protocol.protocol_labels), 3)

    def test_fuzz_label_bit(self):
        self.gframe.ui.cbViewType.setCurrentIndex(1) # hex view

        fdc = FuzzingDialogController(protocol=self.gframe.table_model.protocol, label_index=0, msg_index=0, proto_view=0, parent=self.gframe)
        fdc.finished.connect(self.gframe.refresh_label_list)
        fdc.finished.connect(self.gframe.refresh_table)
        fdc.finished.connect(self.gframe.set_fuzzing_ui_status)

        self.assertEqual(fdc.message_data[fdc.current_label_start:fdc.current_label_end], "00010110010100010100") # Serial Part 1
        fdc.ui.comboBoxFuzzingLabel.setCurrentIndex(1)
        self.assertEqual(fdc.message_data[fdc.current_label_start:fdc.current_label_end], "000000000000000000") # Zeros
        fdc.ui.comboBoxFuzzingLabel.setCurrentIndex(2)
        self.assertEqual(fdc.message_data[fdc.current_label_start:fdc.current_label_end], "11111100100110110110") # Serial Part 2

        fdc.close()
        QTest.qWait(100)

    def test_fuzz_label_hex(self):
        for message in self.gframe.table_model.protocol.messages:
            message.align_labels = False


        self.gframe.ui.cbViewType.setCurrentIndex(1) # hex view

        fdc = FuzzingDialogController(self.gframe.table_model.protocol, 0, 1, 1, parent=self.gframe)
        fdc.finished.connect(self.gframe.refresh_label_list)
        fdc.finished.connect(self.gframe.refresh_table)
        fdc.finished.connect(self.gframe.set_fuzzing_ui_status)

        self.assertEqual(fdc.message_data[fdc.current_label_start:fdc.current_label_end], "c5945") # Serial Part 1
        fdc.ui.comboBoxFuzzingLabel.setCurrentIndex(1)
        self.assertEqual(fdc.message_data[fdc.current_label_start:fdc.current_label_end], "00000") # Zeros
        fdc.ui.comboBoxFuzzingLabel.setCurrentIndex(2)
        self.assertEqual(fdc.message_data[fdc.current_label_start:fdc.current_label_end], "fc9b6") # Serial Part 2
