from tests.QtTestCase import QtTestCase
from urh.signalprocessing.Signal import Signal
from urh.signalprocessing.Spectrogram import Spectrogram


class TestSpectrogram(QtTestCase):
    def setUp(self):
        self.signal = Signal(self.get_path_for_filename("two_participants.complex"), "test")
        self.spectrogram = Spectrogram(self.signal.data, sample_rate=2e6)

    def test_colormap(self):
        bgra_values = self.spectrogram.apply_bgra_lookup(self.spectrogram.data)
        self.assertEqual(bgra_values.shape, (self.spectrogram.freq_bins, self.spectrogram.time_bins, 4))

    def test_create_spectrogram_image(self):
        image = self.spectrogram.create_spectrogram_image()
        self.assertEqual(image.width(), self.spectrogram.time_bins)
        self.assertEqual(image.height(), self.spectrogram.freq_bins)
