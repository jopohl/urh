from tests.QtTestCase import QtTestCase
from urh import colormaps
from urh.signalprocessing.Signal import Signal
from urh.signalprocessing.Spectrogram import Spectrogram


class TestSpectrogram(QtTestCase):
    def setUp(self):
        self.signal = Signal(self.get_path_for_filename("two_participants.complex"), "test")
        self.spectrogram = Spectrogram(self.signal.data)

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


    def test_channel_separation(self):
        super().setUp()
        self.add_signal_to_form("two_channels.complex")
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        self.assertEqual(signal_frame.signal.num_samples, 800)
        signal_frame.ui.cbSignalView.setCurrentIndex(2)
        self.assertTrue(signal_frame.spectrogram_is_active)
        signal_frame.ui.spinBoxSelectionStart.setValue(650)
        signal_frame.ui.spinBoxSelectionEnd.setValue(849)
        signal_frame.ui.spinBoxSelectionEnd.setValue(850)

        self.assertEqual(signal_frame.ui.lNumSelectedSamples.text(), "200")
        self.assertEqual(signal_frame.ui.lDuration.text().replace(".", ","), "195,312kHz")
        menu = signal_frame.ui.gvSpectrogram.create_context_menu()
        create_action = next(action for action in menu.actions() if action.text().startswith("Create"))
        create_action.trigger()

        self.assertEqual(self.form.signal_tab_controller.num_frames, 2)
        filtered_frame1 = self.form.signal_tab_controller.signal_frames[1]
        filtered_frame1.ui.cbModulationType.setCurrentText("ASK")
        filtered_frame1.ui.spinBoxInfoLen.setValue(100)
        filtered_frame1.ui.spinBoxInfoLen.editingFinished.emit()

        self.assertEqual(len(filtered_frame1.proto_analyzer.plain_bits_str), 1)
        self.assertEqual(filtered_frame1.proto_analyzer.plain_bits_str[0], "11001101")

        signal_frame.ui.spinBoxSelectionStart.setValue(500)
        signal_frame.ui.spinBoxSelectionEnd.setValue(620)
        self.assertEqual(signal_frame.ui.lNumSelectedSamples.text(), "120")
        self.assertEqual(signal_frame.ui.lDuration.text().replace(".", ","), "117,188kHz")
        menu = signal_frame.ui.gvSpectrogram.create_context_menu()
        create_action = next(action for action in menu.actions() if action.text().startswith("Create"))
        create_action.trigger()

        self.assertEqual(self.form.signal_tab_controller.num_frames, 3)
        filtered_frame2 = self.form.signal_tab_controller.signal_frames[2]
        filtered_frame2.ui.cbModulationType.setCurrentText("ASK")
        filtered_frame2.ui.spinBoxInfoLen.setValue(100)
        filtered_frame2.ui.spinBoxInfoLen.editingFinished.emit()

        self.assertEqual(len(filtered_frame2.proto_analyzer.plain_bits_str), 1)
        self.assertEqual(filtered_frame2.proto_analyzer.plain_bits_str[0], "10101001")
