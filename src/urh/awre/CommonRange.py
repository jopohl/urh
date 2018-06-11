import itertools
from urh.util import util
import numpy as np


class CommonRange(object):
    def __init__(self, start, length, value: np.ndarray = None, score=0, field_type="Generic", message_indices=None,
                 range_type="bit"):
        """

        :param start:
        :param length:
        :param value: Value for this common range as string
        """
        self.start = start
        self.length = length

        self.sync_end = 0

        if isinstance(value, str):
            value = np.array(list(map(lambda x: int(x, 16), value)), dtype=np.uint8)

        self.values = [value] if value is not None else []
        self.score = score
        self.field_type = field_type  # can also be length, address etc.

        self.range_type = range_type.lower()  # one of bit/hex/byte

        self.message_indices = set() if message_indices is None else set(message_indices)
        """
        Set of message indices, this range applies to
        """

    @property
    def end(self):
        return self.start + self.length - 1

    @property
    def bit_start(self):
        return self.__convert_number(self.start) + self.sync_end

    @property
    def bit_end(self):
        return self.__convert_number(self.start) + self.__convert_number(self.length) - 1 + self.sync_end

    @property
    def value(self):
        if len(self.values) == 0:
            return None
        elif len(self.values) == 1:
            return self.values[0]
        else:
            raise ValueError("This range has multiple values!")

    @property
    def value_str(self):
        return util.convert_numbers_to_hex_string(self.value)

    def matches(self, start: int, value: np.ndarray):
        return self.start == start and \
               self.length == len(value) and \
               self.value_str == util.convert_numbers_to_hex_string(value)

    def __convert_number(self, n):
        if self.range_type == "bit":
            return n
        elif self.range_type == "hex":
            return n * 4
        elif self.range_type == "byte":
            return n * 8
        else:
            raise ValueError("Unknown range type {}".format(self.range_type))

    def __repr__(self):
        result = "{} {}-{} ({} {})".format(self.field_type, self.bit_start,
                                           self.bit_end, self.length, self.range_type)

        result += " Values: " + " ".join(map(util.convert_numbers_to_hex_string, self.values))
        if self.score is not None:
            result += " Score: " + str(self.score)
        result += " Message indices: {" + ",".join(map(str, sorted(self.message_indices))) + "}"
        return result

    def __eq__(self, other):
        if not isinstance(other, CommonRange):
            return False

        return self.bit_start == other.bit_start and \
               self.bit_end == other.bit_end and \
               self.field_type == other.field_type

    def __hash__(self):
        return hash((self.start, self.length, self.field_type))

    def __lt__(self, other):
        return self.bit_start < other.bit_start

    def overlaps_with(self, other) -> bool:
        if not isinstance(other, CommonRange):
            raise ValueError("Need another bit range to compare")
        return any(i in range(self.bit_start, self.bit_end)
                   for i in range(other.bit_start, other.bit_end))


class EmptyCommonRange(CommonRange):
    """
    Empty Common Bit Range, to indicate, that no common Bit Range was found
    """

    def __init__(self, field_type="Generic"):
        super().__init__(0, 0, "")
        self.field_type = field_type

    def __eq__(self, other):
        return isinstance(other, EmptyCommonRange) \
               and other.field_type == self.field_type

    def __repr__(self):
        return "No " + self.field_type

    def __hash__(self):
        return hash(super)


class CommonRangeContainer(object):
    """
    This is the raw equivalent of a Message Type:
    A container of common ranges
    """

    def __init__(self, ranges: list, message_indices=set()):
        assert isinstance(ranges, list)

        self.__ranges = ranges  # type: list[CommonRange]
        self.__ranges.sort()

        self.message_indices = message_indices

    @property
    def ranges_overlap(self) -> bool:
        return self.has_overlapping_ranges(self.__ranges)

    def add_range(self, rng: CommonRange):
        self.__ranges.append(rng)
        self.__ranges.sort()

    def add_ranges(self, ranges: list):
        self.__ranges.extend(ranges)
        self.__ranges.sort()

    def has_same_ranges(self, ranges: list) -> bool:
        return self.__ranges == ranges

    @staticmethod
    def has_overlapping_ranges(ranges: list) -> bool:
        for rng1, rng2 in itertools.combinations(ranges, 2):
            if rng1.overlaps_with(rng2):
                return True
        return False

    def __len__(self):
        return len(self.__ranges)

    def __iter__(self):
        return self.__ranges.__iter__()

    def __repr__(self):
        from pprint import pformat
        return pformat(self.__ranges)

    def __eq__(self, other):
        if not isinstance(other, CommonRangeContainer):
            return False
        return self.__ranges == other.__ranges and self.message_indices == other.message_indices
