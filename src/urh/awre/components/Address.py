from collections import defaultdict

import numpy as np
from urh import constants
from urh.awre.CommonRange import CommonRange
from urh.cythonext import util
from urh.awre.components.Component import Component
from urh.signalprocessing.MessageType import MessageType


class Address(Component):
    MIN_ADDRESS_LENGTH = 8  # Address should be at least one byte

    def __init__(self, xor_matrix, priority=2, predecessors=None, enabled=True, backend=None, default_messagetype=None):
        super().__init__(priority, predecessors, enabled, backend, default_messagetype)
        self.xor_matrix = xor_matrix

    def _py_find_field(self, messages):
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

        print(constants.color.BOLD + "Result after Step 1" +constants.color.END)
        self.__print_ranges(equal_ranges_per_participant)

        # Step 2: Now we want to find our address candidates.
        # We do this by weighting them in order of LCS they share with each other
        scored_candidates = self.find_candidates([cr for crl in equal_ranges_per_participant.values() for cr in crl])
        """:type : dict[str, int] """

        highscored = sorted(scored_candidates, key=scored_candidates.get, reverse=True)[:2]
        print(sorted(scored_candidates, key=scored_candidates.get, reverse=True))
        assert len(highscored[0]) == len(highscored[1]) # TODO: Perform aligning/take next highscored value if lengths do not match

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
        clusters = {"together": defaultdict(set), "isolated": defaultdict(set)}
        """:type: dict[str, dict[tuple[int.int],set[int]]]"""

        all_candidates = [cr for crl in scored_candidates_per_participant.values() for cr in crl]
        # Check for crossmatch and cluster in together and splitted addresses
        # Perform a merge by only saving the ranges and applying messages
        for candidate in sorted(all_candidates):
            if any(c.start == candidate.start and c.end == candidate.end and c.bits != candidate.bits for c in all_candidates):
                # Crossmatch! This is a address
                if any(c.start == candidate.end or c.end == candidate.start for c in all_candidates):
                     clusters["together"][(candidate.start, candidate.end)].update(candidate.messages)
                else:
                    clusters["isolated"][(candidate.start, candidate.end)].update(candidate.messages)

        # Merge clusters and create labels
        print(clusters)

        for participant, ranges in scored_candidates_per_participant.items():
            for rng in ranges:
                for msg in rng.messages:
                    messages[msg].message_type.add_protocol_label(rng.start, rng.end, name="Address", auto_created=True)

        print(clusters)
        print(scored_candidates_per_participant)

       # print(scored_candidates)

        # Now we perform a scoring of the address candidates. There are two ways to score:
            # 1) Address appears as substring in other candidates
            # 2) Opposite Address appears in same range for other participant

        #self.__print_clustered(clustered_addresses)

        # Now we search for ranges that are common in a cluster and contain different bit values. There are two possibilities:
        #   1) If the protocol contains ACKs, these different values are the addresses or at least good candidates for them
        #   2) If the protocol does not contain ACKs, these values contain both addresses and need to be splitted against each other
        # We assume, that the protocol contains ACKs and if we do not find any use the strategy from 2).



        #print(clustered_addresses)
        # Step 2: Align sequences together (correct bit shifts, align to byte)

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

    def __print_clustered(self, clustered_addresses):
        for bl in sorted(clustered_addresses):
            print(constants.color.BOLD + "Byte length " + str(bl) + constants.color.END)
            for (start, end), bits in sorted(clustered_addresses[bl].items()):
                print(start, end, bits)

    def __print_ranges(self, equal_ranges_per_participant):
        for parti in sorted(equal_ranges_per_participant):
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


