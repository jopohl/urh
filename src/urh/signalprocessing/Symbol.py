class Symbol(object):
    def __init__(self, name: str, nbits: int, pulsetype: int, nsamples: int):
        """
        :param nbits: Number of bits this Symbol covers
        :param name: Name of the symbol (one char)
        :param pulsetype: 0 for 0 pulse, 1 für 1 pulse
        :param nsamples: Num Samples for this Symbol. Needed in Modulator.
        """
        self.name = name
        self.pulsetype = pulsetype
        self.nbits = nbits
        self.nsamples = nsamples

    def __repr__(self):
        return "{0} ({1}:{2})".format(self.name, self.pulsetype, self.name)

    def __deepcopy__(self, memo):
        result = Symbol(self.name, self.nbits, self.pulsetype, self.nsamples)
        memo[id(self)] = result
        return result
