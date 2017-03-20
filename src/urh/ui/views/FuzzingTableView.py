from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTableView, QApplication
from PyQt5.QtGui import QKeyEvent
import numpy


class FuzzingTableView(QTableView):
    deletion_wanted = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def resize_me(self):
        QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        w = self.font().pointSize() + 2
        for i in range(10):
            self.setColumnWidth(i, 2 * w)
        for i in range(10, self.model().col_count):
            self.setColumnWidth(i, w * len(str(i + 1)))
        QApplication.instance().restoreOverrideCursor()

    def selection_range(self):
        """
        :rtype: int, int, int, int
        """
        selected = self.selectionModel().selection()
        """:type: QItemSelection """

        if selected.isEmpty():
            return -1, -1, -1, -1

        min_row = numpy.min([rng.top() for rng in selected])
        max_row = numpy.max([rng.bottom() for rng in selected])
        start = numpy.min([rng.left() for rng in selected])
        end = numpy.max([rng.right() for rng in selected]) + 1

        return min_row, max_row, start, end

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            selected = self.selectionModel().selection()
            """:type: QtGui.QItemSelection """
            if selected.isEmpty():
                return

            min_row = numpy.min([rng.top() for rng in selected])
            max_row = numpy.max([rng.bottom() for rng in selected])
            self.deletion_wanted.emit(min_row, max_row)

        else:
            super().keyPressEvent(event)
