from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage, QPixmap

from urh.ui.painting.ZoomableScene import ZoomableScene


class SpectrogramScene(ZoomableScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spectrogram_image = self.addPixmap(QPixmap())

    def set_spectrogram_image(self, image: QImage):
        self.spectrogram_image.setPixmap(QPixmap.fromImage(image))
        self.setSceneRect(QRectF(image.rect()))

    def clear(self):
        self.spectrogram_image = None
        super().clear()
