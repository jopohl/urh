from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from tests.QtTestCase import QtTestCase
from urh import settings
from urh.controller.dialogs.FuzzingDialog import FuzzingDialog
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.Modulator import Modulator


class TestFuzzingDialog(QtTestCase):
    def setUp(self):
        super().setUp()
        self.add_signal_to_form("steckdose_anlernen.complex")
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxNoiseTreshold.setValue(0.06)
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxNoiseTreshold.editingFinished.emit()
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxCenterOffset.setValue(-0.0127)
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxCenterOffset.editingFinished.emit()
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxSamplesPerSymbol.setValue(100)
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxSamplesPerSymbol.editingFinished.emit()

        self.gframe = self.form.generator_tab_controller
        self.gframe.ui.cbViewType.setCurrentIndex(1)  # hex view
        self.gframe.modulators.append(
            Modulator("Prevent Modulation bootstrap when adding first protocol")
        )
        self.gframe.refresh_modulators()

        # Dewhitening mit SyncByte 0x9a7d9a7d, Data Whitening Poly 0x21, Compute and apply CRC16 via X0r,
        # Rest auf False anlegen und setzen
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.form.compare_frame_controller.ui.cbProtoView.setCurrentIndex(1)  # Hex
        decoding = Encoding(
            ["Data Whitening", settings.DECODING_DATAWHITENING, "0x9a7d9a7d;0x21"]
        )
        self.form.compare_frame_controller.decodings.append(decoding)
        self.form.compare_frame_controller.ui.cbDecoding.addItem(decoding.name)
        self.form.compare_frame_controller.set_decoding(decoding)

        # Serial Part 1: Bits 207-226 (Dezimal: 91412) (20 Bits)
        self.form.compare_frame_controller.add_protocol_label(
            start=206, end=225, messagenr=0, proto_view=0, edit_label_name=False
        )

        # Zeros: Bits 227-244 (18 Bits)
        self.form.compare_frame_controller.add_protocol_label(
            start=226, end=243, messagenr=0, proto_view=0, edit_label_name=False
        )

        # Serial Part 2: Bit 245 - 264 (Dezimal: 1034678) (20 Bits)
        self.form.compare_frame_controller.add_protocol_label(
            start=244, end=263, messagenr=0, proto_view=0, edit_label_name=False
        )

        self.form.ui.tabWidget.setCurrentIndex(2)
        item = self.gframe.tree_model.rootItem.children[0].children[0]
        index = self.gframe.tree_model.createIndex(0, 0, item)
        rect = self.gframe.ui.treeProtocols.visualRect(index)

        self.assertEqual(len(self.gframe.ui.treeProtocols.selectedIndexes()), 0)
        QTest.mousePress(
            self.gframe.ui.treeProtocols.viewport(), Qt.LeftButton, pos=rect.center()
        )
        self.assertEqual(self.gframe.ui.treeProtocols.selectedIndexes()[0], index)
        mimedata = self.gframe.tree_model.mimeData(
            self.gframe.ui.treeProtocols.selectedIndexes()
        )
        self.gframe.table_model.dropMimeData(
            mimedata, 1, -1, -1, self.gframe.table_model.createIndex(0, 0)
        )

        self.assertEqual(self.gframe.table_model.row_count, 1)
        self.assertEqual(len(self.gframe.table_model.protocol.protocol_labels), 3)

        self.dialog = FuzzingDialog(
            protocol=self.gframe.table_model.protocol,
            label_index=0,
            msg_index=0,
            proto_view=0,
            parent=self.gframe,
        )
        self.dialog.finished.connect(self.gframe.refresh_label_list)
        self.dialog.finished.connect(self.gframe.refresh_table)
        self.dialog.finished.connect(self.gframe.set_fuzzing_ui_status)

        if self.SHOW:
            self.dialog.show()

    def test_fuzz_label_bit(self):
        self.assertEqual(
            self.dialog.message_data[
                self.dialog.current_label_start : self.dialog.current_label_end
            ],
            "00010110010100010100",
        )  # Serial Part 1
        self.dialog.ui.comboBoxFuzzingLabel.setCurrentIndex(1)
        self.assertEqual(
            self.dialog.message_data[
                self.dialog.current_label_start : self.dialog.current_label_end
            ],
            "000000000000000000",
        )  # Zeros
        self.dialog.ui.comboBoxFuzzingLabel.setCurrentIndex(2)
        self.assertEqual(
            self.dialog.message_data[
                self.dialog.current_label_start : self.dialog.current_label_end
            ],
            "11111100100110110110",
        )  # Serial Part 2

    def test_fuzz_label_hex(self):
        for message in self.gframe.table_model.protocol.messages:
            message.align_labels = False

        self.dialog.proto_view = 1

        self.assertEqual(
            self.dialog.message_data[
                self.dialog.current_label_start : self.dialog.current_label_end
            ],
            "c5945",
        )  # Serial Part 1
        self.dialog.ui.comboBoxFuzzingLabel.setCurrentIndex(1)
        self.assertEqual(
            self.dialog.message_data[
                self.dialog.current_label_start : self.dialog.current_label_end
            ],
            "00000",
        )  # Zeros
        self.dialog.ui.comboBoxFuzzingLabel.setCurrentIndex(2)
        self.assertEqual(
            self.dialog.message_data[
                self.dialog.current_label_start : self.dialog.current_label_end
            ],
            "fc9b6",
        )  # Serial Part 2

    def test_add_remove_fuzzing_data(self):
        self.assertEqual(
            self.dialog.fuzz_table_model.data[0], "00010110010100010100"
        )  # serial part 1
        self.assertEqual(self.dialog.fuzz_table_model.rowCount(), 1)
        self.dialog.ui.btnAddRow.click()
        self.assertEqual(
            self.dialog.fuzz_table_model.data[1], "00010110010100010101"
        )  # serial part 1
        self.dialog.ui.btnAddRow.click()
        self.assertEqual(
            self.dialog.fuzz_table_model.data[2], "00010110010100010110"
        )  # serial part 1
        self.assertEqual(self.dialog.fuzz_table_model.rowCount(), 3)
        self.dialog.ui.btnDelRow.click()
        self.dialog.ui.btnDelRow.click()
        self.assertEqual(self.dialog.fuzz_table_model.rowCount(), 1)

    def test_adding_fuzzing_range(self):
        self.assertEqual(
            self.dialog.fuzz_table_model.data[0], "00010110010100010100"
        )  # serial part 1
        self.dialog.ui.sBAddRangeStart.setValue(10)
        self.dialog.ui.sBAddRangeEnd.setValue(100)
        self.dialog.ui.sBAddRangeStep.setValue(20)
        self.dialog.ui.btnAddFuzzingValues.click()
        self.assertEqual(6, self.dialog.fuzz_table_model.rowCount())

    def test_adding_fuzzing_boundaries(self):
        self.assertEqual(
            self.dialog.fuzz_table_model.data[0], "00010110010100010100"
        )  # serial part 1
        self.dialog.ui.spinBoxLowerBound.setValue(2)
        self.dialog.ui.spinBoxUpperBound.setValue(200)
        self.dialog.ui.spinBoxBoundaryNumber.setValue(2)
        self.dialog.ui.comboBoxStrategy.setCurrentIndex(1)
        self.dialog.ui.btnAddFuzzingValues.click()
        self.assertEqual(5, self.dialog.fuzz_table_model.rowCount())

    def test_adding_fuzzing_random_values(self):
        self.assertEqual(
            self.dialog.fuzz_table_model.data[0], "00010110010100010100"
        )  # serial part 1
        self.dialog.ui.spinBoxNumberRandom.setValue(10)
        self.dialog.ui.comboBoxStrategy.setCurrentIndex(2)
        self.dialog.ui.btnAddFuzzingValues.click()
        self.assertEqual(11, self.dialog.fuzz_table_model.rowCount())

    def test_remove_duplicates(self):
        self.assertEqual(
            self.dialog.fuzz_table_model.data[0], "00010110010100010100"
        )  # serial part 1
        self.dialog.ui.sBAddRangeStart.setValue(10)
        self.dialog.ui.sBAddRangeEnd.setValue(50)
        self.dialog.ui.sBAddRangeStep.setValue(5)
        self.dialog.ui.btnAddFuzzingValues.click()
        self.assertEqual(10, self.dialog.fuzz_table_model.rowCount())
        self.dialog.ui.btnAddFuzzingValues.click()
        self.dialog.ui.btnAddFuzzingValues.click()
        self.assertEqual(28, self.dialog.fuzz_table_model.rowCount())
        self.dialog.ui.chkBRemoveDuplicates.click()
        self.assertEqual(10, self.dialog.fuzz_table_model.rowCount())
        self.dialog.ui.btnAddFuzzingValues.click()
        self.assertEqual(10, self.dialog.fuzz_table_model.rowCount())
