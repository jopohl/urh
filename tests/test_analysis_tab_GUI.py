import copy

from PyQt5.QtCore import QPoint, Qt, QModelIndex
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QMenu

from tests.QtTestCase import QtTestCase
from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.MainController import MainController
from urh.signalprocessing.FieldType import FieldType
from urh.ui.views.LabelValueTableView import LabelValueTableView


class TestAnalysisTabGUI(QtTestCase):
    def setUp(self):
        super().setUp()
        self.add_signal_to_form("two_participants.complex16s")
        assert isinstance(self.form, MainController)
        self.cfc = self.form.compare_frame_controller  # type: CompareFrameController
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxCenterOffset.setValue(-0.0574)
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxCenterOffset.editingFinished.emit()
        self.form.signal_tab_controller.signal_frames[0].ui.spinBoxTolerance.setValue(
            10
        )
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxTolerance.editingFinished.emit()

    def test_analyze_button_fsk(self):
        assert isinstance(self.cfc, CompareFrameController)
        self.add_signal_to_form("fsk.complex")
        self.cfc.assign_labels_action.setChecked(True)
        self.cfc.assign_message_type_action.setChecked(True)
        self.cfc.assign_participants_action.setChecked(True)
        self.cfc.ui.btnAnalyze.click()
        self.assertTrue(True)

    def test_analyze_button_enocean(self):
        self.add_signal_to_form("enocean.complex")
        w = self.form.signal_tab_controller.signal_frames[1].ui.spinBoxCenterOffset
        w.setValue(0)
        QTest.keyClick(w, Qt.Key_Enter)
        w = self.form.signal_tab_controller.signal_frames[1].ui.spinBoxNoiseTreshold
        w.setValue(0.0111)
        QTest.keyClick(w, Qt.Key_Enter)
        self.cfc.assign_labels_action.setChecked(True)
        self.cfc.assign_message_type_action.setChecked(True)
        self.cfc.assign_participants_action.setChecked(True)
        self.cfc.ui.btnAnalyze.click()
        self.assertTrue(True)

    def test_table_selection(self):
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.cfc.ui.cbProtoView.setCurrentIndex(0)
        self.cfc.ui.tblViewProtocol.selectRow(1)
        QApplication.instance().processEvents()
        self.assertEqual(
            self.cfc.ui.lBitsSelection.text(),
            self.cfc.proto_analyzer.messages[1].plain_bits_str,
        )

        self.cfc.ui.tblViewProtocol.clearSelection()
        QApplication.instance().processEvents()
        self.assertEqual("", self.cfc.ui.lBitsSelection.text())

        self.cfc.ui.tblViewProtocol.select(0, 0, 0, 3)
        QApplication.instance().processEvents()
        self.assertEqual("1010", self.cfc.ui.lBitsSelection.text())
        self.cfc.ui.cbProtoView.setCurrentIndex(1)
        QApplication.instance().processEvents()

        min_row, max_row, start, end = self.cfc.ui.tblViewProtocol.selection_range()
        self.assertEqual(min_row, 0)
        self.assertEqual(max_row, 0)
        self.assertEqual(start, 0)
        self.assertEqual(end, 1)

    def test_search(self):
        search_str = "100110001"
        self.cfc.ui.cbProtoView.setCurrentIndex(0)
        self.cfc.ui.tblViewProtocol.clearSelection()
        self.cfc.ui.lineEditSearch.setText(search_str)
        self.cfc.ui.btnSearchSelectFilter.click()

        selected_now = self.cfc.ui.tblViewProtocol.selectedIndexes()
        self.assertEqual(
            len(self.cfc.ui.tblViewProtocol.selectedIndexes()), len(search_str)
        )

        self.cfc.ui.btnNextSearch.click()
        self.assertNotEqual(selected_now, self.cfc.ui.tblViewProtocol.selectedIndexes())

        self.cfc.ui.btnPrevSearch.click()
        self.assertEqual(selected_now, self.cfc.ui.tblViewProtocol.selectedIndexes())

        self.cfc.select_action.trigger()
        self.assertEqual(self.cfc.ui.btnSearchSelectFilter.text(), "Select all")
        self.cfc.ui.btnSearchSelectFilter.click()
        self.assertGreater(
            len(self.cfc.ui.tblViewProtocol.selectedIndexes()), len(selected_now)
        )

        self.cfc.filter_action.trigger()
        self.assertEqual(self.cfc.ui.btnSearchSelectFilter.text(), "Filter")
        self.cfc.ui.btnSearchSelectFilter.click()
        hidden_rows = [
            i
            for i in range(self.cfc.protocol_model.row_count)
            if self.cfc.ui.tblViewProtocol.isRowHidden(i)
        ]

        self.assertEqual(hidden_rows, [0, 5, 6, 10, 13, 14, 16, 17])

    def test_search_hex(self):
        search_str = "aaaaaaaa"
        self.cfc.ui.cbProtoView.setCurrentIndex(1)
        self.cfc.ui.tblViewProtocol.clearSelection()
        self.cfc.ui.lineEditSearch.setText(search_str)
        self.cfc.ui.btnSearchSelectFilter.click()

        self.assertEqual(self.cfc.ui.lSearchTotal.text(), "18")

    def test_search_without_results(self):
        search_str = "deadbeef42"
        self.cfc.ui.cbProtoView.setCurrentIndex(1)
        self.cfc.ui.tblViewProtocol.clearSelection()
        self.cfc.ui.lineEditSearch.setText(search_str)

        self.assertEqual(
            self.cfc.ui.lineEditSearch.text(), search_str, msg="before search"
        )
        self.cfc.ui.btnSearchSelectFilter.click()
        self.assertEqual(self.cfc.ui.lSearchTotal.text(), "-")
        self.assertEqual(
            self.cfc.ui.lineEditSearch.text(), search_str, msg="after search"
        )

    def test_show_diff(self):
        self.cfc.ui.cbProtoView.setCurrentIndex(0)

        hidden_columns_before = [
            i
            for i in range(self.cfc.protocol_model.col_count)
            if self.cfc.ui.tblViewProtocol.isColumnHidden(i)
        ]
        self.assertEqual(len(hidden_columns_before), 0)

        self.cfc.ui.chkBoxShowOnlyDiffs.click()
        self.assertTrue(self.cfc.ui.cbShowDiffs.isChecked())

        hidden_columns_now = [
            i
            for i in range(self.cfc.protocol_model.col_count)
            if self.cfc.ui.tblViewProtocol.isColumnHidden(i)
        ]

        self.assertNotEqual(hidden_columns_before, hidden_columns_now)

        self.cfc.ui.chkBoxOnlyShowLabelsInProtocol.click()

        hidden_columns_now = [
            i
            for i in range(self.cfc.protocol_model.col_count)
            if self.cfc.ui.tblViewProtocol.isColumnHidden(i)
        ]

        self.assertEqual(len(hidden_columns_now), self.cfc.protocol_model.col_count)

        self.cfc.ui.cbProtoView.setCurrentIndex(1)

        self.assertEqual(self.cfc.protocol_model.refindex, 0)
        self.assertEqual(self.cfc.protocol_model.proto_view, 1)

        self.cfc.ui.cbProtoView.setCurrentIndex(2)

        self.assertEqual(self.cfc.protocol_model.refindex, 0)
        self.assertEqual(self.cfc.protocol_model.proto_view, 2)

    def test_add_message_type(self):
        self.assertEqual(len(self.cfc.proto_analyzer.message_types), 1)
        self.cfc.ui.btnAddMessagetype.click()
        self.assertEqual(len(self.cfc.proto_analyzer.message_types), 2)
        self.cfc.message_type_table_model.delete_message_type_at(1)
        self.assertEqual(len(self.cfc.proto_analyzer.message_types), 1)

    def test_create_context_menu(self):
        self.cfc.proto_tree_model.rootItem.child(0).show = False
        QApplication.instance().processEvents()

        self.assertEqual(self.cfc.protocol_model.rowCount(), 0)
        self.cfc.ui.tblViewProtocol.context_menu_pos = QPoint(0, 0)
        QApplication.instance().processEvents()

        menu = self.cfc.ui.tblViewProtocol.create_context_menu()
        texts = [a.text() for a in menu.actions()]
        # Add protocol label should not be there if table is empty
        self.assertFalse(any("label" in text.lower() for text in texts))

    def test_show_in_interpretation(self):
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.assertEqual(self.form.ui.tabWidget.currentIndex(), 1)
        self.cfc.ui.cbProtoView.setCurrentIndex(0)

        self.cfc.ui.tblViewProtocol.selectRow(1)
        min_row, max_row, start, end = self.cfc.ui.tblViewProtocol.selection_range()
        self.cfc.ui.tblViewProtocol.show_interpretation_clicked.emit(
            min_row, start, max_row, end - 1
        )
        self.assertEqual(self.form.ui.tabWidget.currentIndex(), 0)
        self.assertFalse(
            self.form.signal_tab_controller.signal_frames[
                0
            ].ui.gvSignal.selection_area.is_empty
        )

    def test_hide_row(self):
        num_messages = len(self.cfc.proto_analyzer.messages)
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.assertGreater(num_messages, 0)
        self.assertEqual(self.cfc.protocol_model.rowCount(), num_messages)
        self.cfc.ui.tblViewProtocol.hide_rows(0)
        self.assertTrue(self.cfc.ui.tblViewProtocol.isRowHidden(0))
        self.assertEqual(len(self.cfc.protocol_model.hidden_rows), 1)

        for msg in range(1, num_messages):
            self.assertFalse(self.cfc.ui.tblViewProtocol.isRowHidden(msg))

        self.form.ui.tabWidget.setCurrentIndex(2)
        QApplication.instance().processEvents()
        self.form.ui.tabWidget.setCurrentIndex(1)
        QApplication.instance().processEvents()
        self.assertEqual(self.cfc.protocol_model.rowCount(), num_messages)
        self.assertTrue(self.cfc.ui.tblViewProtocol.isRowHidden(0))

        for msg in range(1, num_messages):
            self.assertFalse(self.cfc.ui.tblViewProtocol.isRowHidden(msg))

        self.assertEqual(len(self.cfc.protocol_model.hidden_rows), 1)

    def test_refresh_existing_decodings(self):
        self.assertEqual(
            self.cfc.proto_analyzer.messages[0].decoder, self.cfc.decodings[0]
        )
        decoder = copy.deepcopy(self.cfc.proto_analyzer.messages[0].decoder)
        decoder.chain.append(decoder.code_invert)
        self.cfc.proto_analyzer.messages[0].decoder = decoder
        self.assertNotEqual(
            self.cfc.proto_analyzer.messages[0].decoder, self.cfc.decodings[0]
        )

        self.cfc.refresh_existing_encodings()
        self.assertEqual(
            self.cfc.proto_analyzer.messages[0].decoder, self.cfc.decodings[0]
        )

    def test_get_labels_from_selection(self):
        self.cfc.ui.tblViewProtocol.selectRow(1)
        self.assertEqual(
            len(
                self.cfc.get_labels_from_selection(
                    *self.cfc.ui.tblViewProtocol.selection_range()
                )
            ),
            0,
        )

    def test_refresh_field_types_for_labels(self):
        self.cfc.add_protocol_label(0, 10, 0, 0, edit_label_name=False)
        n = len(self.cfc.field_types)
        self.cfc.refresh_field_types_for_labels()
        self.assertEqual(len(self.cfc.field_types), n)

    def test_tree_view_selection_changed(self):
        self.cfc.proto_tree_model.addGroup()
        self.cfc.proto_tree_model.addGroup()
        QApplication.instance().processEvents()
        self.assertEqual(len(self.cfc.active_group_ids), 1)
        self.cfc.ui.treeViewProtocols.selectAll()
        self.cfc.ui.treeViewProtocols.selection_changed.emit()
        QApplication.instance().processEvents()
        self.assertEqual(len(self.cfc.active_group_ids), 1)

    def test_tree_view_drop_mime_data(self):
        # Drop signal to new group
        self.cfc.proto_tree_model.addGroup("Test group")
        self.assertEqual(len(self.cfc.groups), 2)
        self.assertEqual(self.cfc.groups[0].num_protocols, 1)
        self.assertEqual(self.cfc.groups[1].num_protocols, 0)
        self.cfc.proto_tree_model.update()

        self.cfc.show()
        model = self.cfc.proto_tree_model

        group_1_index = model.index(0, 0, QModelIndex())
        signal_index = model.index(0, 0, group_1_index)

        group_2_index = model.index(1, 0, QModelIndex())
        self.assertEqual(group_2_index.internalPointer().group.name, "Test group")
        mimedata = model.mimeData([signal_index])
        model.dropMimeData(mimedata, Qt.MoveAction, 0, 0, group_2_index)
        self.assertEqual(self.cfc.groups[0].num_protocols, 0)
        self.assertEqual(self.cfc.groups[1].num_protocols, 1)

        # Drop group to another position
        self.assertEqual(self.cfc.groups[0].name, "New Group")
        self.assertEqual(self.cfc.groups[1].name, "Test group")
        mimedata = model.mimeData([group_2_index])
        model.dropMimeData(mimedata, Qt.MoveAction, 0, 0, group_1_index)
        self.assertEqual(self.cfc.groups[0].name, "Test group")
        self.assertEqual(self.cfc.groups[0].num_protocols, 1)
        self.assertEqual(self.cfc.groups[1].name, "New Group")
        self.assertEqual(self.cfc.groups[1].num_protocols, 0)

    def test_remove_label(self):
        self.cfc.add_protocol_label(10, 20, 2, 0, edit_label_name=False)
        self.assertEqual(self.cfc.label_value_model.rowCount(), 1)
        self.cfc.label_value_model.delete_label_at(0)
        self.assertEqual(self.cfc.label_value_model.rowCount(), 0)

    def test_label_tooltip(self):
        self.cfc.ui.cbProtoView.setCurrentIndex(0)
        self.cfc.add_protocol_label(0, 16, 2, 0, edit_label_name=False)
        model = self.cfc.label_value_model
        model.setData(model.index(0, 0), "test", Qt.EditRole)
        table_model = self.cfc.protocol_model
        for i in range(0, 16):
            self.assertEqual(
                table_model.data(table_model.index(2, i), Qt.ToolTipRole),
                "test",
                msg=str(i),
            )

        for i in range(17, 100):
            self.assertEqual(
                table_model.data(table_model.index(2, i), Qt.ToolTipRole),
                "",
                msg=str(i),
            )

        self.cfc.add_protocol_label(20, 24, 2, 0, edit_label_name=False)
        checksum_field_type = next(
            ft
            for ft in self.cfc.field_types
            if ft.function == FieldType.Function.CHECKSUM
        )
        model.setData(model.index(1, 0), checksum_field_type.caption, Qt.EditRole)
        for i in range(20, 24):
            self.assertIn(
                "Expected", table_model.data(table_model.index(2, i), Qt.ToolTipRole)
            )

        for i in range(0, 20):
            self.assertNotIn(
                "Expected", table_model.data(table_model.index(2, i), Qt.ToolTipRole)
            )

    def test_protocol_tree_context_menu(self):
        self.cfc.ui.treeViewProtocols.context_menu_pos = QPoint(0, 0)
        menu = self.cfc.ui.treeViewProtocols.create_context_menu()
        actions = ["Create a new group", "Sort Group Elements", "Delete group"]
        menu_action_names = [
            action.text() for action in menu.actions() if action.text()
        ]
        for action in menu_action_names:
            self.assertIn(action, actions)

    def test_label_value_table(self):
        table = self.cfc.ui.tblLabelValues  # type: LabelValueTableView
        model = table.model()
        self.assertEqual(model.rowCount(), 0)
        self.cfc.add_protocol_label(45, 56, 0, 0, edit_label_name=False)
        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.data(model.index(0, 2)), "Bit")
        self.assertEqual(model.data(model.index(0, 4)), "000011001110")

        model.setData(model.index(0, 2), 1, role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 2)), "Hex")
        self.assertEqual(model.data(model.index(0, 4)), "0ce")

        model.setData(model.index(0, 2), 2, role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 2)), "ASCII")

        model.setData(model.index(0, 2), 3, role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 2)), "Decimal")
        self.assertEqual(model.data(model.index(0, 4)), "206")

        model.setData(model.index(0, 2), 4, role=Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 2)), "BCD")
        self.assertEqual(model.data(model.index(0, 4)), "0??")

        self.assertIn("display type", model.data(model.index(0, 2), Qt.ToolTipRole))
        self.assertIn("bit order", model.data(model.index(0, 3), Qt.ToolTipRole))

        lbl = self.cfc.proto_analyzer.default_message_type[0]
        self.assertEqual(lbl.display_endianness, "big")
        model.setData(model.index(0, 3), "MSB/LE", role=Qt.EditRole)
        self.assertEqual(lbl.display_endianness, "little")
        model.setData(model.index(0, 3), "LSB/BE", role=Qt.EditRole)
        self.assertEqual(lbl.display_endianness, "big")

    def test_label_list_view(self):
        menus_before = [
            w for w in QApplication.topLevelWidgets() if isinstance(w, QMenu)
        ]

        global context_menu
        context_menu = None  # type: QMenu

        def on_timeout():
            global context_menu
            context_menu = next(
                w
                for w in QApplication.topLevelWidgets()
                if w.parent() is None and isinstance(w, QMenu) and w not in menus_before
            )
            context_menu.close()

        self.cfc.add_protocol_label(10, 20, 0, 0, False)
        self.cfc.add_message_type()
        self.assertEqual(self.cfc.message_type_table_model.rowCount(), 2)

        self.cfc.ui.tblViewProtocol.selectRow(0)
        self.assertEqual(self.cfc.ui.tblLabelValues.model().rowCount(), 1)
        self.cfc.ui.tblLabelValues.selectAll()

        timer = QTimer(self.cfc)
        timer.setSingleShot(True)
        timer.timeout.connect(on_timeout)
        timer.start(1)

        self.cfc.ui.tblLabelValues.contextMenuEvent(
            QContextMenuEvent(QContextMenuEvent.Mouse, QPoint(0, 0))
        )

        names = [action.text() for action in context_menu.actions()]
        self.assertIn("Edit...", names)

    def test_create_label_dialog(self):
        self.cfc.add_protocol_label(10, 20, 0, 0, False)
        dialog = self.cfc.create_protocol_label_dialog()
        self.assertIsNotNone(dialog)

    def test_alignment(self):
        assert isinstance(self.cfc, CompareFrameController)
        self.form.close_all_files()
        self.form.add_files([self.get_path_for_filename("misaligned.txt")])
        self.assertEqual(self.cfc.protocol_model.row_count, 16)

        aligned = True
        pattern = "6768676"
        for i in range(self.cfc.protocol_model.row_count):
            for j in range(len(pattern)):
                if (
                    self.cfc.protocol_model.data(
                        self.cfc.protocol_model.index(i, j + 11)
                    )
                    != pattern[j]
                ):
                    aligned = False
                    break

        self.assertFalse(aligned)

        self.cfc.ui.cbProtoView.setCurrentIndex(1)
        self.cfc.align_action.trigger()
        self.cfc.ui.lineEditSearch.setText(pattern)
        self.cfc.ui.btnSearchSelectFilter.click()

        aligned = True
        for i in range(self.cfc.protocol_model.row_count):
            for j in range(len(pattern)):
                if (
                    self.cfc.protocol_model.data(
                        self.cfc.protocol_model.index(i, j + 11)
                    )
                    != pattern[j]
                ):
                    aligned = False
                    break

        self.assertTrue(aligned)
