import array
import random
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class AWRExperiments(AWRETestCase):
    @staticmethod
    def _prepare_protocol_1() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="dead")
        bob = Participant("Bob", address_hex="beef")

        mb = MessageTypeBuilder("protocol_with_one_message_type")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x1337"},
                               participants=[alice, bob])

        return pg

    @staticmethod
    def _prepare_protocol_2() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="dead01")
        bob = Participant("Bob", address_hex="beef24")

        mb = MessageTypeBuilder("protocol_with_one_message_type")
        mb.add_label(FieldType.Function.PREAMBLE, 72)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 24)
        mb.add_label(FieldType.Function.DST_ADDRESS, 24)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x1337"},
                               preambles_by_mt={mb.message_type: "10" * 36},
                               participants=[alice, bob])

        return pg

    @staticmethod
    def _prepare_protocol_3() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="1337")
        bob = Participant("Bob", address_hex="4711")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 16)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 16)
        mb_ack.add_label(FieldType.Function.SYNC, 16)
        mb_ack.add_label(FieldType.Function.LENGTH, 8)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 16)

        pg = ProtocolGenerator([mb.message_type, mb_ack.message_type],
                               syncs_by_mt={mb.message_type: "0x9a7d", mb_ack.message_type: "0x9a7d"},
                               preambles_by_mt={mb.message_type: "10" * 8, mb_ack.message_type: "10" * 8},
                               participants=[alice, bob])

        return pg

    def get_protocol(self, protocol_number: int, num_messages, num_broken_messages=0):
        if protocol_number == 1:
            pg = self._prepare_protocol_1()
        elif protocol_number == 2:
            pg = self._prepare_protocol_2()
        elif protocol_number == 3:
            pg = self._prepare_protocol_3()
        else:
            raise ValueError("Unknown protocol number")

        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = pg.participants[0], pg.participants[1]
                data_bytes = 4
            else:
                source, destination = pg.participants[1], pg.participants[0]
                data_bytes = 16

            pg.generate_message(data="1" * (data_bytes * 8), source=source, destination=destination)

            if "ack" in (msg_type.name for msg_type in pg.protocol.message_types):
                pg.generate_message(message_type=1, data="", source=destination, destination=source)

        for i in range(num_broken_messages):
                msg = pg.protocol.messages[i]
                pos = random.randint(0, len(msg.plain_bits) // 2)
                msg.plain_bits[pos:] = array.array("B",
                                                   [random.randint(0, 1) for _ in range(len(msg.plain_bits) - pos)])

        self.save_protocol("protocol-{}_{}_messages".format(protocol_number, num_messages), pg)

        expected_message_types = [msg.message_type for msg in pg.protocol.messages]

        # Delete message type information -> no prior knowledge
        self.clear_message_types(pg.protocol.messages)

        return pg.protocol, expected_message_types

    @staticmethod
    def calculate_accuracy(messages, expected_labels):
        """
        Calculate the accuracy of labels compared to expected labels
        Accuracy is 100% when labels == expected labels
        Accuracy drops by 1 / len(expected_labels) for every expected label not present in labels

        :type messages: list of Message
        :type expected_labels: list of MessageType
        :return:
        """
        accuracy = 0
        for i, msg in enumerate(messages):
            expected = expected_labels[i]  # type: MessageType
            msg_accuracy = 1
            for lbl in expected:
                try:
                    next(l for l in msg.message_type if
                         l.start == lbl.start and l.end == lbl.end and l.field_type.function == lbl.field_type.function)
                    found = True
                except StopIteration:
                    found = False

                if not found:
                    msg_accuracy -= 1 / len(expected)

            accuracy += msg_accuracy * (1 / len(messages))

        return accuracy * 100

    def test_against_num_messages(self):
        num_messages = list(range(1, 24))
        accuracies = defaultdict(list)

        protocols = [1, 2, 3]

        random.seed(0)
        np.random.seed(0)
        for protocol_nr in protocols:
            for n in num_messages:
                protocol, expected_labels = self.get_protocol(protocol_nr, num_messages=n)
                self.__run_format_finder_for_protocol(protocol)

                accuracy = self.calculate_accuracy(protocol.messages, expected_labels)
                accuracies["protocol {}".format(protocol_nr)].append(accuracy)

        self.__plot(num_messages, accuracies, xlabel="Number of messages", ylabel="Accuracy in %")
        self.__export_to_csv("/tmp/accuray-vs-messages", num_messages, accuracies)

    def test_against_error(self):
        num_runs = 100

        num_messages = 16
        num_broken_messages = list(range(0, num_messages))
        accuracies = defaultdict(list)

        protocols = [1, 2, 3]

        random.seed(0)
        np.random.seed(0)

        for protocol_nr in protocols:
            for broken in num_broken_messages:
                tmp_accuracies = np.empty(num_runs, dtype=np.float64)
                for i in range(num_runs):
                    protocol, expected_labels = self.get_protocol(protocol_nr,
                                                                  num_messages=num_messages,
                                                                  num_broken_messages=broken)

                    self.__run_format_finder_for_protocol(protocol)
                    accuracy = self.calculate_accuracy(protocol.messages, expected_labels)
                    tmp_accuracies[i] = accuracy

                accuracies["protocol {}".format(protocol_nr)].append(np.mean(tmp_accuracies))

        self.__plot(num_broken_messages, accuracies, xlabel="Number of broken messages", ylabel="Accuracy in %")
        self.__export_to_csv("/tmp/accuray-vs-error", num_broken_messages, accuracies)

    @staticmethod
    def __export_to_csv(filename: str, x: list, y: dict):
        if not filename.endswith(".csv"):
            filename += ".csv"

        with open(filename, "w") as f:
            f.write("N,")
            for y_cap in sorted(y):
                f.write(y_cap + ",")
            f.write("\n")

            for i, x_val in enumerate(x):
                f.write("{},".format(x_val))
                for y_cap in sorted(y):
                    f.write("{},".format(y[y_cap][i]))
                f.write("\n")

    @staticmethod
    def __plot(x: list, y: dict, xlabel: str, ylabel: str):
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        for y_cap, y_values in sorted(y.items()):
            plt.plot(x, y_values, label=y_cap)

        plt.legend()
        plt.show()

    @staticmethod
    def __run_format_finder_for_protocol(protocol: ProtocolAnalyzer):
        ff = FormatFinder(protocol.messages)
        ff.known_participant_addresses.clear()
        ff.run()

        for msg_type, indices in ff.existing_message_types.items():
            for i in indices:
                protocol.messages[i].message_type = msg_type
