from multiprocessing import Connection


class LiveModulator(object):
    """
    This class is used in continuous sending mode.
    You pass a list of messages and modulators to it, and it takes care of modulating the messages sequentially.
    This avoids running out of RAM for large amounts of messages.
    The modulated data is passed to a multiprocessing connection object.
    """

    def __init__(self, messages, modulators, data_connection: Connection, ctrl_connection: Connection):
        """
        
        :type messages: list of Message 
        :type modulators: list of Modulator 
        """
        pass
