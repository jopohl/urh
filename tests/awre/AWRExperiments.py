import array
import random
import time
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.Preprocessor import Preprocessor
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.awre.engines.Engine import Engine
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.util.GenericCRC import GenericCRC


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

    @staticmethod
    def _prepare_protocol_4() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="1337")
        bob = Participant("Bob", address_hex="4711")

        checksum = GenericCRC.from_standard_checksum("CRC16 CC1101")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 16)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.DATA, 8 * 8)
        mb.add_checksum_label(16, checksum)

        mb2 = MessageTypeBuilder("data2")
        mb2.add_label(FieldType.Function.PREAMBLE, 16)
        mb2.add_label(FieldType.Function.SYNC, 16)
        mb2.add_label(FieldType.Function.LENGTH, 8)
        mb2.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb2.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb2.add_label(FieldType.Function.DATA, 64 * 8)
        mb2.add_checksum_label(16, checksum)

        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 16)
        mb_ack.add_label(FieldType.Function.SYNC, 16)
        mb_ack.add_label(FieldType.Function.LENGTH, 8)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb_ack.add_checksum_label(16, checksum)

        mt1, mt2, mt3 = mb.message_type, mb2.message_type, mb_ack.message_type

        pg = ProtocolGenerator([mt1, mt2, mt3],
                               syncs_by_mt={mt1: "0x9a7d", mt2: "0x9a7d", mt3: "0x9a7d"},
                               preambles_by_mt={mt1: "10" * 8, mt2: "10" * 8, mt3: "10" * 8},
                               participants=[alice, bob])

        return pg

    @staticmethod
    def _prepare_protocol_5() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="1337")
        bob = Participant("Bob", address_hex="4711")
        carl = Participant("Carl", address_hex="cafe")

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
                               participants=[alice, bob, carl])

        return pg

    @staticmethod
    def _prepare_protocol_6() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="24")
        broadcast = Participant("Broadcast", address_hex="ff")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 8)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x8e88"},
                               preambles_by_mt={mb.message_type: "10" * 8},
                               participants=[alice, broadcast])

        return pg

    @staticmethod
    def _prepare_protocol_7() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="313370")
        bob = Participant("Bob", address_hex="031337")
        charly = Participant("Charly", address_hex="110000")
        daniel = Participant("Daniel", address_hex="001100")
        emy = Participant("Emy", address_hex="100100")
        # broadcast = Participant("Broadcast", address_hex="ff")     #TODO: Sometimes messages to broadcast

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 16)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.DST_ADDRESS, 24)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 24)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 32)
        mb.add_label(FieldType.Function.DATA, 8 * 8)
        mb.add_label(FieldType.Function.CHECKSUM, 16)

        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 8)
        mb_ack.add_label(FieldType.Function.SYNC, 16)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 24)

        mb_kex = MessageTypeBuilder("kex")
        mb_kex.add_label(FieldType.Function.PREAMBLE, 24)
        mb_kex.add_label(FieldType.Function.SYNC, 16)
        mb_kex.add_label(FieldType.Function.DST_ADDRESS, 24)
        mb_kex.add_label(FieldType.Function.SRC_ADDRESS, 24)
        mb_kex.add_label(FieldType.Function.DATA, 64 * 8)
        mb.add_label(FieldType.Function.CHECKSUM, 16)

        pg = ProtocolGenerator([mb.message_type, mb_ack.message_type, mb_kex.message_type],
                               syncs_by_mt={mb.message_type: "0x0420", mb_ack.message_type: "0x2222",
                                            mb_kex.message_type: "0x6767"},
                               preambles_by_mt={mb.message_type: "10" * 8, mb_ack.message_type: "10" * 4,
                                                mb_kex.message_type: "10" * 12},
                               participants=[alice, bob, charly, daniel, emy])

        return pg

    @classmethod
    def get_protocol(cls, protocol_number: int, num_messages, num_broken_messages=0, silent=False):
        if protocol_number == 1:
            pg = cls._prepare_protocol_1()
        elif protocol_number == 2:
            pg = cls._prepare_protocol_2()
        elif protocol_number == 3:
            pg = cls._prepare_protocol_3()
        elif protocol_number == 4:
            pg = cls._prepare_protocol_4()
        elif protocol_number == 5:
            pg = cls._prepare_protocol_5()
        elif protocol_number == 6:
            pg = cls._prepare_protocol_6()
        elif protocol_number == 7:
            pg = cls._prepare_protocol_7()
        else:
            raise ValueError("Unknown protocol number")

        messages_types_with_data_field = [mt for mt in pg.protocol.message_types
                                          if mt.get_first_label_with_type(FieldType.Function.DATA)]
        i = -1
        while len(pg.protocol.messages) < num_messages:
            i += 1
            source = pg.participants[i % len(pg.participants)]
            destination = pg.participants[(i + 1) % len(pg.participants)]
            if i % 2 == 0:
                data_bytes = 8
            else:
                # data_bytes = 16
                data_bytes = 64
            data = "".join(random.choice(["0", "1"]) for _ in range(data_bytes * 8))
            if len(messages_types_with_data_field) == 0:
                # set data automatically
                pg.generate_message(data=data, source=source, destination=destination)
            else:
                # search for message type with right data length
                mt = next(mt for mt in messages_types_with_data_field
                          if mt.get_first_label_with_type(FieldType.Function.DATA).length == data_bytes * 8)
                pg.generate_message(message_type=mt, data=data, source=source, destination=destination)

            ack_message_type = next((mt for mt in pg.protocol.message_types if "ack" in mt.name), None)
            if ack_message_type:
                pg.generate_message(message_type=ack_message_type, data="", source=destination, destination=source)

        for i in range(num_broken_messages):
            msg = pg.protocol.messages[i]
            pos = random.randint(0, len(msg.plain_bits) // 2)
            msg.plain_bits[pos:] = array.array("B",
                                               [random.randint(0, 1) for _ in range(len(msg.plain_bits) - pos)])

        cls.save_protocol("protocol{}_{}_messages".format(protocol_number, num_messages), pg, silent=silent)

        expected_message_types = [msg.message_type for msg in pg.protocol.messages]

        # Delete message type information -> no prior knowledge
        cls.clear_message_types(pg.protocol.messages)

        # Delete data labels if present
        for mt in expected_message_types:
            data_lbl = mt.get_first_label_with_type(FieldType.Function.DATA)
            if data_lbl:
                mt.remove(data_lbl)

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

        def label_functions_matches(lbl1: ProtocolLabel, lbl2: ProtocolLabel) -> bool:
            return lbl1.field_type.function == lbl2.field_type.function

        for i, msg in enumerate(messages):
            expected = expected_labels[i]  # type: MessageType

            msg_accuracy = 1
            for lbl in expected:
                try:
                    next(l for l in msg.message_type if
                         l.start == lbl.start and l.end == lbl.end and label_functions_matches(l, lbl))
                    found = True
                except StopIteration:
                    found = False

                if not found:
                    msg_accuracy -= 1 / len(expected)

            accuracy += msg_accuracy * (1 / len(messages))

        return accuracy * 100

    def test_against_num_messages(self):
        num_messages = list(range(1, 24, 1))
        accuracies = defaultdict(list)

        protocols = [1, 2, 3, 4, 5, 6, 7]

        random.seed(0)
        np.random.seed(0)
        for protocol_nr in protocols:
            for n in num_messages:
                protocol, expected_labels = self.get_protocol(protocol_nr, num_messages=n)
                self.run_format_finder_for_protocol(protocol)

                accuracy = self.calculate_accuracy(protocol.messages, expected_labels)
                accuracies["protocol {}".format(protocol_nr)].append(accuracy)

        self.__plot(num_messages, accuracies, xlabel="Number of messages", ylabel="Accuracy in %", grid=True)
        self.__export_to_csv("/tmp/accuray-vs-messages", num_messages, accuracies)

    def test_against_error(self):
        Engine._DEBUG_ = False
        Preprocessor._DEBUG_ = False

        num_runs = 100

        num_messages = 16
        num_broken_messages = list(range(0, num_messages))
        accuracies = defaultdict(list)

        protocols = [1, 2, 3]

        random.seed(0)
        np.random.seed(0)

        for protocol_nr in protocols:
            for broken in num_broken_messages:
                print("Test Protocol {0} with {1:02d} broken messages ({2} runs)".format(protocol_nr, broken, num_runs))
                tmp_accuracies = np.empty(num_runs, dtype=np.float64)
                for i in range(num_runs):
                    protocol, expected_labels = self.get_protocol(protocol_nr,
                                                                  num_messages=num_messages,
                                                                  num_broken_messages=broken,
                                                                  silent=True)

                    self.run_format_finder_for_protocol(protocol)
                    accuracy = self.calculate_accuracy(protocol.messages, expected_labels)
                    tmp_accuracies[i] = accuracy

                accuracies["protocol {}".format(protocol_nr)].append(np.mean(tmp_accuracies))

        self.__plot(num_broken_messages, accuracies, xlabel="Number of broken messages", ylabel="Accuracy in %")
        self.__export_to_csv("/tmp/accuray-vs-error", num_broken_messages, accuracies)

    def test_performance(self):
        num_messages = list(range(5, 50, 5))
        protocols = [1, 2, 3]

        random.seed(0)
        np.random.seed(0)

        performances = defaultdict(list)

        for protocol_nr in protocols:
            for messages in num_messages:
                protocol, _ = self.get_protocol(protocol_nr, messages)

                t = time.time()
                self.run_format_finder_for_protocol(protocol)
                performances["protocol {}".format(protocol_nr)].append(time.time() - t)

        self.__plot(num_messages, performances, xlabel="Number of messages", ylabel="Time in milliseconds", grid=True)

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
    def __plot(x: list, y: dict, xlabel: str, ylabel: str, grid=False):
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        for y_cap, y_values in sorted(y.items()):
            plt.plot(x, y_values, label=y_cap)

        if grid:
            plt.grid()

        plt.legend()
        plt.show()

    @staticmethod
    def run_format_finder_for_protocol(protocol: ProtocolAnalyzer):
        ff = FormatFinder(protocol.messages)
        ff.known_participant_addresses.clear()
        ff.run()

        for msg_type, indices in ff.existing_message_types.items():
            for i in indices:
                protocol.messages[i].message_type = msg_type
