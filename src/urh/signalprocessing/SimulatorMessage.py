class SimulatorMessage(object):

    def __init__(self, name, source=None, destination=None):
        self.name = name
        self.labels = []
        self.source = source
        self.destination = destination