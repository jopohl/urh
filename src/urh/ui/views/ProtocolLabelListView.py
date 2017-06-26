import numpy
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QContextMenuEvent, QKeySequence, QIcon
from PyQt5.QtWidgets import QListView, QAbstractItemView, QMenu, QAction

from urh.models.ProtocolLabelListModel import ProtocolLabelListModel


class ProtocolLabelListView(QListView):
    editActionTriggered = pyqtSignal(int)
    selection_changed = pyqtSignal()
    configureActionTriggered = pyqtSignal()
    auto_message_type_update_triggered = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)

        self.del_rows_action = QAction("Delete selected labels", self)
        self.del_rows_action.setShortcut(QKeySequence.Delete)
        self.del_rows_action.setIcon(QIcon.fromTheme("edit-delete"))
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

        min_row = min(rng.top() for rng in selected)
        max_row = max(rng.bottom() for rng in selected)

        return min_row, max_row

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()
        pos = event.pos()
        index = self.indexAt(pos)
        min_row, max_row = self.selection_range()

        edit_action = menu.addAction("Edit Protocol Label...")
        edit_action.setIcon(QIcon.fromTheme("configure"))

        assign_actions = []
        message_type_names = []

        if min_row > -1:
            menu.addAction(self.del_rows_action)
            message_type_names = [lset.name for lset in self.model().controller.proto_analyzer.message_types]

            try:
                proto_label = self.model().get_label_at(index.row())
                avail_message_types = []
                for message_type in self.model().controller.proto_analyzer.message_types:
                    if proto_label not in message_type:
                        avail_message_types.append(message_type)

                if avail_message_types:
                    assign_menu = menu.addMenu("Copy label(s) to message type")
                    assign_menu.setIcon(QIcon.fromTheme("edit-copy"))
                    assign_actions = [assign_menu.addAction(message_type.name) for message_type in avail_message_types]
            except IndexError:
                pass

        menu.addSeparator()
        show_all_action = menu.addAction("Show all")
        hide_all_action = menu.addAction("Hide all")

        menu.addSeparator()
        update_message_types_action = menu.addAction("Update automatically assigned message types")
        update_message_types_action.setIcon(QIcon.fromTheme("view-refresh"))
        configure_action = menu.addAction("Configure field types...")

        action = menu.exec_(self.mapToGlobal(pos))

        if action == edit_action:
            self.editActionTriggered.emit(index.row())
        elif action == show_all_action:
            self.model().showAll()
        elif action == hide_all_action:
            self.model().hideAll()
        elif action == configure_action:
            self.configureActionTriggered.emit()
        elif action == update_message_types_action:
            self.auto_message_type_update_triggered.emit()
        elif action in assign_actions:
            message_type_id = message_type_names.index(action.text())
            self.model().add_labels_to_message_type(min_row, max_row, message_type_id)

    def delete_rows(self):
        min_row, max_row = self.selection_range()
        if min_row > -1:
            self.model().delete_labels_at(min_row, max_row)

    def selectionChanged(self, QItemSelection, QItemSelection_1):
        self.selection_changed.emit()
        super().selectionChanged(QItemSelection, QItemSelection_1)
