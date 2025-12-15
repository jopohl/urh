class Interval(object):
    __slots__ = ["data"]

    def __init__(self, start: int, end: int):
        self.data = (start, end)

    @property
    def start(self):
        return self.data[0]

    @property
    def end(self):
        return self.data[1]

    def __hash__(self):
        return hash(self.data)

    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        if isinstance(other, Interval):
            return self.data == other.data
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, Interval):
            return self.data < other.data
        else:
            return self.data < other

    def range(self):
        return range(self.start, self.end)

    def __repr__(self):
        return "{}-{}".format(self.start, self.end)

    def overlaps_with(self, other_interval) -> bool:
        return any(r in self.range() for r in other_interval.range())

    def find_common_interval(self, other_interval):
        sorted_intervals = sorted([self, other_interval])
        common_values = set(sorted_intervals[0].range()).intersection(
            sorted_intervals[1].range()
        )
        return (
            Interval(min(common_values), max(common_values) + 1)
            if common_values
            else None
        )

    @staticmethod
    def find_greatest(intervals: list):
        return max(intervals, key=len)
