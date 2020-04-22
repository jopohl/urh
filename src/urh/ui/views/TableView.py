import numpy as np
from PyQt5.QtCore import Qt, QItemSelectionModel, QItemSelection, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QKeySequence, QKeyEvent, QFontMetrics, QIcon, QContextMenuEvent
from PyQt5.QtWidgets import QTableView, QApplication, QAction, QStyleFactory, QMenu


class TableView(QTableView):
    create_label_triggered = pyqtSignal(int, int, int)
    edit_label_triggered = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.context_menu_pos = None  # type: QPoint

        self.copy_action = QAction("Copy selection", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_action.triggered.connect(self.on_copy_action_triggered)

        self.use_header_colors = False

        self.original_font_size = self.font().pointSize()
        self.original_header_font_sizes = {"vertical": self.verticalHeader().font().pointSize(),
                                           "horizontal": self.horizontalHeader().font().pointSize()}

        self.zoom_in_action = QAction(self.tr("Zoom in"), self)
        self.zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        self.zoom_in_action.triggered.connect(self.on_zoom_in_action_triggered)
        self.zoom_in_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.zoom_in_action.setIcon(QIcon.fromTheme("zoom-in"))
        self.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction(self.tr("Zoom out"), self)
        self.zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        self.zoom_out_action.triggered.connect(self.on_zoom_out_action_triggered)
        self.zoom_out_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.zoom_out_action.setIcon(QIcon.fromTheme("zoom-out"))
        self.addAction(self.zoom_out_action)

        self.zoom_original_action = QAction(self.tr("Zoom original"), self)
        self.zoom_original_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_0))
        self.zoom_original_action.triggered.connect(self.on_zoom_original_action_triggered)
        self.zoom_original_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.zoom_original_action.setIcon(QIcon.fromTheme("zoom-original"))
        self.addAction(self.zoom_original_action)

        self.horizontalHeader().setMinimumSectionSize(0)

    def _add_insert_column_menu(self, menu):
        column_menu = menu.addMenu("Insert column")

        insert_column_left_action = column_menu.addAction("on the left")
        insert_column_left_action.triggered.connect(self.on_insert_column_left_action_triggered)
        insert_column_left_action.setIcon(QIcon.fromTheme("edit-table-insert-column-left"))
        insert_column_right_action = column_menu.addAction("on the right")
        insert_column_right_action.setIcon(QIcon.fromTheme("edit-table-insert-column-right"))
        insert_column_right_action.triggered.connect(self.on_insert_column_right_action_triggered)

    def selectionModel(self) -> QItemSelectionModel:
        return super().selectionModel()

    def set_font_size(self, n: int):
        if n < 1:
            return
        font = self.font()

        if n <= self.original_font_size:
            font.setPointSize(n)
            self.setFont(font)

        if n <= self.original_header_font_sizes["horizontal"]:
            hheader_font = self.horizontalHeader().font()
            hheader_font.setPointSize(n)
            self.horizontalHeader().setFont(hheader_font)

        if n <= self.original_header_font_sizes["vertical"]:
            vheader_font = self.verticalHeader().font()
            vheader_font.setPointSize(n)
            self.verticalHeader().setFont(vheader_font)

        self.resize_columns()

    @property
    def selection_is_empty(self) -> bool:
        return self.selectionModel().selection().isEmpty()

    @property
    def selected_rows(self):
        rows = set()
        for index in self.selectionModel().selectedIndexes():
            rows.add(index.row())

        return sorted(rows)

    @pyqtSlot()
    def on_zoom_in_action_triggered(self):
        self.set_font_size(self.font().pointSize() + 1)

    @pyqtSlot()
    def on_zoom_out_action_triggered(self):
        self.set_font_size(self.font().pointSize() - 1)

    @pyqtSlot()
    def on_zoom_original_action_triggered(self):
        self.set_font_size(self.original_font_size)

    def selection_range(self):
        """
        :rtype: int, int, int, int
        """
        selected = self.selectionModel().selection()  # type: QItemSelection
        if self.selection_is_empty:
            return -1, -1, -1, -1

        def range_to_tuple(rng):
            return rng.row(), rng.column()

        top_left = min(range_to_tuple(rng.topLeft()) for rng in selected)
        bottom_right = max(range_to_tuple(rng.bottomRight()) for rng in selected)

        return top_left[0], bottom_right[0], top_left[1], bottom_right[1] + 1

    def create_context_menu(self) -> QMenu:
        menu = QMenu()
        if self.context_menu_pos is None:
            return menu

        selected_label_index = self.model().get_selected_label_index(row=self.rowAt(self.context_menu_pos.y()),
                                                                     column=self.columnAt(self.context_menu_pos.x()))

        if self.model().row_count > 0:
            if selected_label_index == -1:
                label_action = menu.addAction("Create label...")
                label_action.setIcon(QIcon.fromTheme("list-add"))
            else:
                label_action = menu.addAction("Edit label...")
                label_action.setIcon(QIcon.fromTheme("configure"))

            label_action.triggered.connect(self.on_create_or_edit_label_action_triggered)
            menu.addSeparator()

            zoom_menu = menu.addMenu("Zoom font size")
            zoom_menu.addAction(self.zoom_in_action)
            zoom_menu.addAction(self.zoom_out_action)
            zoom_menu.addAction(self.zoom_original_action)
            menu.addSeparator()

        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.context_menu_pos = event.pos()
        menu = self.create_context_menu()
        menu.exec_(self.mapToGlobal(event.pos()))

        self.context_menu_pos = None

    def select(self, row_1, col_1, row_2, col_2):
        selection = QItemSelection()
        start_index = self.model().index(row_1, col_1)
        end_index = self.model().index(row_2, col_2)
        selection.select(start_index, end_index)
        self.selectionModel().select(selection, QItemSelectionModel.Select)

    def resize_columns(self):
        if not self.isVisible():
            return

        w = QFontMetrics(self.font()).widthChar("0") + 2
        for i in range(10):
            self.setColumnWidth(i, 3 * w)

        QApplication.instance().processEvents()
        for i in range(9, self.model().columnCount()):
            self.setColumnWidth(i, w * (len(str(i + 1)) + 1))
            if i % 10 == 0:
                QApplication.instance().processEvents()

    def resize_vertical_header(self):
        num_rows = self.model().rowCount()
        if self.isVisible() and num_rows > 0:
            hd = self.model().headerData
            max_len = np.max([len(str(hd(i, Qt.Vertical, Qt.DisplayRole))) for i in range(num_rows)])
            w = (self.font().pointSize() + 2) * max_len

            # https://github.com/jopohl/urh/issues/182
            rh = self.verticalHeader().defaultSectionSize()

            for i in range(num_rows):
                self.verticalHeader().resizeSection(i, w)
                self.setRowHeight(i, rh)
                if i % 10 == 0:
                    QApplication.instance().processEvents()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            min_row, max_row, start, end = self.selection_range()
            if min_row == max_row == start == end == -1:
                return

            self.setEnabled(False)
            self.setCursor(Qt.WaitCursor)
            self.model().delete_range(min_row, max_row, start, end - 1)
            self.unsetCursor()
            self.setEnabled(True)
            self.setFocus()

        if event.matches(QKeySequence.Copy):
            self.on_copy_action_triggered()
            return

        if event.key() == Qt.Key_Space:
            min_row, max_row, start, _ = self.selection_range()
            if start == -1:
                return

            self.model().insert_column(start, list(range(min_row, max_row + 1)))

        if event.key() not in (Qt.Key_Right, Qt.Key_Left, Qt.Key_Up, Qt.Key_Down) \
                or event.modifiers() == Qt.ShiftModifier:
            super().keyPressEvent(event)
            return

        min_row, max_row, min_col, max_col = self.selection_range()
        if min_row == max_row == min_col == max_col == -1:
            super().keyPressEvent(event)
            return

        max_col -= 1
        scroll_to_start = True

        if event.key() == Qt.Key_Right and max_col < self.model().col_count - 1:
            max_col += 1
            min_col += 1
            scroll_to_start = False
        elif event.key() == Qt.Key_Left and min_col > 0:
            min_col -= 1
            max_col -= 1
        elif event.key() == Qt.Key_Down and max_row < self.model().row_count - 1:
            first_unhidden = -1
            for row in range(max_row + 1, self.model().row_count):
                if not self.isRowHidden(row):
                    first_unhidden = row
                    break

            if first_unhidden != -1:
                sel_len = max_row - min_row
                max_row = first_unhidden
                min_row = max_row - sel_len
                scroll_to_start = False
        elif event.key() == Qt.Key_Up and min_row > 0:
            first_unhidden = -1
            for row in range(min_row - 1, -1, -1):
                if not self.isRowHidden(row):
                    first_unhidden = row
                    break

            if first_unhidden != -1:
                sel_len = max_row - min_row
                min_row = first_unhidden
                max_row = min_row + sel_len

        start = self.model().index(min_row, min_col)
        end = self.model().index(max_row, max_col)

        selection = QItemSelection()
        selection.select(start, end)
        self.setCurrentIndex(start)
        self.selectionModel().setCurrentIndex(end, QItemSelectionModel.ClearAndSelect)
        self.selectionModel().select(selection, QItemSelectionModel.ClearAndSelect)
        if scroll_to_start:
            self.scrollTo(start)
        else:
            self.scrollTo(end)

    @pyqtSlot()
    def on_copy_action_triggered(self):
        cells = self.selectedIndexes()
        cells.sort()

        current_row = 0
        text = ""

        for cell in cells:
            if len(text) > 0 and cell.row() != current_row:
                text += "\n"
            current_row = cell.row()
            if cell.data() is not None:
                text += str(cell.data())

        QApplication.instance().clipboard().setText(text)

    @pyqtSlot(bool)
    def on_vertical_header_color_status_changed(self, use_colors: bool):
        if use_colors == self.use_header_colors:
            return

        self.use_header_colors = use_colors
        header = self.verticalHeader()
        if self.use_header_colors:
            header.setStyle(QStyleFactory.create("Fusion"))
        else:
            header.setStyle(QStyleFactory.create(""))

        self.setVerticalHeader(header)

    @pyqtSlot()
    def on_insert_column_left_action_triggered(self):
        self.model().insert_column(self.selection_range()[2], self.selected_rows)

    @pyqtSlot()
    def on_insert_column_right_action_triggered(self):
        self.model().insert_column(self.selection_range()[3], self.selected_rows)

    @pyqtSlot()
    def on_create_or_edit_label_action_triggered(self):
        selected_label_index = self.model().get_selected_label_index(row=self.rowAt(self.context_menu_pos.y()),
                                                                     column=self.columnAt(self.context_menu_pos.x()))
        if selected_label_index == -1:
            min_row, max_row, start, end = self.selection_range()
            self.create_label_triggered.emit(min_row, start, end)
        else:
            self.edit_label_triggered.emit(selected_label_index)
