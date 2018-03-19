from urh.awre.CommonRange import CommonRange
from urh.awre.Histogram import Histogram
import numpy as np
from urh.cythonext import awre_util

class Engine(object):
    _DEBUG_ = True

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
