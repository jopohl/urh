from urh import settings
from urh.ui.painting.VerticalSelection import VerticalSelection
from urh.ui.painting.ZoomableScene import ZoomableScene


class SpectrogramScene(ZoomableScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.removeItem(self.selection_area)

        self.selection_area = VerticalSelection(
            0, 0, 0, 0, fillcolor=settings.SELECTION_COLOR, opacity=0.6
        )
        self.selection_area.setZValue(1)
        self.addItem(self.selection_area)

    def width_spectrogram(self):
        return self.spectrogram_image.pixmap().width()
