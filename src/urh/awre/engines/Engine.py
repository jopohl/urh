from urh.awre.CommonRange import CommonRange
from urh.awre.Histogram import Histogram
import numpy as np
from urh.cythonext import awre_util
import itertools


class Engine(object):
    _DEBUG_ = False

    def _debug(self, *args):
        if self._DEBUG_:
            print("[{}]".format(self.__class__.__name__), *args)

    @staticmethod
    def find_common_ranges_by_cluster(msg_vectors, clustered_bitvectors, alpha=0.95, range_type="bit"):
        """

        :param alpha: How many percent of values must be equal per range?
        :param range_type: Describes what kind of range this is: bit, hex or byte.
                           Needed for conversion of range start / end later
        :type msg_vectors: list of np.ndarray
        :type clustered_bitvectors: dict
        :rtype: dict[int, list of CommonRange]
        """
        histograms = {
            cluster: Histogram(msg_vectors, message_indices)
            for cluster, message_indices in clustered_bitvectors.items()
        }

        common_ranges_by_cluster = {
            cluster: histogram.find_common_ranges(alpha=alpha, range_type=range_type)
            for cluster, histogram in histograms.items()
        }

        return common_ranges_by_cluster

    @staticmethod
    def find_common_ranges_exhaustive(msg_vectors, msg_indices, range_type="bit") -> list:
        result = []

        for i, j in itertools.combinations(msg_indices, 2):
            for rng in Histogram(msg_vectors, indices=[i, j]).find_common_ranges(alpha=1, range_type=range_type):
                try:
                    common_range = next(cr for cr in result if cr.start == rng.start and cr.value.tobytes() == rng.value.tobytes())
                    common_range.message_indices.update({i, j})
                except StopIteration:
                    result.append(rng)

        return result

    @staticmethod
    def ignore_already_labeled(common_ranges, already_labeled):
        """
        Shrink the common ranges so that they not overlap with already labeled ranges.
        Empty common ranges are removed after shrinking

        :type common_ranges: list of CommonRange
        :type already_labeled: list of tuple
        :return: list of CommonRange
        """
        result = []
        for common_range in common_ranges:
            range_result = [common_range]
            for start, end in already_labeled:
                for rng in range_result[:]:
                    range_result.remove(rng)
                    range_result.extend(rng.ensure_not_overlaps(start, end))
            result.extend(range_result)

        return result

    @staticmethod
    def find_longest_common_sub_sequences(seq1, seq2) -> list:
        result = []
        if seq1 is None or seq2 is None:
            return result

        indices = awre_util.find_longest_common_sub_sequence_indices(seq1, seq2)
        for ind in indices:
            s = seq1[slice(*ind)]
            if len(s) > 0:
                result.append(s)

        return result
