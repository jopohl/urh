class CommonRange(object):

    __slots__ = ["start", "end", "__bits", "__hex", "messages"]

    def __init__(self, start: int, end: int, bits: str):
        """

        :param start: Start of the common range
        :param end: End of the common range
        :param bits: Value of the common range
        """
        self.start = start
        self.end = end
        self.__bits = bits
        self.__hex = ("{0:0"+str(len(self.__bits)//4)+"x}").format(int(self.__bits, 2))
        self.messages = set()
        """:type: set of int """

    @property
    def bits(self) -> str:
        return self.__bits

    @property
    def hex_value(self) -> str:
        return self.__hex

    @property
    def byte_len(self) -> int:
        return (self.end - self.start) // 8

    def __len__(self):
        return self.end - self.start

    def __hash__(self):
        return hash(self.start) + hash(self.end) + hash(self.bits)

    def pos_of_hex(self, hex_str) -> tuple:
        try:
            start = 4 * self.hex_value.index(hex_str)
            return start, start + 4 * len(hex_str)
        except ValueError:
            return None

    @staticmethod
    def from_hex(hex_str):
        return CommonRange(start=0, end=0, bits="{0:b}".format(int(hex_str, 16)))

    def __eq__(self, other):
        if isinstance(other, CommonRange):
            return self.start == other.start and self.end == other.end and self.bits == other.bits
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, CommonRange):
            if self.start != other.start:
                return self.start < other.start
            else:
                return self.end <= other.end
        else:
            return -1

    def __repr__(self):
        return "{}-{} {} ({})".format(self.start,  self.end, self.hex_value, self.messages)
        
