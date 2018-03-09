from urh.awre.CommonRange import CommonBitRange
from urh.awre.Histogram import Histogram
import numpy as np

class Engine(object):
    _DEBUG_ = True

    def _debug(self, *args):
        if self._DEBUG_:
            print("[{}]".format(self.__class__.__name__), *args)


    @staticmethod
    def find_common_ranges_by_cluster(bitvectors, clustered_bitvectors):
        """

        :type bitvectors: list of np.ndarray
        :type clustered_bitvectors: dict
        :rtype: dict[int, list of CommonBitRange]
        """
        histograms = {
            cluster: Histogram(bitvectors, message_indices)
            for cluster, message_indices in clustered_bitvectors.items()
        }

        common_ranges_by_cluster = {
            cluster: histogram.find_common_ranges(alpha=0.95)
            for cluster, histogram in histograms.items()
        }

        return common_ranges_by_cluster