from urh.signalprocessing.IQArray import IQArray
from urh.ui.painting.SceneManager import SceneManager
from urh.util.RingBuffer import RingBuffer


class ContinuousSceneManager(SceneManager):
    def __init__(self, ring_buffer: RingBuffer, parent):
        super().__init__(parent)
        self.ring_buffer = ring_buffer
        self.__start = 0
        self.__end = 0

    @property
    def plot_data(self):
        return self.ring_buffer.view_data.real

    @plot_data.setter
    def plot_data(self, value):
        pass

    @property
    def end(self):
        return self.ring_buffer.size

    @end.setter
    def end(self, value):
        pass
