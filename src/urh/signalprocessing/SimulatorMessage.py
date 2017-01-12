class SimulatorMessage(object):

    def __init__(self, name, labels=[], source=None, destination=None):
        self.name = name
        self.labels = labels
        self.source = source
        self.destination = destination