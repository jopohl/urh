class SimulatorItem(object):
    def __init__(self):
        self.__parentItem = None
        self.__childItems = []

    def get_pos(self):
        if self.__parentItem is not None:
            return self.__parentItem.__childItems.index(self)

        return 0

    def insert_child(self, pos, child):
        self.__childItems.insert(pos, child)
        child.set_parent(self)

    def delete(self):
        for child in self.children[:]:
            child.set_parent(None)

        self.set_parent(None)

    def parent(self):
        return self.__parentItem

    def set_parent(self, value):
        if self.parent() is not None:
            self.parent().__childItems.remove(self)

        self.__parentItem = value

    @property
    def children(self):
        return self.__childItems

    def child_count(self) -> int:
        return len(self.__childItems)

    def next_sibling(self):
        result = None
        index = self.get_pos()

        if self.parent() and index < self.parent().child_count() - 1:
            result = self.parent().children[index + 1]

        return result

    def prev_sibling(self):
        result = None
        index = self.get_pos()

        if self.parent() and index > 0:
            result = self.parent().children[index - 1]

        return result

    def next(self):
        if self.child_count():
            return self.children[0]

        curr = self

        while curr is not None:
            if curr.next_sibling() is not None:
                return curr.next_sibling()

            curr = curr.parent()

        return None

    def prev(self):
        if self.prev_sibling() is not None:
            curr = self.prev_sibling()
        else:
            return self.parent()

        while curr.child_count():
            curr = curr.children[-1]

        return curr