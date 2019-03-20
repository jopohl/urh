import math
from collections import defaultdict

import numpy as np

from urh.awre.CommonRange import CommonRange, ChecksumRange
from urh.awre.engines.Engine import Engine
from urh.util import util
from urh.util.GenericCRC import GenericCRC


class ChecksumEngine(Engine):
    def __init__(self, bitvectors, n_gram_length=8, minimum_score=0.9, already_labeled: list = None):
        """
        :type bitvectors: list of np.ndarray
        :param bitvectors: bitvectors behind the synchronization
        """
        self.bitvectors = bitvectors
        self.n_gram_length = n_gram_length
        self.minimum_score = minimum_score
        if already_labeled is None:
            self.already_labeled_cols = set()
        else:
            self.already_labeled_cols = {e for rng in already_labeled for e in range(*rng)}

    def find(self):
        result = list()
        bitvectors_by_n_gram_length = defaultdict(list)
        for i, bitvector in enumerate(self.bitvectors):
            bin_num = int(math.ceil(len(bitvector) / self.n_gram_length))
            bitvectors_by_n_gram_length[bin_num].append(i)

        crc = GenericCRC()
        for length, message_indices in bitvectors_by_n_gram_length.items():
            for i, index in enumerate(message_indices):
                inpt = self.bitvectors[index]
                crc_parameter, start, stop, crc_start, crc_stop = crc.guess_all(inpt)
                if (crc_parameter, start, stop, crc_start, crc_stop) != (0,0,0,0,0):
                    result.append(ChecksumRange(start=crc_start,
                                                length=crc_stop-crc_start,
                                                score=1,
                                                field_type="checksum",
                                                message_indices=message_indices
                                                ))
                    crc.set_crc_parameters(crc_parameter)
                    for j in range(i+1, len(message_indices)):
                        inpt = self.bitvectors[message_indices[j]]
                        if crc.crc(inpt) == inpt[crc_start:crc_stop]:
                            result[-1].message_indices.add(j)
        return result

    @staticmethod
    def calc_score(diff_frequencies: dict) -> float:
        """
        Calculate the score based on the distribution of differences
          1. high if one constant (!= zero) dominates
          2. Other constants (!= zero) should lower the score, zero means sequence number stays same for some messages

        :param diff_frequencies: Frequencies of decimal differences between columns of subsequent messages
                                 e.g. {-255: 3, 1: 1020} means -255 appeared 3 times and 1 appeared 1020 times
        :return: a score between 0 and 1
        """
        total = sum(diff_frequencies.values())
        num_zeros = sum(v for k, v in diff_frequencies.items() if k == 0)
        if num_zeros == total:
            return 0

        try:
            most_frequent = ChecksumEngine.get_most_frequent(diff_frequencies)
        except ValueError:
            return 0

        return diff_frequencies[most_frequent] / (total - num_zeros)