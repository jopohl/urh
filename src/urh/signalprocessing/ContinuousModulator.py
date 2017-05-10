import time
from threading import Thread

from multiprocessing import Process

from urh.signalprocessing.Modulator import Modulator
from urh.util.Logger import logger
from urh.util.RingBuffer import RingBuffer


class ContinuousModulator(object):
    """
    This class is used in continuous sending mode.
    You pass a list of messages and modulators to it, and it takes care of modulating the messages sequentially.
    This avoids running out of RAM for large amounts of messages.
    """

    BUFFER_SIZE_MB = 100
    WAIT_TIMEOUT = 0.1

    def __init__(self, messages, modulators):
        """
        
        :type messages: list of Message 
        :type modulators: list of Modulator 
        """
        self.messages = messages
        self.modulators = modulators

        self.ring_buffer = RingBuffer(int(self.BUFFER_SIZE_MB*10**6)//8)

        self.current_message_index = 0

        self.abort = False
        self.process = Process(target=self.modulate_continuously)
        self.process.daemon = True

        self.data_connection = None

    def start(self):
        try:
            self.process.start()
        except RuntimeError as e:
            logger.debug(str(e))

    def stop(self):
        self.abort = True

        try:
            self.process.join(0.1)
        except RuntimeError as e:
            logger.debug(str(e))

        if self.process.is_alive():
            self.process.terminate()
            self.process.join()

        logger.debug("Stopped continuous modulation")

    def modulate_continuously(self):
        pos = 0
        while True:
            for i, message in enumerate(self.messages):
                if self.abort:
                    return

                self.current_message_index = i
                modulator = self.modulators[message.modulator_indx]  # type: Modulator
                modulator.modulate(start=pos, data=message.encoded_bits, pause=message.pause)
                while not self.ring_buffer.will_fit(len(modulator.modulated_samples)):
                    if self.abort:
                        return

                    # Wait till there is space in buffer
                    # TODO: Make this more sophisticated -> If buffer is empty and message does not fit, split modulation of message
                    time.sleep(self.WAIT_TIMEOUT)
                self.ring_buffer.push(modulator.modulated_samples)
                pos += len(modulator.modulated_samples)
