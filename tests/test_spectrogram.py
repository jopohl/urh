from PyQt5.QtCore import QTimer

from tests.QtTestCase import QtTestCase
from urh import colormaps
from urh.signalprocessing.Signal import Signal
from urh.signalprocessing.Spectrogram import Spectrogram


class TestSpectrogram(QtTestCase):
    def setUp(self):
        self.signal = Signal(self.get_path_for_filename("two_participants.complex"), "test")
        self.spectrogram = Spectrogram(self.signal.data)

    def test_create_spectrogram_image(self):
        image = self.spectrogram.create_spectrogram_image()
        self.assertEqual(image.width(), self.spectrogram.time_bins - 2)
        self.assertEqual(image.height(), self.spectrogram.freq_bins)

    def test_create_colormap_image(self):
        image = self.spectrogram.create_colormap_image("magma", height=42)
        self.assertEqual(image.height(), 42)
        self.assertEqual(image.width(), len(colormaps.chosen_colormap_numpy_bgra))

    def test_channel_separation_with_negative_frequency(self):
        super().setUp()
        self.add_signal_to_form("three_channels.complex")
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)

        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        self.__prepare_channel_separation(signal_frame)

        self.__test_extract_channel(signal_frame, freq1=650, freq2=850, bandwidth="195,312kHz", target_bits="11001101")
        self.__test_extract_channel(signal_frame, freq1=500, freq2=620, bandwidth="117,188kHz", target_bits="10101001")
        self.__test_extract_channel(signal_frame, freq1=217, freq2=324, bandwidth="104,492kHz", target_bits="10010111")

    def test_cancel_filtering(self):
        super().setUp()
        self.add_signal_to_form("two_participants.complex")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.cbSignalView.setCurrentIndex(2)
        signal_frame.ui.spinBoxSelectionStart.setValue(100)
        signal_frame.ui.spinBoxSelectionEnd.setValue(200)
        menu = signal_frame.ui.gvSpectrogram.create_context_menu()
        create_action = next(action for action in menu.actions() if "bandpass filter" in action.text())
        timer = QTimer(self.form)
        timer.setSingleShot(True)
        timer.timeout.connect(self.form.cancel_action.trigger)
        timer.start(1)

        create_action.trigger()

        self.assertTrue(signal_frame.filter_abort_wanted)
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)

    def __prepare_channel_separation(self, signal_frame):
        self.assertEqual(self.form.signal_tab_controller.num_frames, 1)
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.spinBoxNoiseTreshold.setValue(0)
        signal_frame.ui.spinBoxNoiseTreshold.editingFinished.emit()
        self.assertEqual(signal_frame.signal.num_samples, 800)
        signal_frame.ui.cbSignalView.setCurrentIndex(2)
        self.assertTrue(signal_frame.spectrogram_is_active)

    def __test_extract_channel(self, signal_frame, freq1, freq2, bandwidth: str, target_bits: str, center=None):
        num_frames = self.form.signal_tab_controller.num_frames

        signal_frame.ui.spinBoxSelectionStart.setValue(freq1)
        signal_frame.ui.spinBoxSelectionEnd.setValue(freq2 - 1)
        signal_frame.ui.spinBoxSelectionEnd.setValue(freq2)

        self.assertEqual(signal_frame.ui.lNumSelectedSamples.text(), str(freq2 - freq1))
        self.assertEqual(signal_frame.ui.lDuration.text().replace(".", ","), bandwidth)
        menu = signal_frame.ui.gvSpectrogram.create_context_menu()
        create_action = next(action for action in menu.actions() if "bandpass filter" in action.text())
        create_action.trigger()

        self.assertEqual(self.form.signal_tab_controller.num_frames, num_frames + 1)
        filtered_frame = self.form.signal_tab_controller.signal_frames[1]
        filtered_frame.ui.cbModulationType.setCurrentText("ASK")
        filtered_frame.ui.spinBoxInfoLen.setValue(100)
        filtered_frame.ui.spinBoxInfoLen.editingFinished.emit()
        if center is not None:
            filtered_frame.ui.spinBoxCenterOffset.setValue(center)
            filtered_frame.ui.spinBoxCenterOffset.editingFinished.emit()

        self.assertEqual(len(filtered_frame.proto_analyzer.plain_bits_str), 1)
        self.assertEqual(filtered_frame.proto_analyzer.plain_bits_str[0], target_bits)
