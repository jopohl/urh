from urh.signalprocessing.Message import Message
from urh.signalprocessing.Participant import Participant


class Transcript(object):
    FORMAT = "{0} ({1}->{2}): {3}"

    def __init__(self):
        self.__data = []

    def append(
        self, source: Participant, destination: Participant, msg: Message, index: int
    ):
        if len(self.__data) == 0:
            self.__data.append([])

        self.__data[-1].append((source, destination, msg, index))

    def start_new_round(self):
        if len(self.__data) == 0 or len(self.__data[-1]) > 0:
            self.__data.append([])

    def clear(self):
        self.__data.clear()

    def get_for_all_participants(self, all_rounds: bool, use_bit=True) -> list:
        result = []
        if len(self.__data) == 0:
            return result

        rng = (
            range(0, len(self.__data))
            if all_rounds
            else range(len(self.__data) - 1, len(self.__data))
        )

        for i in rng:
            for source, destination, msg, msg_index in self.__data[i]:
                data = msg.plain_bits_str if use_bit else msg.plain_hex_str
                result.append(
                    self.FORMAT.format(
                        msg_index, source.shortname, destination.shortname, data
                    )
                )

            if i != len(self.__data) - 1:
                result.append("")

        return result

    def get_for_participant(self, participant: Participant) -> str:
        if len(self.__data) == 0:
            return ""

        result = []
        for source, destination, msg, _ in self.__data[-1]:
            if participant == destination:
                result.append("->" + msg.plain_bits_str)
            elif participant == source:
                result.append("<-" + msg.plain_bits_str)

        return "\n".join(result)
