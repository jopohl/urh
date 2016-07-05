from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QDragMoveEvent, QDragEnterEvent, QPainter, QBrush, QColor, QPen, QDropEvent, QDragLeaveEvent, \
    QContextMenuEvent

from PyQt5.QtWidgets import QHeaderView, QAbstractItemView, QStyleOption, QMenu

from urh.models.GeneratorTableModel import GeneratorTableModel
from urh.ui.views.TableView import TableView


class GeneratorTableView(TableView):
    create_fuzzing_label_clicked = pyqtSignal(int, int, int)
    edit_fuzzing_label_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.dropIndicatorRect = QRect()
        self.drag_active = False
        self.show_pause_active = False
        self.pause_row = -1

    def model(self) -> GeneratorTableModel:
        return super().model()

    def dragEnterEvent(self, event: QDragEnterEvent):
        event.acceptProposedAction()
        self.drag_active = True

    def dragMoveEvent(self, event: QDragMoveEvent):
        pos = event.pos()
        row = self.rowAt(pos.y())

        index = self.model().createIndex(row, 0)  # this always get the default 0 column index

        rect = self.visualRect(index)
        rect_left = self.visualRect(index.sibling(index.row(), 0))
        rect_right = self.visualRect(index.sibling(index.row(),
            self.horizontalHeader().logicalIndex(self.model().columnCount() - 1)))  # in case section has been moved

        self.dropIndicatorPosition = self.position(event.pos(), rect)

        if self.dropIndicatorPosition == self.AboveItem:
            self.dropIndicatorRect = QRect(rect_left.left(), rect_left.top(), rect_right.right() - rect_left.left(), 0)
            event.accept()
        elif self.dropIndicatorPosition == self.BelowItem:
            self.dropIndicatorRect = QRect(rect_left.left(), rect_left.bottom(), rect_right.right() - rect_left.left(),
                0)
            event.accept()
        elif self.dropIndicatorPosition == self.OnItem:
            self.dropIndicatorRect = QRect(rect_left.left(), rect_left.bottom(), rect_right.right() - rect_left.left(),
                0)
            event.accept()
        else:
            self.dropIndicatorRect = QRect()

        # This is necessary or else the previously drawn rect won't be erased
        self.viewport().update()

    def __rect_for_row(self, row):
        index = self.model().createIndex(row, 0)  # this always get the default 0 column index
        # rect = self.visualRect(index)
        rect_left = self.visualRect(index.sibling(index.row(), 0))
        rect_right = self.visualRect(index.sibling(index.row(),
            self.horizontalHeader().logicalIndex(self.model().columnCount() - 1)))  # in case section has been moved
        return QRect(rect_left.left(), rect_left.bottom(), rect_right.right() - rect_left.left(), 0)

    def dropEvent(self, event: QDropEvent):
        self.drag_active = False
        row = self.rowAt(event.pos().y())
        index = self.model().createIndex(row, 0)  # this always get the default 0 column index
        rect = self.visualRect(index)
        dropIndicatorPosition = self.position(event.pos(), rect)
        if row == -1:
            row = self.model().row_count - 1
        elif dropIndicatorPosition == self.BelowItem or dropIndicatorPosition == self.OnItem:
            row += 1

        self.model().dropped_row = row

        super().dropEvent(event)

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.drag_active = False
        self.viewport().update()

        super().dragLeaveEvent(event)

    def position(self, pos, rect):
        r = QAbstractItemView.OnViewport
        # margin*2 must be smaller than row height, or the drop onItem rect won't show
        margin = 5
        if pos.y() - rect.top() < margin:
            r = QAbstractItemView.AboveItem
        elif rect.bottom() - pos.y() < margin:
            r = QAbstractItemView.BelowItem

        elif pos.y() - rect.top() > margin and rect.bottom() - pos.y() > margin:
            r = QAbstractItemView.OnItem

        return r

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        # in original implementation, it calls an inline function paintDropIndicator here
        self.paintDropIndicator(painter)
        self.paintPauseIndicator(painter)

    def paintDropIndicator(self, painter):
        if self.drag_active:
            opt = QStyleOption()
            opt.initFrom(self)
            opt.rect = self.dropIndicatorRect
            rect = opt.rect

            brush = QBrush(QColor(Qt.darkRed))

            if rect.height() == 0:
                pen = QPen(brush, 2, Qt.SolidLine)
                painter.setPen(pen)
                painter.drawLine(rect.topLeft(), rect.topRight())
            else:
                pen = QPen(brush, 2, Qt.SolidLine)
                painter.setPen(pen)
                painter.drawRect(rect)

    def paintPauseIndicator(self, painter):
        if self.show_pause_active:
            rect = self.__rect_for_row(self.pause_row)
            brush = QBrush(QColor(Qt.darkGreen))
            pen = QPen(brush, 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(rect.topLeft(), rect.topRight())

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()
        pos = event.pos()
        min_row, max_row, start, end = self.selection_range()

        selected_label_indx = self.model().get_selected_label_index(row=self.rowAt(event.pos().y()),column=self.columnAt(event.pos().x()))

        if selected_label_indx == -1:
            fuzzingAction = menu.addAction("Create Fuzzing Label...")
        else:
            fuzzingAction = menu.addAction("Edit Fuzzing Label...")

        menu.addSeparator()
        column_menu = menu.addMenu("Add column")

        insertColLeft = column_menu.addAction("on the left")
        insertColRight = column_menu.addAction("on the right")

        duplicateAction = menu.addAction("Duplicate Line")
        menu.addSeparator()
        clearAction = menu.addAction("Clear Table")

        if min_row == -1:
            fuzzingAction.setEnabled(False)

        if self.model().col_count == 0:
            clearAction.setEnabled(False)

        selected_rows = list(range(min_row, max_row + 1))

        action = menu.exec_(self.mapToGlobal(pos))
        if action == fuzzingAction:
            if selected_label_indx == -1:
                self.create_fuzzing_label_clicked.emit(min_row, start, end)
            else:
                self.edit_fuzzing_label_clicked.emit(selected_label_indx)
        elif action == clearAction:
            self.model().clear()
        elif action == duplicateAction:
            row = self.rowAt(event.pos().y())
            self.model().duplicate_row(row)
        elif action == insertColLeft:
            self.model().insert_column(start, selected_rows)
        elif action == insertColRight:
            self.model().insert_column(end, selected_rows)
