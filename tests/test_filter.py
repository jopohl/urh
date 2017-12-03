import unittest

import numpy as np
import time

from tests.QtTestCase import QtTestCase
from urh.signalprocessing.Filter import Filter


class TestFilter(QtTestCase):
    def setUp(self):
        super().setUp()

        self.add_signal_to_form("unaveraged.complex")
        self.sig_frame = self.form.signal_tab_controller.signal_frames[0]

    def test_fir_filter(self):
        input_signal = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 42], dtype=np.complex64)
        filter_taps = [0.25, 0.25, 0.25, 0.25]

        fir_filter = Filter(filter_taps)

        filtered_signal = fir_filter.apply_fir_filter(input_signal)
        expected_filtered_signal = np.array([0.25, 0.75, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 16.5], dtype=np.complex64)

        self.assertTrue(np.array_equal(filtered_signal, expected_filtered_signal))

    def test_filter_full_signal(self):
        expected = "5555599595999995cccaccd"
        bit_len = 1000
        center = 0

        self.sig_frame.ui.btnFilter.click()
        self.sig_frame.ui.spinBoxInfoLen.setValue(bit_len)
        self.sig_frame.ui.spinBoxInfoLen.editingFinished.emit()
        self.sig_frame.ui.spinBoxCenterOffset.setValue(center)
        self.sig_frame.ui.spinBoxCenterOffset.editingFinished.emit()

        self.assertTrue(self.sig_frame.proto_analyzer.plain_hex_str[0].startswith(expected),
                        msg=self.sig_frame.proto_analyzer.plain_hex_str[0])

    def test_filter_selection(self):
        self.sig_frame.apply_filter_to_selection_only.trigger()
        self.assertTrue(self.sig_frame.apply_filter_to_selection_only.isChecked())

        selection_start, selection_end = 100, 200

        self.sig_frame.ui.spinBoxSelectionStart.setValue(selection_start)
        self.sig_frame.ui.spinBoxSelectionStart.editingFinished.emit()
        self.sig_frame.ui.spinBoxSelectionEnd.setValue(selection_end)
        self.sig_frame.ui.spinBoxSelectionEnd.editingFinished.emit()

        old_signal = self.sig_frame.signal._fulldata.copy()

        self.assertFalse(self.sig_frame.undo_stack.canUndo())
        self.sig_frame.ui.btnFilter.click()
        self.assertTrue(self.sig_frame.undo_stack.canUndo())

        filtered_signal = self.sig_frame.signal._fulldata
        self.assertEqual(len(old_signal), len(filtered_signal))

        for i, (old_sample, filtered_sample) in enumerate(zip(old_signal, filtered_signal)):
            if i in range(selection_start, selection_end):
                self.assertNotEqual(old_sample, filtered_sample, msg=str(i))
            else:
                self.assertEqual(old_sample, filtered_sample, msg=str(i))

        self.sig_frame.undo_stack.command(0).undo()
        self.assertTrue(np.array_equal(old_signal, self.sig_frame.signal.data))

        self.sig_frame.undo_stack.command(0).redo()
        self.assertTrue(np.array_equal(filtered_signal, self.sig_frame.signal.data))

    def test_filter_caption(self):
        self.assertIn("moving average", self.sig_frame.ui.btnFilter.text())

        self.assertFalse(self.sig_frame.filter_dialog.ui.lineEditCustomTaps.isEnabled())
        self.assertFalse(self.sig_frame.filter_dialog.ui.radioButtonCustomTaps.isChecked())
        self.sig_frame.filter_dialog.ui.radioButtonCustomTaps.click()
        self.assertTrue(self.sig_frame.filter_dialog.ui.lineEditCustomTaps.isEnabled())
        self.sig_frame.filter_dialog.ui.buttonBox.accepted.emit()

        self.assertIn("custom", self.sig_frame.ui.btnFilter.text())

    def test_fft_convolution(self):
        x = np.array([1, 2, 3])
        h = np.array([0, 1, 0.5])
        expected_result = np.array([1., 2.5, 4.])
        result_np = np.convolve(x, h, 'same')
        self.assertTrue(np.array_equal(result_np, expected_result))

        result_fft = Filter.fft_convolve_1d(x, h)
        self.assertTrue(np.array_equal(result_fft, expected_result))

        x = np.linspace(0, 1, num=10 ** 3).astype(np.complex64)
        h = Filter.design_windowed_sinc_bandpass(0.1, 0.4, 0.01)
        # fft convolve is faster if IR is round about 400 samples or windowed sinc has bandwidth of 0.01
        #print(len(h))

        t_np = time.time()
        result_np = np.convolve(x, h, mode="same")
        t_np = time.time() - t_np

        t_fft = time.time()
        result_fft = Filter.fft_convolve_1d(x, h)
        t_fft = time.time() - t_fft

        np.testing.assert_array_almost_equal(result_np, result_fft)
        #print("fft convolve time", t_fft, "np convolve time", t_np)

    def test_bandpass_filter(self):
        # GUI tests for bandpass filter are in test_spectrogram.py
        sig1 = np.sin(2 * np.pi * 0.2 * np.arange(0, 100))
        sig2 = np.sin(2 * np.pi * 0.3 * np.arange(0, 100))
        sig = sig1 + sig2

        filtered1 = Filter.apply_bandpass_filter(sig, 0.1, 0.2)
        filtered2 = Filter.apply_bandpass_filter(sig, 0.2, 0.1)
        self.assertTrue(np.array_equal(filtered1, filtered2))

if __name__ == '__main__':
    unittest.main()
