import array
import math
from collections import defaultdict

import numpy as np

from urh.awre.CommonRange import ChecksumRange
from urh.awre.engines.Engine import Engine
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
            checksums_for_length = []
            for i, index in enumerate(message_indices):
                bits = self.bitvectors[index]
                crc_object, start, stop, crc_start, crc_stop = crc.guess_all(bits,
                                                                             ignore_positions=self.already_labeled_cols)

                if (crc_object, start, stop, crc_start, crc_stop) != (0, 0, 0, 0, 0):
                    checksums_for_length.append(ChecksumRange(start=crc_start,
                                                              length=crc_stop - crc_start,
                                                              data_range_start=start,
                                                              data_range_end=stop,
                                                              crc=crc_object,
                                                              score=1 / len(message_indices),
                                                              field_type="checksum",
                                                              message_indices={index}
                                                              ))

                    for j in range(i + 1, len(message_indices)):
                        bits = self.bitvectors[message_indices[j]]
                        if crc_object.crc(bits[:crc_start]) == array.array("B", bits[crc_start:crc_stop]):
                            checksums_for_length[-1].message_indices.add(message_indices[j])
                            checksums_for_length[-1].score += 1 / len(message_indices)

            try:
                result.append(max(checksums_for_length, key=lambda x: x.score))
            except ValueError:
                pass  # no checksums found for this length

        self._debug("Found Checksums", result)
        try:
            max_scored = max(filter(lambda x: len(x.message_indices) >= 2 and x.score >= self.minimum_score, result),
                             key=lambda x: x.score)
        except ValueError:
            return []

        result = list(filter(lambda x: x.crc == max_scored.crc, result))
        self._debug("Filtered Checksums", result)

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
