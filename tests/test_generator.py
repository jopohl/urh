import array
import os

from PyQt5.QtCore import QDir, QPoint, Qt
from PyQt5.QtTest import QTest

from tests.QtTestCase import QtTestCase


class TestGenerator(QtTestCase):
    def test_generation(self):
        """
        Complex test including much functionality
        1) Load a Signal
        2) Set Decoding in Compareframe
        3) Move with encoding to Generator
        4) Generate datafile
        5) Read datafile and compare with original signal

        """
        # Load a Signal
        self.add_signal_to_form("ask.complex")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.cbModulationType.setCurrentIndex(0)  # ASK
        signal_frame.ui.spinBoxInfoLen.setValue(295)
        signal_frame.ui.spinBoxCenterOffset.setValue(-0.1667)
        signal_frame.refresh()
        signal_frame.ui.cbProtoView.setCurrentIndex(0)

        proto = "1011001001011011011011011011011011001000000"
        self.assertTrue(signal_frame.ui.txtEdProto.toPlainText().startswith(proto))

        # Set Decoding
        self.form.ui.tabWidget.setCurrentIndex(1)
        cfc = self.form.compare_frame_controller
        cfc.ui.cbDecoding.setCurrentIndex(1)  # NRZ-I
        proto_inv = cfc.proto_analyzer.decoded_proto_bits_str[0]
        self.assertTrue(self.__is_inv_proto(proto, proto_inv))

        # Move with encoding to generator
        gframe = self.form.generator_tab_controller
        gframe.ui.cbViewType.setCurrentIndex(0)
        self.add_signal_to_generator(signal_index=0)
        self.assertEqual(array.array("B", list(map(int, proto_inv))), gframe.table_model.display_data[0])
        self.assertNotEqual(array.array("B", list(map(int, proto))), gframe.table_model.display_data[0])

        # Generate Datafile
        modulator = gframe.modulators[0]
        modulator.modulation_type = 0
        modulator.samples_per_bit = 295
        buffer = gframe.prepare_modulation_buffer(gframe.total_modulated_samples, show_error=False)
        modulated_data = gframe.modulate_data(buffer)
        filename = os.path.join(QDir.tempPath(), "test_generator.complex")
        modulated_data.tofile(filename)

        # Reload datafile and see if bits match
        self.form.add_signalfile(filename)
        self.assertEqual(len(self.form.signal_tab_controller.signal_frames), 2)
        signal_frame = self.form.signal_tab_controller.signal_frames[1]

        self.assertEqual(signal_frame.signal.num_samples, 14374)
        signal_frame.ui.cbProtoView.setCurrentIndex(0)
        self.assertEqual(signal_frame.ui.lineEditSignalName.text(), "test_generator")
        signal_frame.ui.cbModulationType.setCurrentIndex(0)  # ASK
        signal_frame.ui.spinBoxNoiseTreshold.setValue(0)
        signal_frame.ui.spinBoxNoiseTreshold.editingFinished.emit()

        signal_frame.ui.spinBoxInfoLen.setValue(295)
        signal_frame.ui.spinBoxInfoLen.editingFinished.emit()

        signal_frame.ui.spinBoxCenterOffset.setValue(0.1)
        signal_frame.ui.spinBoxCenterOffset.editingFinished.emit()

        signal_frame.ui.spinBoxTolerance.setValue(6)
        signal_frame.ui.spinBoxTolerance.editingFinished.emit()

        self.assertEqual(len(signal_frame.proto_analyzer.messages), 1)
        gen_proto = signal_frame.ui.txtEdProto.toPlainText()
        gen_proto = gen_proto[:gen_proto.index(" ")]
        self.assertTrue(proto.startswith(gen_proto))

    def test_close_signal(self):
        self.add_signal_to_form("ask.complex")
        sframe = self.form.signal_tab_controller.signal_frames[0]
        sframe.ui.cbModulationType.setCurrentIndex(0)  # ASK
        sframe.ui.spinBoxInfoLen.setValue(295)
        sframe.ui.spinBoxCenterOffset.setValue(-0.1667)
        sframe.refresh()

        # Move with encoding to generator
        gframe = self.form.generator_tab_controller
        gframe.ui.cbViewType.setCurrentIndex(0)
        item = gframe.tree_model.rootItem.children[0].children[0]
        index = gframe.tree_model.createIndex(0, 0, item)
        rect = gframe.ui.treeProtocols.visualRect(index)
        QTest.mousePress(gframe.ui.treeProtocols.viewport(), Qt.LeftButton, pos=rect.center())
        self.assertEqual(gframe.ui.treeProtocols.selectedIndexes()[0], index)
        mimedata = gframe.tree_model.mimeData(gframe.ui.treeProtocols.selectedIndexes())
        gframe.table_model.dropMimeData(mimedata, 1, -1, -1, gframe.table_model.createIndex(0, 0))
        self.assertEqual(gframe.table_model.row_count, self.form.compare_frame_controller.protocol_model.row_count)
        self.form.ui.tabWidget.setCurrentIndex(0)
        self.form.on_selected_tab_changed(0)
        sframe.ui.btnCloseSignal.click()
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.form.on_selected_tab_changed(1)
        self.form.ui.tabWidget.setCurrentIndex(2)
        self.form.on_selected_tab_changed(2)
        self.assertEqual(1, 1)

    def test_create_table_context_menu(self):
        # Context menu should only contain one item (add new message)
        self.assertEqual(self.form.generator_tab_controller.table_model.rowCount(), 0)
        self.form.generator_tab_controller.ui.tableMessages.context_menu_pos = QPoint(0, 0)
        menu = self.form.generator_tab_controller.ui.tableMessages.create_context_menu()
        self.assertEqual(len(menu.actions()), 1)

        # Add data to test entries in context menu
        self.add_signal_to_form("ask.complex")
        gframe = self.form.generator_tab_controller
        index = gframe.tree_model.createIndex(0, 0, gframe.tree_model.rootItem.children[0].children[0])
        mimedata = gframe.tree_model.mimeData([index])
        gframe.table_model.dropMimeData(mimedata, 1, -1, -1, gframe.table_model.createIndex(0, 0))

        self.assertGreater(self.form.generator_tab_controller.table_model.rowCount(), 0)
        menu = self.form.generator_tab_controller.ui.tableMessages.create_context_menu()
        n_items = len(menu.actions())
        self.assertGreater(n_items, 1)

        # If there is a selection, additional items should be present in context menu
        gframe.ui.tableMessages.selectRow(0)
        menu = self.form.generator_tab_controller.ui.tableMessages.create_context_menu()
        self.assertGreater(len(menu.actions()), n_items)

    def test_add_empty_row_behind(self):
        self.assertEqual(self.form.generator_tab_controller.table_model.rowCount(), 0)
        gframe = self.form.generator_tab_controller
        gframe.ui.cbViewType.setCurrentIndex(0)
        gframe.table_model.add_empty_row_behind(-1, 30)
        self.assertEqual(self.form.generator_tab_controller.table_model.rowCount(), 1)

        # Add data to test
        self.add_signal_to_form("ask.complex")

        index = gframe.tree_model.createIndex(0, 0, gframe.tree_model.rootItem.children[0].children[0])
        mimedata = gframe.tree_model.mimeData([index])
        gframe.table_model.dropMimeData(mimedata, 1, -1, -1, gframe.table_model.createIndex(0, 0))
        self.assertEqual(self.form.generator_tab_controller.table_model.rowCount(), 2)
        self.assertNotEqual(len(self.form.generator_tab_controller.table_model.display_data[1]), 30)
        gframe.table_model.add_empty_row_behind(0, 30)
        self.assertEqual(self.form.generator_tab_controller.table_model.rowCount(), 3)
        self.assertEqual(len(self.form.generator_tab_controller.table_model.display_data[1]), 30)
        self.assertNotEqual(len(self.form.generator_tab_controller.table_model.display_data[2]), 30)

    def test_create_fuzzing_list_view_context_menu(self):
        # Context menu should be empty if table is empty
        self.assertEqual(self.form.generator_tab_controller.table_model.rowCount(), 0)
        self.form.generator_tab_controller.ui.tableMessages.context_menu_pos = QPoint(0, 0)
        menu = self.form.generator_tab_controller.ui.listViewProtoLabels.create_context_menu()
        self.assertEqual(len(menu.actions()), 0)

        # Add data to test entries in context menu
        self.add_signal_to_form("fsk.complex")
        self.form.compare_frame_controller.add_protocol_label(0, 10, 0, 0, False)
        self.assertEqual(1, len(self.form.compare_frame_controller.proto_analyzer.protocol_labels))
        gframe = self.form.generator_tab_controller
        index = gframe.tree_model.createIndex(0, 0, gframe.tree_model.rootItem.children[0].children[0])
        mimedata = gframe.tree_model.mimeData([index])
        gframe.table_model.dropMimeData(mimedata, 1, -1, -1, gframe.table_model.createIndex(0, 0))

        self.assertGreater(self.form.generator_tab_controller.table_model.rowCount(), 0)
        # Select a row so there is a message for that fuzzing labels can be shown
        self.form.generator_tab_controller.ui.tableMessages.selectRow(0)
        menu = self.form.generator_tab_controller.ui.listViewProtoLabels.create_context_menu()
        n_items = len(menu.actions())
        self.assertGreater(n_items, 0)

    def test_add_column(self):
        # Add data to test
        self.add_signal_to_form("ask.complex")
        gframe = self.form.generator_tab_controller
        gframe.ui.cbViewType.setCurrentText("Bit")

        index = gframe.tree_model.createIndex(0, 0, gframe.tree_model.rootItem.children[0].children[0])
        mimedata = gframe.tree_model.mimeData([index])
        gframe.table_model.dropMimeData(mimedata, 1, -1, -1, gframe.table_model.createIndex(0, 0))
        self.assertEqual(self.form.generator_tab_controller.table_model.rowCount(), 1)

        l1 = len(self.form.generator_tab_controller.table_model.protocol.messages[0])
        self.form.generator_tab_controller.table_model.insert_column(0, [0])
        self.assertEqual(l1 + 1, len(self.form.generator_tab_controller.table_model.protocol.messages[0]))

        self.form.generator_tab_controller.generator_undo_stack.undo()
        self.assertEqual(l1, len(self.form.generator_tab_controller.table_model.protocol.messages[0]))

        self.form.generator_tab_controller.generator_undo_stack.redo()
        self.assertEqual(l1 + 1, len(self.form.generator_tab_controller.table_model.protocol.messages[0]))


    def __is_inv_proto(self, proto1: str, proto2: str):
        if len(proto1) != len(proto2):
            return False

        for c1, c2 in zip(proto1, proto2):
            if not self.__is_inv_bits(c1, c2):
                return False

        return True

    def __is_inv_bits(self, a: str, b: str):
        # We only check bits here
        if a not in ("0", "1") or b not in ("0", "1"):
            return True

        if a == "0" and b == "1":
            return True
        if a == "1" and b == "0":
            return True
        return False
