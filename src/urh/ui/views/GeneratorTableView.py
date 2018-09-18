from PyQt5.QtCore import Qt, QRect, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDragMoveEvent, QDragEnterEvent, QPainter, QBrush, QColor, QPen, QDropEvent, QDragLeaveEvent, \
    QContextMenuEvent, QIcon
from PyQt5.QtWidgets import QActionGroup, QInputDialog

from PyQt5.QtWidgets import QHeaderView, QAbstractItemView, QStyleOption, QMenu

from urh.models.GeneratorTableModel import GeneratorTableModel
from urh.ui.views.TableView import TableView


class GeneratorTableView(TableView):
    encodings_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.drop_indicator_rect = QRect()
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
                                                   self.horizontalHeader().logicalIndex(
                                                       self.model().columnCount() - 1)))  # in case section has been moved

        self.drop_indicator_position = self.position(event.pos(), rect)

        if self.drop_indicator_position == self.AboveItem:
            self.drop_indicator_rect = QRect(rect_left.left(), rect_left.top(), rect_right.right() - rect_left.left(), 0)
            event.accept()
        elif self.drop_indicator_position == self.BelowItem:
            self.drop_indicator_rect = QRect(rect_left.left(), rect_left.bottom(), rect_right.right() - rect_left.left(),
                                             0)
            event.accept()
        elif self.drop_indicator_position == self.OnItem:
            self.drop_indicator_rect = QRect(rect_left.left(), rect_left.bottom(), rect_right.right() - rect_left.left(),
                                             0)
            event.accept()
        else:
            self.drop_indicator_rect = QRect()

        # This is necessary or else the previously drawn rect won't be erased
        self.viewport().update()

    def __rect_for_row(self, row):
        index = self.model().createIndex(row, 0)  # this always get the default 0 column index
        # rect = self.visualRect(index)
        rect_left = self.visualRect(index.sibling(index.row(), 0))
        rect_right = self.visualRect(index.sibling(index.row(),
                                                   self.horizontalHeader().logicalIndex(
                                                       self.model().columnCount() - 1)))  # in case section has been moved
        return QRect(rect_left.left(), rect_left.bottom(), rect_right.right() - rect_left.left(), 0)

    def dropEvent(self, event: QDropEvent):
        self.drag_active = False
        row = self.rowAt(event.pos().y())
        index = self.model().createIndex(row, 0)  # this always get the default 0 column index
        rect = self.visualRect(index)
        drop_indicator_position = self.position(event.pos(), rect)
        if row == -1:
            row = self.model().row_count - 1
        elif drop_indicator_position == self.BelowItem or drop_indicator_position == self.OnItem:
            row += 1

        self.model().dropped_row = row

        super().dropEvent(event)

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.drag_active = False
        self.viewport().update()

        super().dragLeaveEvent(event)

    @staticmethod
    def position(pos, rect):
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
        self.paint_drop_indicator(painter)
        self.paint_pause_indicator(painter)

    def paint_drop_indicator(self, painter):
        if self.drag_active:
            opt = QStyleOption()
            opt.initFrom(self)
            opt.rect = self.drop_indicator_rect
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

    def paint_pause_indicator(self, painter):
        if self.show_pause_active:
            rect = self.__rect_for_row(self.pause_row)
            brush = QBrush(QColor(Qt.darkGreen))
            pen = QPen(brush, 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(rect.topLeft(), rect.topRight())

    def create_context_menu(self) -> QMenu:
        menu = super().create_context_menu()

        add_message_action = menu.addAction("Add empty message...")
        add_message_action.setIcon(QIcon.fromTheme("edit-table-insert-row-below"))
        add_message_action.triggered.connect(self.on_add_message_action_triggered)

        if not self.selection_is_empty:
            menu.addAction(self.copy_action)

        if self.model().row_count > 0:
            duplicate_action = menu.addAction("Duplicate line")
            duplicate_action.setIcon(QIcon.fromTheme("edit-table-insert-row-under"))
            duplicate_action.triggered.connect(self.on_duplicate_action_triggered)

            self._add_insert_column_menu(menu)

            menu.addSeparator()
            clear_action = menu.addAction("Clear table")
            clear_action.triggered.connect(self.on_clear_action_triggered)
            clear_action.setIcon(QIcon.fromTheme("edit-clear"))

        self.encoding_actions = {}

        if not self.selection_is_empty:
            selected_encoding = self.model().protocol.messages[self.selected_rows[0]].decoder
            for i in self.selected_rows:
                if self.model().protocol.messages[i].decoder != selected_encoding:
                    selected_encoding = None
                    break

            menu.addSeparator()
            encoding_group = QActionGroup(self)
            encoding_menu = menu.addMenu("Enforce encoding")

            for decoding in self.model().decodings:
                ea = encoding_menu.addAction(decoding.name)
                ea.setCheckable(True)
                ea.setActionGroup(encoding_group)
                if selected_encoding == decoding:
                    ea.setChecked(True)

                self.encoding_actions[ea] = decoding
                ea.triggered.connect(self.on_encoding_action_triggered)

        return menu

    @pyqtSlot()
    def on_duplicate_action_triggered(self):
        row = self.rowAt(self.context_menu_pos.y())
        self.model().duplicate_row(row)

    @pyqtSlot()
    def on_clear_action_triggered(self):
        self.model().clear()

    @pyqtSlot()
    def on_encoding_action_triggered(self):
        for row in self.selected_rows:
            self.model().protocol.messages[row].decoder = self.encoding_actions[self.sender()]
        self.encodings_updated.emit()

    @pyqtSlot()
    def on_add_message_action_triggered(self):
        row = self.rowAt(self.context_menu_pos.y())
        num_bits, ok = QInputDialog.getInt(self, self.tr("How many bits shall the new message have?"),
                                           self.tr("Number of bits:"), 42, 1)
        if ok:
            self.model().add_empty_row_behind(row, num_bits)
