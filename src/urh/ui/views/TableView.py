import numpy
import numpy as np
from PyQt5.QtCore import Qt, QItemSelectionModel, QItemSelection, pyqtSlot
from PyQt5.QtGui import QKeySequence, QKeyEvent, QFontMetrics, QIcon
from PyQt5.QtWidgets import QTableView, QApplication, QAction, QStyleFactory


class TableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.context_menu_pos = None  # type: QPoint

        self.copy_action = QAction("Copy selection", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_action.triggered.connect(self.on_copy_action_triggered)

        self.use_header_colors = False

    def selectionModel(self) -> QItemSelectionModel:
        return super().selectionModel()

    @property
    def selection_is_empty(self) -> bool:
        return self.selectionModel().selection().isEmpty()

    @property
    def selected_rows(self):
        min_row, max_row, _, _ = self.selection_range()
        if not self.selection_is_empty:
            selected_rows = list(range(min_row, max_row + 1))
        else:
            selected_rows = []

        return selected_rows

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

    def select(self, row_1, col_1, row_2, col_2):
        sel = QItemSelection()
        startindex = self.model().index(row_1, col_1)
        endindex = self.model().index(row_2, col_2)
        sel.select(startindex, endindex)
        self.selectionModel().select(sel, QItemSelectionModel.Select)

    def resize_columns(self):
        if not self.isVisible():
            return

        f = QFontMetrics(self.font())
        w = f.widthChar("0") + 2

        for i in range(10):
            self.setColumnWidth(i, 3*w)

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
            selected = self.selectionModel().selection()
            """:type: QtGui.QItemSelection """
            if selected.isEmpty():
                return

            min_row = numpy.min([rng.top() for rng in selected])
            max_row = numpy.max([rng.bottom() for rng in selected])
            start = numpy.min([rng.left() for rng in selected])
            end = numpy.max([rng.right() for rng in selected])

            self.setEnabled(False)
            self.setCursor(Qt.WaitCursor)
            self.model().delete_range(min_row, max_row, start, end)
            self.unsetCursor()
            self.setEnabled(True)
            self.setFocus()

        if event.matches(QKeySequence.Copy):
            self.on_copy_action_triggered()
            return

        if event.key() not in (Qt.Key_Right, Qt.Key_Left, Qt.Key_Up, Qt.Key_Down) \
                or event.modifiers() == Qt.ShiftModifier:
            super().keyPressEvent(event)
            return

        sel = self.selectionModel().selectedIndexes()
        cols = [i.column() for i in sel]
        rows = [i.row() for i in sel]
        if len(cols) == 0 or len(rows) == 0:
            super().keyPressEvent(event)
            return

        mincol, maxcol = numpy.min(cols), numpy.max(cols)
        minrow, maxrow = numpy.min(rows), numpy.max(rows)
        scroll_to_start = True

        if event.key() == Qt.Key_Right and maxcol < self.model().col_count - 1:
            maxcol += 1
            mincol += 1
            scroll_to_start = False
        elif event.key() == Qt.Key_Left and mincol > 0:
            mincol -= 1
            maxcol -= 1
        elif event.key() == Qt.Key_Down and maxrow < self.model().row_count - 1:
            first_unhidden = -1
            for row in range(maxrow + 1, self.model().row_count):
                if not self.isRowHidden(row):
                    first_unhidden = row
                    break

            if first_unhidden != -1:
                sel_len = maxrow - minrow
                maxrow = first_unhidden
                minrow = maxrow - sel_len
                scroll_to_start = False
        elif event.key() == Qt.Key_Up and minrow > 0:
            first_unhidden = -1
            for row in range(minrow - 1, -1, -1):
                if not self.isRowHidden(row):
                    first_unhidden = row
                    break

            if first_unhidden != -1:
                sel_len = maxrow - minrow
                minrow = first_unhidden
                maxrow = minrow + sel_len

        start = self.model().index(minrow, mincol)
        end = self.model().index(maxrow, maxcol)

        selctn = QItemSelection()
        selctn.select(start, end)
        self.selectionModel().setCurrentIndex(end, QItemSelectionModel.ClearAndSelect)
        self.selectionModel().select(selctn, QItemSelectionModel.ClearAndSelect)
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
