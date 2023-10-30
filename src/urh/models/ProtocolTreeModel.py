from PyQt5.QtCore import QAbstractItemModel, pyqtSignal, QModelIndex, Qt, QMimeData
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMessageBox, QWidget

from urh.models.ProtocolTreeItem import ProtocolTreeItem
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.util.Logger import logger


class ProtocolTreeModel(QAbstractItemModel):
    item_dropped = pyqtSignal()
    group_deleted = pyqtSignal(int, int)
    proto_to_group_added = pyqtSignal(int)
    group_added = pyqtSignal(QModelIndex)

    def __init__(self, controller, parent=None):
        self.rootItem = ProtocolTreeItem(None, None)
        self.rootItem.addGroup()
        self.controller = controller

        super().__init__(parent)

    @property
    def protocols(self):
        """
        :rtype: dict[int, list of ProtocolAnalyzer]
        """
        result = {}
        for i, group in enumerate(self.rootItem.children):
            result[i] = [child.protocol for child in group.children]

        return result

    @property
    def ngroups(self):
        return self.rootItem.childCount()

    @property
    def groups(self):
        """

        :rtype: list of ProtocolGroup
        """
        return [self.group_at(i) for i in range(self.ngroups)]

    @property
    def protocol_tree_items(self):
        """
        :rtype: dict[int, list of ProtocolTreeItem]
        """
        result = {}
        for i, group in enumerate(self.rootItem.children):
            result[i] = [child for child in group.children]

        return result

    def group_at(self, index: int) -> ProtocolGroup:
        return self.rootItem.child(index).group

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def get_group_id_for_index(self, index: QModelIndex) -> int:
        item = self.getItem(index)
        if item.parent() == self.rootItem:
            return self.rootItem.index_of(item)
        elif item == self.rootItem:
            return self.ngroups - 1  # Last group when dropped on root
        else:
            return self.rootItem.index_of(item.parent())  # Item is Protocol

    def getItem(self, index: QModelIndex) -> ProtocolTreeItem:
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def rowCount(self, parent: QModelIndex = None, *args, **kwargs):
        parent_item = self.getItem(parent)
        return parent_item.childCount()

    def columnCount(self, parent: QModelIndex = None, *args, **kwargs):
        return 1

    def index(self, row: int, column: int, parent=None, *args, **kwargs):
        if parent is None:
            return QModelIndex()

        parent_item = self.getItem(parent)
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex = None):
        if not index.isValid():
            return QModelIndex()

        child_item = self.getItem(index)
        try:
            parent_item = child_item.parent()
        except AttributeError:
            return QModelIndex()

        if parent_item == self.rootItem or parent_item is None:
            return QModelIndex()

        return self.createIndex(parent_item.indexInParent(), 0, parent_item)

    def data(self, index: QModelIndex, role=None):
        item = self.getItem(index)
        if role == Qt.DisplayRole:
            return item.data()
        elif role == Qt.DecorationRole and item.is_group:
            return QIcon.fromTheme("folder")
        elif role == Qt.CheckStateRole:
            return item.show
        elif role == Qt.FontRole:
            if (
                item.is_group
                and self.rootItem.index_of(item) in self.controller.active_group_ids
            ):
                font = QFont()
                font.setBold(True)
                return font
            elif item.protocol in self.controller.selected_protocols:
                font = QFont()
                font.setBold(True)
                return font
        elif role == Qt.ToolTipRole:
            return item.data()

    def setData(self, index: QModelIndex, value, role=None):
        item = self.getItem(index)

        if role == Qt.EditRole and len(value) > 0:
            item.setData(value)
            return True
        elif role == Qt.CheckStateRole:
            item.show = value
            return True

        return False

    def add_protocol(self, protocol: ProtocolAnalyzer, group_id=0):
        if group_id >= self.ngroups:
            group_id = 0
        self.beginResetModel()
        self.rootItem.child(group_id).addProtocol(protocol)
        self.endResetModel()
        self.proto_to_group_added.emit(group_id)
        return self.groups[group_id]

    def remove_protocol(self, protocol: ProtocolAnalyzer):
        self.beginResetModel()
        result = False
        for group in self.rootItem.children:
            if group.removeProtocol(protocol):
                result = True
                break
        self.endResetModel()
        return result

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsDropEnabled
        return (
            Qt.ItemIsEditable
            | Qt.ItemIsEnabled
            | Qt.ItemIsSelectable
            | Qt.ItemIsUserCheckable
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsDropEnabled
        )

    def supportedDragActions(self):
        return Qt.MoveAction | Qt.CopyAction

    def mimeTypes(self):
        return ["text/plain", "text/uri-list"]

    def mimeData(self, indexes):
        data = ""
        for index in indexes:
            parent_item = self.getItem(index.parent())
            if parent_item == self.rootItem:
                data += "{0},{1},{2}/".format(index.row(), index.column(), -1)
            else:
                data += "{0},{1},{2}/".format(
                    index.row(), index.column(), self.rootItem.index_of(parent_item)
                )
        mime_data = QMimeData()
        mime_data.setText(data)
        return mime_data

    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        if action == Qt.IgnoreAction:
            return True

        data_str = str(mimedata.text())
        indexes = list(reversed(data_str.split("/")[:-1]))
        drag_nodes = []

        # Ensure we only drop groups or files
        contains_groups = False
        contains_files = False

        for index in indexes:
            row, column, parent = map(int, index.split(","))
            if parent == -1:
                parent = self.rootItem
            else:
                parent = self.rootItem.child(parent)
            node = parent.child(row)
            try:
                if node.is_group:
                    contains_groups = True
                else:
                    contains_files = True
            except AttributeError:
                logger.error("Could not perform drop for index {}".format(index))
                continue

            if contains_files and contains_groups:
                QMessageBox.information(
                    QWidget(),
                    self.tr("Drag not supported"),
                    self.tr(
                        "You can only drag/drop groups or protocols, no mixtures of both."
                    ),
                )
                return False

            drag_nodes.append(node)

        drop_node = self.getItem(parentIndex)

        if drop_node == self.rootItem:
            # Append to Last Group when dropped on root
            try:
                drop_node = self.rootItem.children[-1]
            except IndexError:
                return False

        if not drop_node.is_group:
            parent_node = drop_node.parent()
            dropped_on_group = False
        else:
            parent_node = drop_node
            dropped_on_group = True

        if parent_node is None:
            return False

        if dropped_on_group and contains_groups:
            parent_node = drop_node.parent()
            pos = parent_node.index_of(drop_node)
            parent_node.bringChildsToIndex(pos, drag_nodes)
        elif dropped_on_group:
            if parent_node.containsChilds(drag_nodes):
                # "Nodes on parent folder Dropped"
                parent_node.bringChildsToFront(drag_nodes)
            else:
                # "Nodes on distinct folder dropped"
                for dragNode in drag_nodes:
                    parent_node.appendChild(dragNode)

                self.proto_to_group_added.emit(self.rootItem.index_of(parent_node))
        else:
            # Dropped on file
            if contains_groups:
                # Can't drop groups on files
                return False

            elif (
                parent_node.containsChilds(drag_nodes)
                and drop_node in parent_node.children
            ):
                # "Nodes on node in parent folder dropped"
                pos = parent_node.index_of(drop_node)
                parent_node.bringChildsToIndex(pos, drag_nodes)
            elif parent_node.containsChilds(drag_nodes):
                parent_node.bringChildsToFront(drag_nodes)
            else:
                # "Nodes on node in distinct folder dropped"
                pos = parent_node.index_of(drop_node)
                for dragNode in drag_nodes:
                    dragNode.setParent(parent_node)
                    parent_node.insertChild(pos, dragNode)
                self.proto_to_group_added.emit(self.rootItem.index_of(parent_node))

        self.item_dropped.emit()
        return True

    def insertRow(self, row, parent=None, *args, **kwargs):
        return self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent=None, *args, **kwargs):
        self.beginInsertRows(parent, row, (row + (count - 1)))
        self.endInsertRows()
        return True

    def removeRow(self, row, parentIndex=None, *args, **kwargs):
        return self.removeRows(row, 1, parentIndex)

    def removeRows(self, row, count, parentIndex=None, *args, **kwargs):
        self.beginRemoveRows(parentIndex, row, row)
        node = self.getItem(parentIndex)
        node.removeAtIndex(row)
        self.endRemoveRows()

        return True

    def addGroup(self, name="New group"):
        self.rootItem.addGroup(name)
        child_nr = self.rootItem.childCount() - 1
        self.group_added.emit(
            self.createIndex(child_nr, 0, self.rootItem.child(child_nr))
        )

    def delete_group(self, group_item: ProtocolTreeItem):
        if self.rootItem.childCount() == 1:
            QMessageBox.critical(
                self.controller,
                self.tr("Group not deletable"),
                self.tr(
                    "You can't delete the last group. Think about the children, they would be homeless!"
                ),
            )
            return

        group_id = self.rootItem.index_of(group_item)
        if group_id == 0:
            new_group_index = 1
        else:
            new_group_index = group_id - 1

        new_group = self.rootItem.children[new_group_index]

        for i in reversed(range(group_item.childCount())):
            new_group.appendChild(group_item.children[i])

        self.removeRow(group_id, QModelIndex())
        self.group_deleted.emit(group_id, new_group_index)

    def move_to_group(self, items, new_group_id: int):
        """
        :type items: list of ProtocolTreeItem
        """
        group = self.rootItem.child(new_group_id)
        for item in items:
            group.appendChild(item)
        self.controller.refresh()

    def sort_group(self, sortgroup_id):
        self.blockSignals(True)
        self.rootItem.child(sortgroup_id).sortChilds()
        self.controller.refresh()
        self.blockSignals(False)

    def set_copy_mode(self, use_copy: bool):
        """
        Set all protocols in copy mode. They will return a copy of their protocol.
        This is used for writable mode in CFC.

        :param use_copy:
        :return:
        """
        for group in self.rootItem.children:
            for proto in group.children:
                proto.copy_data = use_copy
