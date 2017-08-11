from urh.ui.painting.Selection import Selection


class HorizontalSelection(Selection):
    def __init__(self, *args, fillcolor, opacity, parent=None):
        super().__init__(*args, fillcolor=fillcolor, opacity=opacity, parent=parent)

    @property
    def is_empty(self) -> bool:
        return self.height == 0

    @property
    def start(self):
        if self.height < 0:
            return self.y + self.height
        else:
            return self.y

    @start.setter
    def start(self, value):
        self.setY(value)

    @property
    def end(self):
        if self.height < 0:
            return self.y
        else:
            return self.y + self.height

    @end.setter
    def end(self, value):
        self.height = value - self.start

    def clear(self):
        self.height = 0
        super().clear()
