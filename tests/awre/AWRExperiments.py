import array
import multiprocessing
import os
import random
import time
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from tests.utils_testing import get_path_for_data_file
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.Preprocessor import Preprocessor
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.awre.engines.Engine import Engine
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.util.GenericCRC import GenericCRC


def run_for_num_broken(
    protocol_nr, num_broken: list, num_messages: int, num_runs: int
) -> list:
    random.seed(0)
    np.random.seed(0)

    result = []
    for broken in num_broken:
        tmp_accuracies = np.empty(num_runs, dtype=np.float64)
        tmp_accuracies_without_broken = np.empty(num_runs, dtype=np.float64)
        for i in range(num_runs):
            protocol, expected_labels = AWRExperiments.get_protocol(
                protocol_nr,
                num_messages=num_messages,
                num_broken_messages=broken,
                silent=True,
            )

            AWRExperiments.run_format_finder_for_protocol(protocol)
            accuracy = AWRExperiments.calculate_accuracy(
                protocol.messages, expected_labels
            )
            accuracy_without_broken = AWRExperiments.calculate_accuracy(
                protocol.messages, expected_labels, broken
            )
            tmp_accuracies[i] = accuracy
            tmp_accuracies_without_broken[i] = accuracy_without_broken

        avg_accuracy = np.mean(tmp_accuracies)
        avg_accuracy_without_broken = np.mean(tmp_accuracies_without_broken)

        result.append((avg_accuracy, avg_accuracy_without_broken))
        print(
            "Protocol {} with {} broken: {:>3}% {:>3}%".format(
                protocol_nr, broken, int(avg_accuracy), int(avg_accuracy_without_broken)
            )
        )

    return result


class AWRExperiments(AWRETestCase):
    @staticmethod
    def _prepare_protocol_1() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="dead")
        bob = Participant("Bob", address_hex="beef")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 8)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x1337"},
            participants=[alice, bob],
        )
        return pg

    @staticmethod
    def _prepare_protocol_2() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="dead01")
        bob = Participant("Bob", address_hex="beef24")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 72)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 24)
        mb.add_label(FieldType.Function.DST_ADDRESS, 24)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x1337"},
            preambles_by_mt={mb.message_type: "10" * 36},
            sequence_number_increment=32,
            participants=[alice, bob],
        )

        return pg

    @staticmethod
    def _prepare_protocol_3() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="1337")
        bob = Participant("Bob", address_hex="beef")

        checksum = GenericCRC.from_standard_checksum("CRC8 CCITT")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 16)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)
        mb.add_label(FieldType.Function.DATA, 10 * 8)
        mb.add_checksum_label(8, checksum)

        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 16)
        mb_ack.add_label(FieldType.Function.SYNC, 16)
        mb_ack.add_label(FieldType.Function.LENGTH, 8)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb_ack.add_checksum_label(8, checksum)

        pg = ProtocolGenerator(
            [mb.message_type, mb_ack.message_type],
            syncs_by_mt={mb.message_type: "0x9a7d", mb_ack.message_type: "0x9a7d"},
            preambles_by_mt={mb.message_type: "10" * 8, mb_ack.message_type: "10" * 8},
            participants=[alice, bob],
        )

        return pg

    @staticmethod
    def _prepare_protocol_4() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="1337")
        bob = Participant("Bob", address_hex="beef")

        checksum = GenericCRC.from_standard_checksum("CRC16 CCITT")

        mb = MessageTypeBuilder("data1")
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

        preamble = "10001000" * 2

        pg = ProtocolGenerator(
            [mt1, mt2, mt3],
            syncs_by_mt={mt1: "0x9a7d", mt2: "0x9a7d", mt3: "0x9a7d"},
            preambles_by_mt={mt1: preamble, mt2: preamble, mt3: preamble},
            participants=[alice, bob],
        )

        return pg

    @staticmethod
    def _prepare_protocol_5() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="1337")
        bob = Participant("Bob", address_hex="beef")
        carl = Participant("Carl", address_hex="cafe")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 16)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 16)
        mb.add_label(FieldType.Function.DST_ADDRESS, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 16)
        mb_ack.add_label(FieldType.Function.SYNC, 16)
        mb_ack.add_label(FieldType.Function.LENGTH, 8)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 16)

        pg = ProtocolGenerator(
            [mb.message_type, mb_ack.message_type],
            syncs_by_mt={mb.message_type: "0x9a7d", mb_ack.message_type: "0x9a7d"},
            preambles_by_mt={mb.message_type: "10" * 8, mb_ack.message_type: "10" * 8},
            participants=[alice, bob, carl],
        )

        return pg

    @staticmethod
    def _prepare_protocol_6() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="24")
        broadcast = Participant("Bob", address_hex="ff")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 8)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)

        pg = ProtocolGenerator(
            [mb.message_type],
            syncs_by_mt={mb.message_type: "0x8e88"},
            preambles_by_mt={mb.message_type: "10" * 8},
            participants=[alice, broadcast],
        )

        return pg

    @staticmethod
    def _prepare_protocol_7() -> ProtocolGenerator:
        alice = Participant("Alice", address_hex="313370")
        bob = Participant("Bob", address_hex="031337")
        charly = Participant("Charly", address_hex="110000")
        daniel = Participant("Daniel", address_hex="001100")
        # broadcast = Participant("Broadcast", address_hex="ff")     #TODO: Sometimes messages to broadcast

        checksum = GenericCRC.from_standard_checksum("CRC16 CC1101")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.PREAMBLE, 16)
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.DST_ADDRESS, 24)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 24)
        mb.add_label(FieldType.Function.DATA, 8 * 8)
        mb.add_checksum_label(16, checksum)

        mb_ack = MessageTypeBuilder("ack")
        mb_ack.add_label(FieldType.Function.PREAMBLE, 8)
        mb_ack.add_label(FieldType.Function.SYNC, 16)
        mb_ack.add_label(FieldType.Function.DST_ADDRESS, 24)
        mb_ack.add_checksum_label(16, checksum)

        mb_kex = MessageTypeBuilder("kex")
        mb_kex.add_label(FieldType.Function.PREAMBLE, 24)
        mb_kex.add_label(FieldType.Function.SYNC, 16)
        mb_kex.add_label(FieldType.Function.DST_ADDRESS, 24)
        mb_kex.add_label(FieldType.Function.SRC_ADDRESS, 24)
        mb_kex.add_label(FieldType.Function.DATA, 64 * 8)
        mb_kex.add_checksum_label(16, checksum)

        pg = ProtocolGenerator(
            [mb.message_type, mb_ack.message_type, mb_kex.message_type],
            syncs_by_mt={
                mb.message_type: "0x0420",
                mb_ack.message_type: "0x2222",
                mb_kex.message_type: "0x6767",
            },
            preambles_by_mt={
                mb.message_type: "10" * 8,
                mb_ack.message_type: "10" * 4,
                mb_kex.message_type: "10" * 12,
            },
            participants=[alice, bob, charly, daniel],
        )

        return pg

    @staticmethod
    def _prepare_protocol_8() -> ProtocolGenerator:
        alice = Participant("Alice")

        mb = MessageTypeBuilder("data1")
        mb.add_label(FieldType.Function.PREAMBLE, 4)
        mb.add_label(FieldType.Function.SYNC, 4)
        mb.add_label(FieldType.Function.LENGTH, 16)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)
        mb.add_label(FieldType.Function.DATA, 8 * 542)

        mb2 = MessageTypeBuilder("data2")
        mb2.add_label(FieldType.Function.PREAMBLE, 4)
        mb2.add_label(FieldType.Function.SYNC, 4)
        mb2.add_label(FieldType.Function.LENGTH, 16)
        mb2.add_label(FieldType.Function.SEQUENCE_NUMBER, 16)
        mb2.add_label(FieldType.Function.DATA, 8 * 260)

        pg = ProtocolGenerator(
            [mb.message_type, mb2.message_type],
            syncs_by_mt={mb.message_type: "0x9", mb2.message_type: "0x9"},
            preambles_by_mt={mb.message_type: "10" * 2, mb2.message_type: "10" * 2},
            sequence_number_increment=32,
            participants=[alice],
            little_endian=True,
        )

        return pg

    def test_export_to_latex(self):
        filename = os.path.expanduser("~/GIT/publications/awre/USENIX/protocols.tex")
        if os.path.isfile(filename):
            os.remove(filename)

        for i in range(1, 9):
            pg = getattr(self, "_prepare_protocol_" + str(i))()
            pg.export_to_latex(filename, i)

    @classmethod
    def get_protocol(
        cls, protocol_number: int, num_messages, num_broken_messages=0, silent=False
    ):
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
        elif protocol_number == 8:
            pg = cls._prepare_protocol_8()
        else:
            raise ValueError("Unknown protocol number")

        messages_types_with_data_field = [
            mt
            for mt in pg.protocol.message_types
            if mt.get_first_label_with_type(FieldType.Function.DATA)
        ]
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

            if len(messages_types_with_data_field) == 0:
                # set data automatically
                data = "".join(random.choice(["0", "1"]) for _ in range(data_bytes * 8))
                pg.generate_message(data=data, source=source, destination=destination)
            else:
                # search for message type with right data length
                mt = messages_types_with_data_field[
                    i % len(messages_types_with_data_field)
                ]
                data_length = mt.get_first_label_with_type(
                    FieldType.Function.DATA
                ).length
                data = "".join(random.choice(["0", "1"]) for _ in range(data_length))
                pg.generate_message(
                    message_type=mt, data=data, source=source, destination=destination
                )

            ack_message_type = next(
                (mt for mt in pg.protocol.message_types if "ack" in mt.name), None
            )
            if ack_message_type:
                pg.generate_message(
                    message_type=ack_message_type,
                    data="",
                    source=destination,
                    destination=source,
                )

        for i in range(num_broken_messages):
            msg = pg.protocol.messages[i]
            pos = random.randint(0, len(msg.plain_bits) // 2)
            msg.plain_bits[pos:] = array.array(
                "B", [random.randint(0, 1) for _ in range(len(msg.plain_bits) - pos)]
            )

        if num_broken_messages == 0:
            cls.save_protocol(
                "protocol{}_{}_messages".format(protocol_number, num_messages),
                pg,
                silent=silent,
            )
        else:
            cls.save_protocol(
                "protocol{}_{}_broken".format(protocol_number, num_broken_messages),
                pg,
                silent=silent,
            )

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
    def calculate_accuracy(messages, expected_labels, num_broken_messages=0):
        """
        Calculate the accuracy of labels compared to expected labels
        Accuracy is 100% when labels == expected labels
        Accuracy drops by 1 / len(expected_labels) for every expected label not present in labels

        :type messages: list of Message
        :type expected_labels: list of MessageType
        :return:
        """
        accuracy = sum(
            len(set(expected_labels[i]) & set(messages[i].message_type))
            / len(expected_labels[i])
            for i in range(num_broken_messages, len(messages))
        )
        try:
            accuracy /= len(messages) - num_broken_messages
        except ZeroDivisionError:
            accuracy = 0

        return accuracy * 100

    def test_against_num_messages(self):
        num_messages = list(range(1, 24, 1))
        accuracies = defaultdict(list)

        protocols = [1, 2, 3, 4, 5, 6, 7, 8]

        random.seed(0)
        np.random.seed(0)
        for protocol_nr in protocols:
            for n in num_messages:
                protocol, expected_labels = self.get_protocol(
                    protocol_nr, num_messages=n
                )
                self.run_format_finder_for_protocol(protocol)

                accuracy = self.calculate_accuracy(protocol.messages, expected_labels)
                accuracies["protocol {}".format(protocol_nr)].append(accuracy)

        self.__plot(
            num_messages,
            accuracies,
            xlabel="Number of messages",
            ylabel="Accuracy in %",
            grid=True,
        )
        self.__export_to_csv("/tmp/accuray-vs-messages", num_messages, accuracies)

    def test_against_error(self):
        Engine._DEBUG_ = False
        Preprocessor._DEBUG_ = False

        num_runs = 100

        num_messages = 30
        num_broken_messages = list(range(0, num_messages + 1))
        accuracies = defaultdict(list)
        accuracies_without_broken = defaultdict(list)

        protocols = [1, 2, 3, 4, 5, 6, 7, 8]

        random.seed(0)
        np.random.seed(0)

        with multiprocessing.Pool() as p:
            result = p.starmap(
                run_for_num_broken,
                [(i, num_broken_messages, num_messages, num_runs) for i in protocols],
            )
            for i, acc in enumerate(result):
                accuracies["protocol {}".format(i + 1)] = [a[0] for a in acc]
                accuracies_without_broken["protocol {}".format(i + 1)] = [
                    a[1] for a in acc
                ]

        self.__plot(
            100 * np.array(num_broken_messages) / num_messages,
            accuracies,
            title="Overall Accuracy vs percentage of broken messages",
            xlabel="Broken messages in %",
            ylabel="Accuracy in %",
            grid=True,
        )
        self.__plot(
            100 * np.array(num_broken_messages) / num_messages,
            accuracies_without_broken,
            title=" Accuracy of unbroken vs percentage of broken messages",
            xlabel="Broken messages in %",
            ylabel="Accuracy in %",
            grid=True,
        )
        self.__export_to_csv(
            "/tmp/accuray-vs-error",
            num_broken_messages,
            accuracies,
            relative=num_messages,
        )
        self.__export_to_csv(
            "/tmp/accuray-vs-error-without-broken",
            num_broken_messages,
            accuracies_without_broken,
            relative=num_messages,
        )

    def test_performance(self):
        Engine._DEBUG_ = False
        Preprocessor._DEBUG_ = False

        num_messages = list(range(200, 205, 5))
        protocols = [1]

        random.seed(0)
        np.random.seed(0)

        performances = defaultdict(list)

        for protocol_nr in protocols:
            print("Running for protocol", protocol_nr)
            for messages in num_messages:
                protocol, _ = self.get_protocol(protocol_nr, messages, silent=True)

                t = time.time()
                self.run_format_finder_for_protocol(protocol)
                performances["protocol {}".format(protocol_nr)].append(time.time() - t)

        # self.__plot(num_messages, performances, xlabel="Number of messages", ylabel="Time in seconds", grid=True)

    def test_performance_real_protocols(self):
        Engine._DEBUG_ = False
        Preprocessor._DEBUG_ = False

        num_runs = 100

        num_messages = list(range(8, 512, 4))
        protocol_names = ["enocean", "homematic", "rwe"]

        random.seed(0)
        np.random.seed(0)

        performances = defaultdict(list)

        for protocol_name in protocol_names:
            for messages in num_messages:
                if protocol_name == "homematic":
                    protocol = self.generate_homematic(messages, save_protocol=False)
                elif protocol_name == "enocean":
                    protocol = self.generate_enocean(messages, save_protocol=False)
                elif protocol_name == "rwe":
                    protocol = self.generate_rwe(messages, save_protocol=False)
                else:
                    raise ValueError("Unknown protocol name")

                tmp_performances = np.empty(num_runs, dtype=np.float64)
                for i in range(num_runs):
                    print(
                        "\r{0} with {1:02d} messages ({2}/{3} runs)".format(
                            protocol_name, messages, i + 1, num_runs
                        ),
                        flush=True,
                        end="",
                    )

                    t = time.time()
                    self.run_format_finder_for_protocol(protocol)
                    tmp_performances[i] = time.time() - t
                    self.clear_message_types(protocol.messages)

                mean_performance = tmp_performances.mean()
                print(" {:.2f}s".format(mean_performance))
                performances["{}".format(protocol_name)].append(mean_performance)

        self.__plot(
            num_messages,
            performances,
            xlabel="Number of messages",
            ylabel="Time in seconds",
            grid=True,
        )
        self.__export_to_csv("/tmp/performance.csv", num_messages, performances)

    @staticmethod
    def __export_to_csv(filename: str, x: list, y: dict, relative=None):
        if not filename.endswith(".csv"):
            filename += ".csv"

        with open(filename, "w") as f:
            f.write("N,")
            if relative is not None:
                f.write("NRel,")
            for y_cap in sorted(y):
                f.write(y_cap + ",")
            f.write("\n")

            for i, x_val in enumerate(x):
                f.write("{},".format(x_val))
                if relative is not None:
                    f.write("{},".format(100 * x_val / relative))

                for y_cap in sorted(y):
                    f.write("{},".format(y[y_cap][i]))
                f.write("\n")

    @staticmethod
    def __plot(x: list, y: dict, xlabel: str, ylabel: str, grid=False, title=None):
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        for y_cap, y_values in sorted(y.items()):
            plt.plot(x, y_values, label=y_cap)

        if grid:
            plt.grid()

        if title:
            plt.title(title)

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

    @classmethod
    def generate_homematic(cls, num_messages: int, save_protocol=True):
        mb_m_frame = MessageTypeBuilder("mframe")
        mb_c_frame = MessageTypeBuilder("cframe")
        mb_r_frame = MessageTypeBuilder("rframe")
        mb_a_frame = MessageTypeBuilder("aframe")

        participants = [
            Participant("CCU", address_hex="3927cc"),
            Participant("Switch", address_hex="3101cc"),
        ]

        checksum = GenericCRC.from_standard_checksum("CRC16 CC1101")
        for mb_builder in [mb_m_frame, mb_c_frame, mb_r_frame, mb_a_frame]:
            mb_builder.add_label(FieldType.Function.PREAMBLE, 32)
            mb_builder.add_label(FieldType.Function.SYNC, 32)
            mb_builder.add_label(FieldType.Function.LENGTH, 8)
            mb_builder.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)
            mb_builder.add_label(FieldType.Function.TYPE, 16)
            mb_builder.add_label(FieldType.Function.SRC_ADDRESS, 24)
            mb_builder.add_label(FieldType.Function.DST_ADDRESS, 24)
            if mb_builder.name == "mframe":
                mb_builder.add_label(FieldType.Function.DATA, 16, name="command")
            elif mb_builder.name == "cframe":
                mb_builder.add_label(
                    FieldType.Function.DATA, 16 * 4, name="command+challenge+magic"
                )
            elif mb_builder.name == "rframe":
                mb_builder.add_label(FieldType.Function.DATA, 32 * 4, name="cipher")
            elif mb_builder.name == "aframe":
                mb_builder.add_label(
                    FieldType.Function.DATA, 10 * 4, name="command + auth"
                )
            mb_builder.add_checksum_label(16, checksum)

        message_types = [
            mb_m_frame.message_type,
            mb_c_frame.message_type,
            mb_r_frame.message_type,
            mb_a_frame.message_type,
        ]
        preamble = "0xaaaaaaaa"
        sync = "0xe9cae9ca"
        initial_sequence_number = 36
        pg = ProtocolGenerator(
            message_types,
            participants,
            preambles_by_mt={mt: preamble for mt in message_types},
            syncs_by_mt={mt: sync for mt in message_types},
            sequence_numbers={mt: initial_sequence_number for mt in message_types},
            message_type_codes={
                mb_m_frame.message_type: 42560,
                mb_c_frame.message_type: 40962,
                mb_r_frame.message_type: 40963,
                mb_a_frame.message_type: 32770,
            },
        )

        for i in range(num_messages):
            mt = pg.message_types[i % 4]
            data_length = mt.get_first_label_with_type(FieldType.Function.DATA).length
            data = "".join(random.choice(["0", "1"]) for _ in range(data_length))
            pg.generate_message(
                mt,
                data,
                source=pg.participants[i % 2],
                destination=pg.participants[(i + 1) % 2],
            )

        if save_protocol:
            cls.save_protocol("homematic", pg)

        cls.clear_message_types(pg.messages)
        return pg.protocol

    @classmethod
    def generate_enocean(cls, num_messages: int, save_protocol=True):
        filename = get_path_for_data_file("enocean_bits.txt")
        enocean_bits = []
        with open(filename, "r") as f:
            for line in map(str.strip, f):
                enocean_bits.append(line)

        protocol = ProtocolAnalyzer(None)
        message_type = MessageType("empty")
        for i in range(num_messages):
            msg = Message.from_plain_bits_str(enocean_bits[i % len(enocean_bits)])
            msg.message_type = message_type
            protocol.messages.append(msg)

        if save_protocol:
            cls.save_protocol("enocean", protocol)

        return protocol

    @classmethod
    def generate_rwe(cls, num_messages: int, save_protocol=True):
        proto_file = get_path_for_data_file("rwe.proto.xml")
        protocol = ProtocolAnalyzer(signal=None, filename=proto_file)
        protocol.from_xml_file(filename=proto_file, read_bits=True)
        messages = protocol.messages

        result = ProtocolAnalyzer(None)
        message_type = MessageType("empty")
        for i in range(num_messages):
            msg = messages[i % len(messages)]  # type: Message
            msg.message_type = message_type
            result.messages.append(msg)

        if save_protocol:
            cls.save_protocol("rwe", result)

        return result

    def test_export_latex_table(self):
        def bold_latex(s):
            return r"\textbf{" + str(s) + r"}"

        comments = {
            1: "common protocol",
            2: "unusual field sizes",
            3: "contains ack and CRC8 CCITT",
            4: "contains ack and CRC16 CCITT",
            5: "three participants with ack frame",
            6: "short address",
            7: "four participants, varying preamble size, varying sync words",
            8: "nibble fields + LE",
        }

        bold = {i: defaultdict(bool) for i in range(1, 9)}
        bold[2][FieldType.Function.PREAMBLE] = True
        bold[2][FieldType.Function.SRC_ADDRESS] = True
        bold[2][FieldType.Function.DST_ADDRESS] = True

        bold[3][FieldType.Function.CHECKSUM] = True

        bold[4][FieldType.Function.CHECKSUM] = True

        bold[6][FieldType.Function.SRC_ADDRESS] = True

        bold[7][FieldType.Function.PREAMBLE] = True
        bold[7][FieldType.Function.SYNC] = True
        bold[7][FieldType.Function.SRC_ADDRESS] = True
        bold[7][FieldType.Function.DST_ADDRESS] = True

        bold[8][FieldType.Function.PREAMBLE] = True
        bold[8][FieldType.Function.SYNC] = True

        filename = os.path.expanduser(
            "~/GIT/publications/awre/USENIX/protocol_table.tex"
        )
        rowcolors = [r"\rowcolor{black!10}", r"\rowcolor{black!20}"]

        with open(filename, "w") as f:
            f.write(r"\begin{table*}[!h]" + "\n")
            f.write(
                "\t"
                + r"\caption{Properties of tested protocols whereby $\times$ means field is not present and $N_P$ is the number of participants.}"
                + "\n"
            )
            f.write("\t" + r"\label{tab:protocols}" + "\n")
            f.write("\t" + r"\centering" + "\n")
            f.write("\t" + r"\begin{tabularx}{\linewidth}{cp{2.5cm}llcccccccc}" + "\n")
            f.write("\t\t" + r"\hline" + "\n")
            f.write("\t\t" + r"\rowcolor{black!90}" + "\n")
            f.write(
                "\t\t" + r"\textcolor{white}{\textbf{\#}} & "
                r"\textcolor{white}{\textbf{Comment}} & "
                r"\textcolor{white}{$\mathbf{ N_P }$} & "
                r"\textcolor{white}{\textbf{Message}} & "
                r"\textcolor{white}{\textbf{Even/odd}} & "
                r"\multicolumn{7}{c}{\textcolor{white}{\textbf{Size of field in bit (BE=Big Endian, LE=Little Endian)}}}\\"
                "\n\t\t"
                r"\rowcolor{black!90}"
                "\n\t\t"
                r"& & & \textcolor{white}{\textbf{Type}} & \textcolor{white}{\textbf{message data}} &"
                r"\textcolor{white}{Preamble} & "
                r"\textcolor{white}{Sync} & "
                r"\textcolor{white}{Length}  & "
                r"\textcolor{white}{SRC} & "
                r"\textcolor{white}{DST} & "
                r"\textcolor{white}{SEQ Nr} & "
                r"\textcolor{white}{CRC}  \\" + "\n"
            )
            f.write("\t\t" + r"\hline" + "\n")

            rowcolor_index = 0
            for i in range(1, 9):
                pg = getattr(self, "_prepare_protocol_" + str(i))()
                assert isinstance(pg, ProtocolGenerator)

                try:
                    data1 = next(mt for mt in pg.message_types if mt.name == "data1")
                    data2 = next(mt for mt in pg.message_types if mt.name == "data2")

                    data1_len = (
                        data1.get_first_label_with_type(FieldType.Function.DATA).length
                        // 8
                    )
                    data2_len = (
                        data2.get_first_label_with_type(FieldType.Function.DATA).length
                        // 8
                    )

                except StopIteration:
                    data1_len, data2_len = 8, 64

                rowcolor = rowcolors[rowcolor_index % len(rowcolors)]
                rowcount = 0
                for j, mt in enumerate(pg.message_types):
                    if mt.name == "data2":
                        continue

                    rowcount += 1
                    if j == 0:
                        protocol_nr, participants = str(i), len(pg.participants)
                        if participants > 2:
                            participants = bold_latex(participants)
                    else:
                        protocol_nr, participants = " ", " "

                    f.write("\t\t" + rowcolor + "\n")

                    if len(pg.message_types) == 1 or (
                        mt.name == "data1"
                        and "ack" not in {m.name for m in pg.message_types}
                    ):
                        f.write(
                            "\t\t{} & {} & {} & {} &".format(
                                protocol_nr,
                                comments[i],
                                participants,
                                mt.name.replace("1", ""),
                            )
                        )
                    elif j == len(pg.message_types) - 1:
                        f.write(
                            "\t\t{} & \\multirow{{{}}}{{\\linewidth}}{{{}}} & {} & {} &".format(
                                protocol_nr,
                                -rowcount,
                                comments[i],
                                participants,
                                mt.name.replace("1", ""),
                            )
                        )
                    else:
                        f.write(
                            "\t\t{} & & {} & {} &".format(
                                protocol_nr, participants, mt.name.replace("1", "")
                            )
                        )
                    data_lbl = mt.get_first_label_with_type(FieldType.Function.DATA)

                    if mt.name == "data1" or mt.name == "data2":
                        f.write("{}/{} byte &".format(data1_len, data2_len))
                    elif mt.name == "data" and data_lbl is None:
                        f.write("{}/{} byte &".format(data1_len, data2_len))
                    elif data_lbl is not None:
                        f.write("{0}/{0} byte & ".format(data_lbl.length // 8))
                    else:
                        f.write(r"$ \times $ & ")

                    for t in (
                        FieldType.Function.PREAMBLE,
                        FieldType.Function.SYNC,
                        FieldType.Function.LENGTH,
                        FieldType.Function.SRC_ADDRESS,
                        FieldType.Function.DST_ADDRESS,
                        FieldType.Function.SEQUENCE_NUMBER,
                        FieldType.Function.CHECKSUM,
                    ):
                        lbl = mt.get_first_label_with_type(t)
                        if lbl is not None:
                            if bold[i][lbl.field_type.function]:
                                f.write(bold_latex(lbl.length))
                            else:
                                f.write(str(lbl.length))
                            if lbl.length > 8 and t in (
                                FieldType.Function.LENGTH,
                                FieldType.Function.SEQUENCE_NUMBER,
                            ):
                                f.write(
                                    " ({})".format(
                                        bold_latex("LE") if pg.little_endian else "BE"
                                    )
                                )
                        else:
                            f.write(r"$ \times $")

                        if t != FieldType.Function.CHECKSUM:
                            f.write(" & ")
                        else:
                            f.write(r"\\" + "\n")

                rowcolor_index += 1

            f.write("\t" + r"\end{tabularx}" + "\n")

            f.write(r"\end{table*}" + "\n")
