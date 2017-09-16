import time

from multiprocessing import Process, Value

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

        self.current_message_index = Value("L", 0)

        self.abort = Value("i", 0)
        self.process = Process(target=self.modulate_continuously)
        self.process.daemon = True

    @property
    def is_running(self):
        return self.process.is_alive()

    def start(self):
        self.abort.value = 0
        try:
            self.process = Process(target=self.modulate_continuously)
            self.process.daemon = True
            self.process.start()
        except RuntimeError as e:
            logger.debug(str(e))

    def stop(self, clear_buffer=True):
        self.abort.value = 1
        if clear_buffer:
            self.ring_buffer.clear()
        if not self.process.is_alive():
            return

        try:
            self.process.join(0.1)
        except RuntimeError as e:
            logger.debug(str(e))

        if self.process.is_alive():
            self.process.terminate()
            self.process.join()

        logger.debug("Stopped continuous modulation")

    def modulate_continuously(self):
        while True:
            start = self.current_message_index.value
            for i in range(start, len(self.messages)):
                if self.abort.value:
                    return

                message = self.messages[i]
                self.current_message_index.value = i
                modulator = self.modulators[message.modulator_index]  # type: Modulator
                modulator.modulate(start=0, data=message.encoded_bits, pause=message.pause)
                while not self.ring_buffer.will_fit(len(modulator.modulated_samples)):
                    if self.abort.value:
                        return

                    # Wait till there is space in buffer
                    time.sleep(self.WAIT_TIMEOUT)
                self.ring_buffer.push(modulator.modulated_samples)
