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
        newGroupAction = menu.addAction(self.tr("Create a new group"))
        item = self.model().getItem(self.indexAt(event.pos()))
        selected_items = [self.model().getItem(index) for index in self.selectionModel().selectedIndexes()]
        selected_protos = [item.protocol for item in selected_items if not item.is_group]
        deleteGroupAction = 42
        close_action = 42
        sortGroupElementsAction = 4711
        moveToGroupActions = {}
        if item.is_group:
            deleteGroupAction = menu.addAction(self.tr("Delete Group"))
        elif item != self.model().rootItem:
            pfitems = self.model().protocol_tree_items
            other_groups = [i for i in pfitems.keys() if item not in pfitems[i]]

            if len(selected_protos) > 0:
                close_action = menu.addAction(self.tr("Close"))
                close_action.setIcon(QIcon.fromTheme("window-close"))

            if len(other_groups) > 0:
                moveToGroupMenu = menu.addMenu("Move to Group")
                for i in other_groups:
                    group_name = self.model().rootItem.child(i).data()
                    moveToGroupActions[moveToGroupMenu.addAction(group_name)] = i

        if item != self.model().rootItem:
            menu.addSeparator()
            sortGroupElementsAction = menu.addAction("Sort Group Elements")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == newGroupAction:
            self.model().addGroup()
            self.model().update()
        elif action == deleteGroupAction:
            self.model().deleteGroup(item)
        elif action in moveToGroupActions.keys():
            i = moveToGroupActions[action]
            self.model().moveToGroup(selected_items, i)
        elif action == close_action:
            self.close_wanted.emit(selected_protos)
        elif action == sortGroupElementsAction:
            if item.is_group:
                sortgroup_id = self.model().rootItem.index_of(item)
            else:
                sortgroup_id = self.model().rootItem.index_of(item.parent())
            self.model().sort_group(sortgroup_id)

    def selectionChanged(self, QItemSelection, QItemSelection_1):
        self.selection_changed.emit()
        super().selectionChanged(QItemSelection, QItemSelection_1)

    def dropEvent(self, event: QDropEvent):
        if len(event.mimeData().urls()) > 0:
            group_id = self.model().get_groupid_for_index(self.indexAt(event.pos()))
            self.files_dropped_on_group.emit(event.mimeData().urls(), group_id)
        else:
            super().dropEvent(event)