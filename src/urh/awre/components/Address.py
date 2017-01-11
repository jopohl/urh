from collections import defaultdict

import numpy as np
from urh import constants
from urh.awre.CommonRange import CommonRange
from urh.cythonext import util
from urh.awre.components.Component import Component
from urh.signalprocessing.MessageType import MessageType


class Address(Component):
    MIN_ADDRESS_LENGTH = 8  # Address should be at least one byte

    def __init__(self, fieldtypes, xor_matrix, priority=2, predecessors=None, enabled=True, backend=None, messagetypes=None):
        super().__init__(priority, predecessors, enabled, backend, messagetypes)
        self.xor_matrix = xor_matrix

        self.dst_field_type = next((ft for ft in fieldtypes if ft.function == ft.Function.DST_ADDRESS), None)
        self.src_field_type = next((ft for ft in fieldtypes if ft.function == ft.Function.SRC_ADDRESS), None)

        self.dst_field_name = self.dst_field_type.caption if self.dst_field_type else "DST address"
        self.src_field_name = self.src_field_type.caption if self.src_field_type else "SRC address"

    def _py_find_field(self, messages, verbose=False):
        """

        :type messages: list of urh.signalprocessing.Message.Message
        :return:
        """
        msg_indices_per_participant = defaultdict(list)
        """:type : dict[urh.signalprocessing.Participant.Participant, list[int]] """

        for i, msg in enumerate(messages):
            msg_indices_per_participant[msg.participant].append(i)


        # Cluster participants
        equal_ranges_per_participant = defaultdict(list)
        """:type : dict[urh.signalprocessing.Participant.Participant, list[CommonRange]] """

        alignment = 8

        # Step 1: Find equal ranges for participants by evaluating the XOR matrix participant wise
        for participant, participant_msg_indices in msg_indices_per_participant.items():
            for i, msg_index in enumerate(participant_msg_indices):
                msg = messages[msg_index]
                bitvector_str = msg.decoded_bits_str

                for other_index in participant_msg_indices[i+1:]:
                    other_msg = messages[other_index]
                    xor_vec = self.xor_matrix[msg_index, other_index][self.xor_matrix[msg_index, other_index] != -1] # -1 = End of Vector

                    # addresses are searched across message types, as we assume them to be in almost every message
                    # therefore we need to consider message types of both messages we compare and ignore already labeled areas
                    unlabeled_ranges = msg.message_type.unlabeled_ranges_with_other_mt(other_msg.message_type)
                    for rng_start, rng_end in unlabeled_ranges:
                        start = 0
                        # The last 1 marks end of sequence, and prevents swallowing long zero sequences at the end
                        cmp_vector = np.append(xor_vec[rng_start:rng_end], 1)
                        for end in np.where(cmp_vector == 1)[0]:
                            if end - start >= self.MIN_ADDRESS_LENGTH:
                                equal_range_start = alignment * ((rng_start + start) // alignment)
                                equal_range_end = alignment * ((rng_start + end) // alignment)
                                bits = bitvector_str[equal_range_start:equal_range_end]

                                # Did we already found this range?
                                cr = next((cr for cr in equal_ranges_per_participant[participant] if
                                          cr.start == equal_range_start and cr.end == equal_range_end
                                          and cr.bits == bits), None)

                                # If not: Create it
                                if cr is None:
                                    cr = CommonRange(equal_range_start, equal_range_end, bits)
                                    equal_ranges_per_participant[participant].append(cr)

                                cr.messages.add(msg_index)
                                cr.messages.add(other_index)

                            start = end + alignment

        if verbose:
            print(constants.color.BOLD + "Result after Step 1" +constants.color.END)
            self.__print_ranges(equal_ranges_per_participant)

        # Step 2: Now we want to find our address candidates.
        # We do this by weighting them in order of LCS they share with each other
        scored_candidates = self.find_candidates([cr for crl in equal_ranges_per_participant.values() for cr in crl])
        """:type : dict[str, int] """

        try:
            highscored = next(self.choose_candidate_pair(scored_candidates))
            assert len(highscored[0]) == len(highscored[1])
        except (StopIteration, AssertionError):
            return

        if verbose:
            print(scored_candidates)
            print(sorted(scored_candidates, key=scored_candidates.get, reverse=True))

        # Now get the common_ranges we need
        scored_candidates_per_participant = defaultdict(list)
        """:type : dict[urh.signalprocessing.Participant.Participant, list[CommonRange]] """

        for participant, ranges in equal_ranges_per_participant.items():
            for equal_range in ranges:
                for h in highscored:
                    rng = equal_range.pos_of_hex(h)
                    if rng is not None:
                        start, end = rng
                        bits = equal_range.bits[start:end]
                        rel_start = equal_range.start + start
                        rel_end = rel_start + (end - start)
                        cr = next((cr for cr in scored_candidates_per_participant[participant] if cr.start == rel_start
                                                                                               and cr.end == rel_end and
                                                                                               cr.bits == bits), None)
                        if cr is None:
                            cr = CommonRange(rel_start, rel_end, bits)
                            scored_candidates_per_participant[participant].append(cr)

                        cr.messages.update(equal_range.messages)

        # Now we have the highscored ranges per participant
        # If there is a crossmatch of the ranges we are good and found the addresses!
        # We have something like:
        #
        # Participant: Alice (A):                               Participant: Bob (B):
        # =======================                               =====================
        #
        # Range	   Value     Messages                           Range	   Value     Messages
        # -----    -----     --------                           -----      -----     --------
        # 72-96    1b6033    {1, 5, 9, 13, 17, 20}              72-96      78e289    {11, 3, 15, 7}
        # 88-112   1b6033    {2, 6, 10, 14, 18}                 88-112     78e289    {4, 8, 12, 16, 19}
        # 112-136  78e289    {2, 6, 10, 14, 18}                 112-136    1b6033    {0, 4, 8, 12, 16, 19}
        #

        # If the value doubles for the same participant in other range, then we need to create a new message type
        # We consider the default case (=default message type) to have addresses followed by each other
        # Furthermore, we assume if there is only one address per message type, it is the destination address
        clusters = {"default": defaultdict(set), "ack": defaultdict(set)}
        """:type: dict[str, dict[tuple[int.int],set[int]]]"""

        all_candidates = [cr for crl in scored_candidates_per_participant.values() for cr in crl]
        # Check for crossmatch and cluster in together and splitted addresses
        # Perform a merge by only saving the ranges and applying messages
        for candidate in sorted(all_candidates):
            if any(c.start == candidate.start and c.end == candidate.end and c.bits != candidate.bits for c in all_candidates):
                # Crossmatch! This is a address
                if any(c.start == candidate.end or c.end == candidate.start for c in all_candidates):
                     clusters["default"][(candidate.start, candidate.end)].update(candidate.messages)
                else:
                    clusters["ack"][(candidate.start, candidate.end)].update(candidate.messages)

        msg_clusters =  {cname: set(i for s in ranges.values() for i in s) for cname, ranges in clusters.items()}

        # If there are no addresses in default message type prevent evaluating everything as ACK
        if not msg_clusters["default"]:
            msg_clusters["ack"] = set()
            scored_candidates_per_participant.clear()

        self.assign_messagetypes(messages, msg_clusters)

        # Now try to find the addresses of the participants to separate SRC and DST address later
        self.assign_participant_addresses(messages, list(scored_candidates_per_participant.keys()), highscored)

        for participant, ranges in scored_candidates_per_participant.items():
            for rng in ranges:
                for msg_index in rng.messages:
                    msg = messages[msg_index]

                    if msg.message_type.name == "ack":
                       field_type = self.dst_field_type
                       name = self.dst_field_name
                    elif msg.participant:
                        if rng.hex_value == msg.participant.address_hex:
                            name = self.src_field_name
                            field_type = self.src_field_type
                        else:
                            name = self.dst_field_name
                            field_type = self.dst_field_type
                    else:
                        name = "Address"
                        field_type = None

                    if not any(lbl.name == name and lbl.auto_created for lbl in msg.message_type):
                        msg.message_type.add_protocol_label(rng.start, rng.end - 1, name=name,
                                                            auto_created=True, type=field_type)


    @staticmethod
    def find_candidates(candidates):
        """
        Find candidate addresses using LCS algorithm
        perform a scoring based on how often a candidate appears in a longer candidate

        Input is something like
        ------------------------
        ['1b6033', '1b6033fd57', '701b603378e289', '20701b603378e289000c62',
        '1b603300', '78e289757e', '7078e2891b6033000000', '207078e2891b6033000000']

        Output like
        -----------
        {'1b6033': 18, '1b6033fd57': 1, '701b603378e289': 2, '207078e2891b6033000000': 1,
        '57': 1, '7078e2891b6033000000': 2, '78e289757e': 1, '20701b603378e289000c62': 1,
        '78e289': 4, '1b603300': 3}

        :type candidates: list of CommonRange
        :return:
        """

        result = defaultdict(int)
        for i, c_i in enumerate(candidates):
            for j in range(i, len(candidates)):
                lcs = util.longest_common_substring(c_i.hex_value, candidates[j].hex_value)
                if lcs:
                    result[lcs] += 1

        return result

    @staticmethod
    def choose_candidate_pair(candidates):
        """
        Choose a pair of address candidates ensuring they have the same length and starting with the highest scored ones

        :type candidates: dict[str, int]
        :param candidates: Count how often the longest common substrings appeared in the messages
        :return:
        """
        highscored = sorted(candidates, key=candidates.get, reverse=True)
        for i, h_i in enumerate(highscored):
            for h_j in highscored[i+1:]:
                if len(h_i) == len(h_j):
                    yield (h_i, h_j)

    @staticmethod
    def assign_participant_addresses(messages, participants, hex_addresses):
        """

        :type participants: list[urh.signalprocessing.Participant.Participant]
        :type hex_addresses: tuple[str]
        :type messages: list[urh.signalprocessing.Message.Message]
        :return:
        """
        try:
            participants.remove(None)
        except ValueError:
            pass

        if len(participants) != len(hex_addresses):
            return

        if len(participants) == 0:
            return #  No chance


        score = {p: {addr: 0 for addr in hex_addresses} for p in participants}

        for i in range(1, len(messages)):
            msg = messages[i]
            prev_msg = messages[i-1]

            if msg.message_type.name == "ack":
                addr = next(addr for addr in hex_addresses if addr in msg.decoded_hex_str)
                if addr in prev_msg.decoded_hex_str:
                    score[prev_msg.participant][addr] += 1

        for p in participants:
            p.address_hex = max(score[p], key=score[p].get)

    def __print_clustered(self, clustered_addresses):
        for bl in sorted(clustered_addresses):
            print(constants.color.BOLD + "Byte length " + str(bl) + constants.color.END)
            for (start, end), bits in sorted(clustered_addresses[bl].items()):
                print(start, end, bits)

    def __print_ranges(self, equal_ranges_per_participant):
        for parti in sorted(equal_ranges_per_participant):
            if parti is None:
                continue

            print("\n" + constants.color.UNDERLINE + str(parti.name) + " (" + parti.shortname+ ")" + constants.color.END)
            address1 = "000110110110000000110011"
            address2 = "011110001110001010001001"

            assert len(address1) % 8 == 0
            assert len(address2) % 8 == 0

            print("address1", constants.color.BLUE, address1 + " (" +hex(int("".join(map(str, address1)), 2)) +")", constants.color.END)
            print("address2", constants.color.GREEN, address2 + " (" + hex(int("".join(map(str, address2)), 2)) + ")",
                  constants.color.END)

            print()

            for common_range in sorted(equal_ranges_per_participant[parti]):
                assert isinstance(common_range, CommonRange)
                bits_str = common_range.bits
                format_start = ""
                if address1 in bits_str and address2 not in bits_str:
                    format_start = constants.color.BLUE
                if address2 in bits_str and address1 not in bits_str:
                    format_start = constants.color.GREEN
                if address1 in bits_str and address2 in bits_str:
                    format_start = constants.color.RED + constants.color.BOLD

                # For Bob the adress 1b60330 is found to be 0x8db0198000 which is correct,
                # as it starts with a leading 1 in all messages.
                # This is the last Bit of e0003 (Broadcast) or 78e289  (Other address)
                # Code to verify: hex(int("1000"+bin(int("1b6033",16))[2:]+"000",2))
                # Therefore we need to check for partial bits inside the address candidates to be sure we find the correct ones
                occurences = len(common_range.messages)
                print(common_range.start, common_range.end,
                      "({})\t".format(occurences),
                      format_start + common_range.hex_value + "\033[0m", common_range.byte_len,
                      bits_str, "(" + ",".join(map(str, common_range.messages)) + ")")


