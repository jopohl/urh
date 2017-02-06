from PyQt5.QtCore import QItemSelection
from PyQt5.QtCore import pyqtSignal, QItemSelectionModel, Qt
from PyQt5.QtGui import QContextMenuEvent, QDropEvent, QIcon
from PyQt5.QtWidgets import  QTreeView, QAbstractItemView, QMenu

from urh.models.ProtocolTreeModel import ProtocolTreeModel


class ProtocolTreeView(QTreeView):
    create_new_group_clicked = pyqtSignal()
    selection_changed = pyqtSignal()
    files_dropped_on_group = pyqtSignal(list, int)
    close_wanted = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def model(self) -> ProtocolTreeModel:
        return super().model()

    def selectionModel(self) -> QItemSelectionModel:
        return super().selectionModel()

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()
        new_group_action = menu.addAction(self.tr("Create a new group"))
        item = self.model().getItem(self.indexAt(event.pos()))
        selected_items = [self.model().getItem(index) for index in self.selectionModel().selectedIndexes()]
        selected_protocols = [item.protocol for item in selected_items if not item.is_group]
        delete_group_action = 42
        close_action = 42
        sort_group_elements_action = 4711
        move_to_group_actions = {}
        if item.is_group:
            delete_group_action = menu.addAction(self.tr("Delete Group"))
        elif item != self.model().rootItem:
            tree_items = self.model().protocol_tree_items
            other_groups = [i for i in tree_items.keys() if item not in tree_items[i]]

            if len(selected_protocols) > 0:
                close_action = menu.addAction(self.tr("Close"))
                close_action.setIcon(QIcon.fromTheme("window-close"))

            if len(other_groups) > 0:
                move_to_group_menu = menu.addMenu("Move to Group")
                for i in other_groups:
                    group_name = self.model().rootItem.child(i).data()
                    move_to_group_actions[move_to_group_menu.addAction(group_name)] = i

        if item != self.model().rootItem:
            menu.addSeparator()
            sort_group_elements_action = menu.addAction("Sort Group Elements")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == new_group_action:
            self.model().addGroup()
            self.model().update()
        elif action == delete_group_action:
            self.model().delete_group(item)
        elif action in move_to_group_actions.keys():
            i = move_to_group_actions[action]
            self.model().move_to_group(selected_items, i)
        elif action == close_action:
            self.close_wanted.emit(selected_protocols)
        elif action == sort_group_elements_action:
            if item.is_group:
                sortgroup_id = self.model().rootItem.index_of(item)
            else:
                sortgroup_id = self.model().rootItem.index_of(item.parent())
            self.model().sort_group(sortgroup_id)

    def selectionChanged(self, selection1: QItemSelection, selection2: QItemSelection):
        self.selection_changed.emit()
        super().selectionChanged(selection1, selection2)

    def dropEvent(self, event: QDropEvent):
        if len(event.mimeData().urls()) > 0:
            group_id = self.model().get_group_id_for_index(self.indexAt(event.pos()))
            self.files_dropped_on_group.emit(event.mimeData().urls(), group_id)
        else:
            super().dropEvent(event)
