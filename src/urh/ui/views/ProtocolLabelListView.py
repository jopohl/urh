from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QContextMenuEvent, QKeySequence
from PyQt5.QtWidgets import QListView, QAbstractItemView, QMenu, QAction
import numpy

from urh.models.ProtocolLabelListModel import ProtocolLabelListModel


class ProtocolLabelListView(QListView):
    editActionTriggered = pyqtSignal(int)
    selection_changed = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)

        self.del_rows_action = QAction("Delete selected labels", self)
        self.del_rows_action.setShortcut(QKeySequence.Delete)
        self.del_rows_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.del_rows_action.triggered.connect(self.delete_rows)

        self.addAction(self.del_rows_action)



    def model(self) -> ProtocolLabelListModel:
        return super().model()

    def selection_range(self):
        """
        :rtype: int, int
        """
        selected = self.selectionModel().selection()
        """:type: QItemSelection """

        if selected.isEmpty():
            return -1, -1

        min_row = numpy.min([rng.top() for rng in selected])
        max_row = numpy.max([rng.bottom() for rng in selected])

        return min_row, max_row


    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()
        pos = event.pos()
        index = self.indexAt(pos)
        min_row, max_row = self.selection_range()

        editAction = menu.addAction("Edit Protocol Label...")

        assign_actions = []
        labelset_names = []


        if min_row > -1:
            menu.addAction(self.del_rows_action)
            labelset_names = [lset.name for lset in self.model().controller.proto_analyzer.labelsets]

            try:
                proto_label = self.model().get_label_at(index.row())
                avail_labelsets = []
                for lblset in self.model().controller.proto_analyzer.labelsets:
                    if proto_label not in lblset:
                        avail_labelsets.append(lblset)

                if avail_labelsets:
                    assign_menu = menu.addMenu("Copy label(s) to labelset")
                    assign_actions = [assign_menu.addAction(labelset.name) for labelset in avail_labelsets]
            except IndexError:
                pass

        menu.addSeparator()
        showAllAction = menu.addAction("Show all")
        hideAllAction = menu.addAction("Hide all")

        action = menu.exec_(self.mapToGlobal(pos))

        if action == editAction:
            self.editActionTriggered.emit(index.row())
        elif action == showAllAction:
            self.model().showAll()
        elif action == hideAllAction:
            self.model().hideAll()
        elif action in assign_actions:
            labelset_id = labelset_names.index(action.text())
            self.model().add_labels_to_labelset(min_row, max_row, labelset_id)


    def delete_rows(self):
        min_row, max_row = self.selection_range()
        if min_row > -1:
            self.model().delete_labels_at(min_row, max_row)

    def selectionChanged(self, QItemSelection, QItemSelection_1):
        self.selection_changed.emit()
        super().selectionChanged(QItemSelection, QItemSelection_1)