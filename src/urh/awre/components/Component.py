from abc import ABCMeta

from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from enum import Enum

from urh.util.Logger import logger


class Component(metaclass=ABCMeta):
    """
    A component is the basic building block of our AWRE algorithm.
    A component can be a Preamble or Sync or Length Field finding routine.
    Components can have a priority which determines the order in which they are processed by the algorithm.
    Additionally, components can have a set of predecessors to define hard dependencies.
    """


    EQUAL_BIT_TRESHOLD = 0.9

    class Backend(Enum):
        python = 1
        cython = 2
        plainc = 3

    def __init__(self, priority=0, predecessors=None, enabled=True, backend=None, messagetypes=None):
        """

        :param priority: Priority for this Component. 0 is highest priority
        :type priority: int
        :param predecessors: List of preceding components, that need to be run before this one
        :type predecessors: list of Component or None
        :param messagetypes: Message types of the examined protocol
        :type messagetypes: list[MessageType]
        """
        self.enabled = enabled
        self.backend = backend if backend is not None else self.Backend.python
        self.priority = abs(priority)
        self.predecessors = predecessors if isinstance(predecessors, list) else []
        """:type: list of Component """

        self.messagetypes = messagetypes

    def find_field(self, messages):
        """
        Wrapper method selecting the backend to assign the protocol field.
        Various strategies are possible e.g.:
        1) Heuristics e.g. for Preamble
        2) Scoring based e.g. for Length
        3) Fulltext search for addresses based on participant subgroups

        :param messages: messages a field shall be searched for
        :type messages: list of Message
        """
        try:
            if self.backend == self.Backend.python:
                self._py_find_field(messages)
            elif self.backend == self.Backend.cython:
                self._cy_find_field(messages)
            elif self.backend == self.Backend.plainc:
                self._c_find_field(messages)
            else:
                raise ValueError("Unsupported backend {}".format(self.backend))
        except NotImplementedError:
            logger.info("Skipped {} because not implemented yet".format(self.__class__.__name__))

    def _py_find_field(self, messages):
        raise NotImplementedError()

    def _cy_find_field(self, messages):
        raise NotImplementedError()

    def _c_find_field(self, messages):
        raise NotImplementedError()


    def assign_messagetypes(self, messages, clusters):
        """
        Assign message types based on the clusters. Following rules:
        1) Messages from different clusters will get different message types
        2) Messages from same clusters will get same message type
        3) The new message type will copy over the existing labels
        4) No new message type will be set for messages, that already have a custom message type assigned

        For messages with clustername "default" no new message type will be created

        :param messages: Messages, that messagetype needs to be clustered
        :param clusters: clusters for the messages
        :type messages: list[Message]
        :type clusters: dict[str, set[int]]
        :return:
        """
        for clustername, clustercontent in clusters.items():
            if clustername == "default":
                # Do not force the default message type
                continue

            for msg_i in clustercontent:
                msg = messages[msg_i]
                if msg.message_type == self.messagetypes[0]:
                    # Message has default message type
                    # Copy the existing labels and create a new message type
                    # if it was not already done
                    try:
                        msg_type = next(mtype for mtype in self.messagetypes if mtype.name == clustername)
                    except StopIteration:
                        msg_type = MessageType(name=clustername, iterable=msg.message_type)
                        msg_type.assigned_by_logic_analyzer = True
                        self.messagetypes.append(msg_type)
                    msg.message_type = msg_type

