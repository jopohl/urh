import array
import random

import matplotlib.pyplot as plt
import numpy as np

from tests.awre.AWRETestCase import AWRETestCase
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Participant import Participant


class AWRExperiments(AWRETestCase):
    def __prepare_protocol_1(self, num_messages, num_broken_messages=0):
        """

        :param num_messages:
        :param num_broken_messages: probability that a bit is flipped
        :return:
        """
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

        random.seed(0)
        np.random.seed(0)
        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = alice, bob
                data_length = 8
            else:
                source, destination = bob, alice
                data_length = 16

            if num_broken_messages == 0:
                pg.generate_message(data=pg.decimal_to_bits(random.randint(0, 2 ** (data_length - 1)), data_length),
                                    source=source, destination=destination)
            else:
                pg.generate_message(data=pg.decimal_to_bits(random.randint(0, 2 ** (data_length - 1)), data_length),
                                    source=source, destination=destination)

                msg = pg.protocol.messages[-1]
                pos = random.randint(0, len(msg.plain_bits) // 2)
                msg.plain_bits[pos:] = array.array("B", [random.randint(0, 1) for _ in range(len(msg.plain_bits) - pos)])
                num_broken_messages -= 1

        self.save_protocol("protocol_1", pg)

        # Delete message type information -> no prior knowledge
        self.clear_message_types(pg.protocol.messages)

        return pg.protocol, mb.message_type

    def __prepare_protocol_1a(self, num_messages, num_broken_messages=0):
        """

        :param num_messages:
        :param num_broken_messages: probability that a bit is flipped
        :return:
        """
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

        random.seed(0)
        np.random.seed(0)
        for i in range(num_messages):
            if i % 2 == 0:
                source, destination = alice, bob
                data_length = 8
            else:
                source, destination = bob, alice
                data_length = 16

            if num_broken_messages == 0:
                pg.generate_message(data=pg.decimal_to_bits(random.randint(0, 2 ** (data_length - 1)), data_length),
                                    source=source, destination=destination)
            else:
                l = random.choice([8, 16, 64])
                pg.generate_message(data=pg.decimal_to_bits(random.randint(0, 2 ** (l - 1)), l))
                num_broken_messages -= 1

        self.save_protocol("protocol_1a", pg)

        # Delete message type information -> no prior knowledge
        self.clear_message_types(pg.protocol.messages)

        return pg.protocol, mb.message_type


    @staticmethod
    def calculate_accuracy(labels, expected_labels, penalty_for_additional_labels=True):
        """
        Calculate the accuracy of labels compared to expected labels
        Accuracy is 100% when labels == expected labels
        Accuracy drops by 1 / len(expected_labels) for every expected label not present in labels

        :param penalty_for_additional_labels:
        :type labels: list of ProtocolLabel
        :type expected_labels: list of ProtocolLabel
        :return:
        """

        accuracy = 1
        for lbl in expected_labels:
            try:
                next(l for l in labels if
                     l.start == lbl.start and l.end == lbl.end and l.field_type.function == lbl.field_type.function)
                found = True
            except StopIteration:
                found = False

            if not found:
                accuracy -= 1 / len(expected_labels)

        if penalty_for_additional_labels and len(labels) > len(expected_labels):
            # Penalty if there are more labels found than present
            accuracy -= (len(labels) - len(expected_labels)) / len(expected_labels)

        return max(0, accuracy * 100)

    def test_against_num_messages(self):
        num_messages = list(range(1, 12))
        accuracies = []

        for n in num_messages:
            protocol, expected_labels = self.__prepare_protocol_1(num_messages=n)

            ff = FormatFinder(protocol.messages)
            ff.known_participant_addresses.clear()
            ff.perform_iteration()

            self.assertEqual(len(ff.message_types), 1)

            print("Expected ({}): {}".format(len(expected_labels), expected_labels))
            print(ff.message_types[0])

            accuracy = self.calculate_accuracy(ff.message_types[0], expected_labels)
            accuracies.append(accuracy)

        plt.plot(num_messages, accuracies)
        plt.xlabel("Number of messages")
        plt.ylabel("Accuracy in %")
        plt.show()

    def test_against_broken_messages(self):
        num_messages = 16
        num_broken_messages = list(range(0, num_messages))
        accuracies = []

        for broken in num_broken_messages:
            protocol, expected_labels = self.__prepare_protocol_1(num_messages=num_messages, num_broken_messages=broken)

            ff = FormatFinder(protocol.messages)
            ff.known_participant_addresses.clear()
            ff.perform_iteration()

            # self.assertEqual(len(ff.message_types), 1)

            print("Expected ({}): {}".format(len(expected_labels), expected_labels))
            print(ff.message_types[0])

            accuracy = self.calculate_accuracy(ff.message_types[0], expected_labels)
            accuracies.append(accuracy)

        plt.plot(num_broken_messages, accuracies)
        plt.xlabel("Number of broken messages")
        plt.ylabel("Accuracy in %")
        plt.show()
