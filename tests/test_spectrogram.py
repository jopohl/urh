from tests.QtTestCase import QtTestCase
from urh import colormaps
from urh.signalprocessing.Signal import Signal
from urh.signalprocessing.Spectrogram import Spectrogram


class TestSpectrogram(QtTestCase):
    def setUp(self):
        self.signal = Signal(self.get_path_for_filename("two_participants.complex"), "test")
        self.spectrogram = Spectrogram(self.signal.data, sample_rate=2e6)

    def test_colormap(self):
        bgra_values = self.spectrogram.apply_bgra_lookup(self.spectrogram.data, colormaps.chosen_colormap_numpy_bgra,
                                                         self.spectrogram.data_min, self.spectrogram.data_max)
        self.assertEqual(bgra_values.shape, (self.spectrogram.freq_bins, self.spectrogram.time_bins, 4))

    def test_create_spectrogram_image(self):
        image = self.spectrogram.create_spectrogram_image()
        self.assertEqual(image.width(), self.spectrogram.time_bins)
        self.assertEqual(image.height(), self.spectrogram.freq_bins)

    def test_create_colormap_image(self):
        image = self.spectrogram.create_colormap_image("magma", height=42)
        self.assertEqual(image.height(), 42)
        self.assertEqual(image.width(), len(colormaps.chosen_colormap_numpy_bgra))
