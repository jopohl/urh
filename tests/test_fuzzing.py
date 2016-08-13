import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

import tests.startApp
from urh import constants
from urh.controller.FuzzingDialogController import FuzzingDialogController
from urh.controller.MainController import MainController
from urh.signalprocessing.encoding import encoding

app = tests.startApp.app


class TestFuzzing(unittest.TestCase):
    def setUp(self):
        self.old_sym_len = constants.SETTINGS.value('rel_symbol_length', type=int)
        constants.SETTINGS.setValue('rel_symbol_length', 0) # Disable Symbols for this Test

        QTest.qWait(10)

        self.form = MainController()
        self.form.add_signalfile("./data/steckdose_anlernen.complex")
        QTest.qWait(10)
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxNoiseTreshold.setValue(0.06)
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxNoiseTreshold.editingFinished.emit()
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxCenterOffset.setValue(-0.0127)
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxCenterOffset.editingFinished.emit()
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxInfoLen.setValue(100)
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxInfoLen.editingFinished.emit()
        QTest.qWait(10)

        self.sframe = self.form.signal_tab_controller.signal_frames[0]
        self.cframe = self.form.compare_frame_controller
        self.gframe = self.form.generator_tab_controller

        # Dewhitening mit SyncByte 0x9a7d9a7d, Data Whitening Poly 0x21, Compute and apply CRC16 via X0r,
        # Rest auf False anlegen und setzen
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.cframe.ui.cbProtoView.setCurrentIndex(1) # Hex
        QTest.qWait(10)
        decoding = encoding(["Data Whitening", constants.DECODING_DATAWHITENING, "0x9a7d9a7d;0x21;0x8"])
        self.cframe.decodings.append(decoding)
        self.cframe.ui.cbDecoding.addItem(decoding.name)
        self.cframe.set_decoding(decoding)

        # CRC Check
        QTest.qWait(10)
        self.assertEqual(self.cframe.protocol_model.display_data[0][-4:], "0000")

        # Serial Part 1: Bits 207-226 (Dezimal: 91412) (20 Bits)
        self.cframe.add_protocol_label(206, 225, 0, 0, edit_label_name = False)

        # Zeros: Bits 227-244 (18 Bits)
        self.cframe.add_protocol_label(226, 243, 0, 0, edit_label_name = False)

        # Serial Part 2: Bit 245 - 264 (Dezimal: 1034678) (20 Bits)
        self.cframe.add_protocol_label(244, 263, 0, 0, edit_label_name = False)
        QTest.qWait(10)

        self.form.ui.tabWidget.setCurrentIndex(2)
        item = self.gframe.tree_model.rootItem.children[0].children[0]
        index = self.gframe.tree_model.createIndex(0, 0, item)
        rect = self.gframe.ui.treeProtocols.visualRect(index)

        self.assertEqual(len(self.gframe.ui.treeProtocols.selectedIndexes()), 0)
        QTest.mousePress(self.gframe.ui.treeProtocols.viewport(), Qt.LeftButton, pos = rect.center())
        self.assertEqual(self.gframe.ui.treeProtocols.selectedIndexes()[0], index)
        mimedata = self.gframe.tree_model.mimeData(self.gframe.ui.treeProtocols.selectedIndexes())
        self.gframe.table_model.dropMimeData(mimedata, 1, -1, -1, self.gframe.table_model.createIndex(0, 0))
        QTest.qWait(10)

        self.assertEqual(self.gframe.table_model.row_count, 1)
        self.assertEqual(len(self.gframe.table_model.protocol.protocol_labels), 3)

    def tearDown(self):
        constants.SETTINGS.setValue('rel_symbol_length', self.old_sym_len) # Restore Symbol Length

    def test_fuzz_label_bit(self):
        self.gframe.ui.cbViewType.setCurrentIndex(1) # hex view
        QTest.qWait(10)

        fdc = FuzzingDialogController(protocol=self.gframe.table_model.protocol, label_index=0, block_index=0, proto_view=0, parent=self.gframe)
        fdc.finished.connect(self.gframe.refresh_label_list)
        fdc.finished.connect(self.gframe.refresh_table)
        fdc.finished.connect(self.gframe.set_fuzzing_ui_status)

        self.assertEqual(fdc.block_data[fdc.current_label_start:fdc.current_label_end], "00010110010100010100") # Serial Part 1
        fdc.ui.comboBoxFuzzingLabel.setCurrentIndex(1)
        self.assertEqual(fdc.block_data[fdc.current_label_start:fdc.current_label_end], "000000000000000000") # Zeros
        fdc.ui.comboBoxFuzzingLabel.setCurrentIndex(2)
        self.assertEqual(fdc.block_data[fdc.current_label_start:fdc.current_label_end], "11111100100110110110") # Serial Part 2

    def test_fuzz_label_hex(self):
        for block in self.gframe.table_model.protocol.blocks:
            block.align_labels = False


        self.gframe.ui.cbViewType.setCurrentIndex(1) # hex view
        QTest.qWait(10)

        fdc = FuzzingDialogController(self.gframe.table_model.protocol, 0, 1, 1, parent=self.gframe)
        fdc.finished.connect(self.gframe.refresh_label_list)
        fdc.finished.connect(self.gframe.refresh_table)
        fdc.finished.connect(self.gframe.set_fuzzing_ui_status)

        self.assertEqual(fdc.block_data[fdc.current_label_start:fdc.current_label_end], "c5945") # Serial Part 1
        fdc.ui.comboBoxFuzzingLabel.setCurrentIndex(1)
        self.assertEqual(fdc.block_data[fdc.current_label_start:fdc.current_label_end], "00000") # Zeros
        fdc.ui.comboBoxFuzzingLabel.setCurrentIndex(2)
        self.assertEqual(fdc.block_data[fdc.current_label_start:fdc.current_label_end], "fc9b6") # Serial Part 2
