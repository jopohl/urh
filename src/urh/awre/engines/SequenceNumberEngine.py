import numpy as np

from urh.awre.engines.Engine import Engine
from urh.util import util


class SequenceNumberEngine(Engine):
    def __init__(self, bitvectors):
        """

        :type bitvectors: list of np.ndarray
        :param bitvectors: bitvectors behind the synchronization
        """
        self.bitvectors = bitvectors

    def find(self, n_gram_length=8, minimum_score=0.1):
        max_len = len(max(self.bitvectors, key=len))

        corr_coeff_vector = []
        for j in range(0, max_len, n_gram_length):
            corr_coeff = self.corr_coeff([util.bits_to_number(bv[j:j+n_gram_length]) for bv in self.bitvectors])
            corr_coeff_vector.append(corr_coeff)
        print(corr_coeff_vector)


    @staticmethod
    def corr_coeff(values):
        return np.corrcoef(range(len(values)), values)[1, 0]