class SimulatorItem(object):
    simulator_config = None
    expression_parser = None

    def __init__(self):
        self.__parentItem = None
        self.__childItems = []
        self.logging_active = True
        self.is_valid = True

    def validate(self):
        return True

    def get_pos(self):
        if self.parent() is not None:
            return self.parent().children.index(self)

        return 0

    def index(self):
        if self.parent() is None:
            return ""

        item = self
        result = str(item.get_pos() + 1)

        while item.parent().parent() is not None:
            item = item.parent()
            result = str(item.get_pos() + 1) + "." + result

        return result

    def insert_child(self, pos, child):
        child.set_parent(self)
        self.children.insert(pos, child)

    def add_child(self, child):
        child.set_parent(self)
        self.children.append(child)

    def delete(self):
        for child in self.children[:]:
            child.set_parent(None)

        self.set_parent(None)

    def parent(self):
        return self.__parentItem

    def set_parent(self, value):
        if self.parent() is not None:
            self.parent().children.remove(self)

        self.__parentItem = value

    @property
    def children(self):
        return self.__childItems

    def child_count(self) -> int:
        return len(self.children)

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
