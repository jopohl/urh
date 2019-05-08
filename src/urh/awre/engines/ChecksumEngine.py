import copy
import math
from collections import defaultdict

import numpy as np
from urh.util.WSPChecksum import WSPChecksum

from urh.awre.CommonRange import ChecksumRange
from urh.awre.engines.Engine import Engine
from urh.cythonext import awre_util
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
            for index in message_indices:
                bits = self.bitvectors[index]
                data_start, data_stop, crc_start, crc_stop = WSPChecksum.search_for_wsp_checksum(bits)
                if (data_start, data_stop, crc_start, crc_stop) != (0, 0, 0, 0):
                    checksum_range = ChecksumRange(start=crc_start, length=crc_stop-crc_start,
                                                   data_range_start=data_start, data_range_end=data_stop,
                                                   crc=WSPChecksum(), score=1/len(message_indices),
                                                   field_type="checksum", message_indices={index})
                    try:
                        present = next(c for c in checksums_for_length if c == checksum_range)
                        present.message_indices.add(index)
                    except StopIteration:
                        checksums_for_length.append(checksum_range)
                    continue

                crc_object, data_start, data_stop, crc_start, crc_stop = crc.guess_all(bits,
                                                                                       ignore_positions=self.already_labeled_cols)

                if (crc_object, data_start, data_stop, crc_start, crc_stop) != (0, 0, 0, 0, 0):
                    checksum_range = ChecksumRange(start=crc_start, length=crc_stop - crc_start,
                                                   data_range_start=data_start, data_range_end=data_stop,
                                                   crc=copy.copy(crc_object), score=1 / len(message_indices),
                                                   field_type="checksum", message_indices={index}
                                                   )

                    try:
                        present = next(rng for rng in checksums_for_length if rng == checksum_range)
                        present.message_indices.add(index)
                        continue
                    except StopIteration:
                        pass

                    checksums_for_length.append(checksum_range)

                    matching = awre_util.check_crc_for_messages(message_indices, self.bitvectors,
                                                                data_start, data_stop,
                                                                crc_start, crc_stop,
                                                                *crc_object.get_parameters())

                    checksum_range.message_indices.update(matching)

            # Score ranges
            for rng in checksums_for_length:
                rng.score = len(rng.message_indices) / len(message_indices)

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
