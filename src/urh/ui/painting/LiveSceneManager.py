from urh.signalprocessing.IQArray import IQArray
from urh.ui.painting.SceneManager import SceneManager


class LiveSceneManager(SceneManager):
    def __init__(self, data_array, parent):
        super().__init__(parent)
        self.plot_data = data_array
        self.end = 0

    @property
    def num_samples(self):
        return self.end
