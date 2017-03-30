from PyQt5.QtCore import QItemSelection, pyqtSlot
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

        self.move_to_group_actions = {}
        self.context_menu_pos = None

    def model(self) -> ProtocolTreeModel:
        return super().model()

    def selectionModel(self) -> QItemSelectionModel:
        return super().selectionModel()

    def create_context_menu(self):
        menu = QMenu()
        new_group_action = menu.addAction(self.tr("Create a new group"))
        new_group_action.setIcon(QIcon.fromTheme("list-add"))
        new_group_action.triggered.connect(self.on_new_group_action_triggered)

        item = self.model().getItem(self.indexAt(self.context_menu_pos))
        selected_items = [self.model().getItem(index) for index in self.selectionModel().selectedIndexes()]
        selected_protocols = [item.protocol for item in selected_items if not item.is_group]
        self.move_to_group_actions.clear()

        if item.is_group:
            delete_group_action = menu.addAction(self.tr("Delete group"))
            delete_group_action.setIcon(QIcon.fromTheme("list-remove"))
            delete_group_action.triggered.connect(self.on_delete_group_action_triggered)
        elif item != self.model().rootItem:
            tree_items = self.model().protocol_tree_items
            other_groups = [i for i in tree_items.keys() if item not in tree_items[i]]

            if len(selected_protocols) > 0:
                menu.addSeparator()
                close_action = menu.addAction(self.tr("Close"))
                close_action.setIcon(QIcon.fromTheme("window-close"))
                close_action.triggered.connect(self.on_close_action_triggered)

            if len(other_groups) > 0:
                move_to_group_menu = menu.addMenu("Move to Group")
                for i in other_groups:
                    group_name = self.model().rootItem.child(i).data()
                    move_to_group_action = move_to_group_menu.addAction(group_name)
                    move_to_group_action.triggered.connect(self.on_move_to_group_action_triggered)
                    self.move_to_group_actions[move_to_group_action] = i

        if item != self.model().rootItem:
            menu.addSeparator()
            sort_group_elements_action = menu.addAction("Sort Group Elements")
            sort_group_elements_action.setIcon(QIcon.fromTheme("view-sort-ascending"))
            sort_group_elements_action.triggered.connect(self.on_sort_group_elements_action_triggered)

        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.context_menu_pos = event.pos()
        menu = self.create_context_menu()
        menu.exec(self.mapToGlobal(event.pos()))
        self.context_menu_pos = None

    def selectionChanged(self, selection1: QItemSelection, selection2: QItemSelection):
        self.selection_changed.emit()
        super().selectionChanged(selection1, selection2)

    def dropEvent(self, event: QDropEvent):
        if len(event.mimeData().urls()) > 0:
            group_id = self.model().get_group_id_for_index(self.indexAt(event.pos()))
            self.files_dropped_on_group.emit(event.mimeData().urls(), group_id)
        else:
            super().dropEvent(event)

    @pyqtSlot()
    def on_new_group_action_triggered(self):
        self.model().addGroup()
        self.model().update()

    @pyqtSlot()
    def on_move_to_group_action_triggered(self):
        selected_items = [self.model().getItem(index) for index in self.selectionModel().selectedIndexes()]
        i = self.move_to_group_actions[self.sender()]
        self.model().move_to_group(selected_items, i)

    @pyqtSlot()
    def on_close_action_triggered(self):
        selected_items = [self.model().getItem(index) for index in self.selectionModel().selectedIndexes()]
        selected_protocols = [item.protocol for item in selected_items if not item.is_group]
        self.close_wanted.emit(selected_protocols)

    @pyqtSlot()
    def on_delete_group_action_triggered(self):
        item = self.model().getItem(self.indexAt(self.context_menu_pos))
        self.model().delete_group(item)

    @pyqtSlot()
    def on_sort_group_elements_action_triggered(self):
        item = self.model().getItem(self.indexAt(self.context_menu_pos))
        if item.is_group:
            sortgroup_id = self.model().rootItem.index_of(item)
        else:
            sortgroup_id = self.model().rootItem.index_of(item.parent())
        self.model().sort_group(sortgroup_id)
