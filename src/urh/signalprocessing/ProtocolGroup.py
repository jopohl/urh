from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Message import Message


class ProtocolGroup(object):
    __slots__ = ["name", "__items", "loaded_from_file"]

    def __init__(self, name: str):
        self.name = name
        self.__items = []
        self.loaded_from_file = False

    @property
    def items(self):
        """

        :rtype: list of ProtocolTreeItem
        """
        return self.__items

    @property
    def num_protocols(self):
        return len(self.items)

    @property
    def num_messages(self):
        return sum(p.num_messages for p in self.protocols)

    @property
    def all_protocols(self):
        """

        :rtype: list of ProtocolAnalyzer
        """
        return [self.protocol_at(i) for i in range(self.num_protocols)]

    @property
    def protocols(self):
        """

        :rtype: list of ProtocolAnalyzer
        """
        return [proto for proto in self.all_protocols if proto.show]

    @property
    def messages(self):
        """

        :rtype: list of Message
        """
        result = []
        for proto in self.protocols:
            result.extend(proto.messages)
        return result

    @property
    def plain_bits_str(self):
        """

        :rtype: list of str
        """
        result = []
        for proto in self.protocols:
            result.extend(proto.plain_bits_str)
        return result

    @property
    def decoded_bits_str(self):
        """

        :rtype: list of str
        """
        result = []
        for proto in self.protocols:
            result.extend(proto.decoded_proto_bits_str)
        return result

    def protocol_at(self, index: int) -> ProtocolAnalyzer:
        try:
            proto = self.items[index].protocol
            return proto
        except IndexError:
            return None

    def __repr__(self):
        return "Group: {0}".format(self.name)

    def add_protocol_item(self, protocol_item):
        """
        This is intended for adding a protocol item directly to the group

        :type protocol: ProtocolTreeItem
        :return:
        """
        self.__items.append(protocol_item) # Warning: parent is None!
