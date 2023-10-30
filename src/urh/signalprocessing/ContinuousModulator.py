import time
from multiprocessing import Process, Value

from urh import settings
from urh.signalprocessing.Modulator import Modulator
from urh.util.Logger import logger
from urh.util.RingBuffer import RingBuffer


class ContinuousModulator(object):
    """
    This class is used in continuous sending mode.
    You pass a list of messages and modulators to it, and it takes care of modulating the messages sequentially.
    This avoids running out of RAM for large amounts of messages.
    """

    WAIT_TIMEOUT = 0.1

    def __init__(self, messages, modulators, num_repeats=-1):
        """

        :type messages: list of Message
        :type modulators: list of Modulator
        """
        self.messages = messages
        self.modulators = modulators
        self.num_repeats = num_repeats  # -1 or 0 = infinite

        self.ring_buffer = RingBuffer(
            int(settings.CONTINUOUS_BUFFER_SIZE_MB * 1e6) // 8,
            dtype=Modulator.get_dtype(),
        )

        self.current_message_index = Value("L", 0)

        self.abort = Value("i", 0)
        self.process = Process(
            target=self.modulate_continuously, args=(self.num_repeats,), daemon=True
        )

    @property
    def is_running(self):
        return self.process.is_alive()

    def start(self):
        self.abort.value = 0
        try:
            self.process = Process(
                target=self.modulate_continuously, args=(self.num_repeats,), daemon=True
            )
            self.process.start()
        except RuntimeError as e:
            logger.exception(e)

    def stop(self, clear_buffer=True):
        self.abort.value = 1

        if self.process.is_alive():
            try:
                self.process.join(1.5)
            except RuntimeError as e:
                logger.exception(e)
                self.process.terminate()

        if clear_buffer:
            self.ring_buffer.clear()

        logger.debug("Stopped continuous modulation")

    def modulate_continuously(self, num_repeats):
        rng = (
            iter(int, 1) if num_repeats <= 0 else range(0, num_repeats)
        )  # <= 0 = forever
        for _ in rng:
            if self.abort.value:
                return

            start = self.current_message_index.value

            for i in range(start, len(self.messages)):
                if self.abort.value:
                    return

                message = self.messages[i]
                self.current_message_index.value = i
                modulator = self.modulators[message.modulator_index]  # type: Modulator
                modulated = modulator.modulate(
                    start=0, data=message.encoded_bits, pause=message.pause
                )
                while not self.ring_buffer.will_fit(len(modulated)):
                    if self.abort.value:
                        return

                    # Wait till there is space in buffer
                    time.sleep(self.WAIT_TIMEOUT)

                self.ring_buffer.push(modulated)

            self.current_message_index.value = 0
