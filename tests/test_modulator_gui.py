from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDropEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from urh.controller.dialogs.ModulatorDialog import ModulatorDialog
from urh.util.Logger import logger


class TestModulatorGUI(QtTestCase):
    def setUp(self):
        super().setUp()
        self.form.ui.tabWidget.setCurrentIndex(2)

        logger.debug("Preparing Modulation dialog")
        self.dialog, _ = self.form.generator_tab_controller.prepare_modulation_dialog()

        if self.SHOW:
            self.dialog.show()

        logger.debug("Initializing Modulation dialog")
        self.dialog.initialize("1111")
        logger.debug("Preparation success")

    def test_add_remove_modulator(self):
        self.assertEqual(len(self.dialog.modulators), 1)
        self.dialog.ui.btnAddModulation.click()
        self.assertEqual(len(self.dialog.modulators), 2)
        self.dialog.ui.btnAddModulation.click()
        self.assertEqual(len(self.dialog.modulators), 3)
        self.app.processEvents()
        self.dialog.ui.btnRemoveModulation.click()
        self.assertEqual(len(self.dialog.modulators), 2)
        self.dialog.ui.btnRemoveModulation.click()
        self.assertEqual(len(self.dialog.modulators), 1)
        self.assertFalse(self.dialog.ui.btnRemoveModulation.isEnabled())

    def test_edit_carrier(self):
        self.dialog.ui.doubleSpinBoxCarrierFreq.setValue(1e9)
        self.dialog.ui.doubleSpinBoxCarrierFreq.editingFinished.emit()
        self.assertEqual(self.dialog.current_modulator.carrier_freq_hz, 1e9)

        self.dialog.ui.doubleSpinBoxCarrierPhase.setValue(100)
        self.dialog.ui.doubleSpinBoxCarrierPhase.editingFinished.emit()
        self.assertEqual(self.dialog.current_modulator.carrier_phase_deg, 100)

    def test_edit_data(self):
        bits = self.dialog.current_modulator.display_bits
        self.dialog.ui.linEdDataBits.setText("10101010")
        self.dialog.ui.linEdDataBits.editingFinished.emit()
        self.assertEqual(self.dialog.current_modulator.display_bits, "10101010")

        assert isinstance(self.dialog, ModulatorDialog)

        self.dialog.restore_bits_action.trigger()
        self.dialog.ui.linEdDataBits.editingFinished.emit()
        self.assertEqual(self.dialog.current_modulator.display_bits, bits)

        self.dialog.ui.spinBoxSamplesPerSymbol.setValue(1337)
        self.dialog.ui.spinBoxSamplesPerSymbol.editingFinished.emit()
        self.assertEqual(self.dialog.current_modulator.samples_per_symbol, 1337)

        self.dialog.ui.spinBoxSampleRate.setValue(5e6)
        self.dialog.ui.spinBoxSampleRate.editingFinished.emit()
        self.assertEqual(self.dialog.current_modulator.sample_rate, 5e6)

    def test_zoom(self):
        self.dialog.ui.gVModulated.zoom(1.1)
        self.assertIn(
            int(self.dialog.ui.gVModulated.view_rect().width()),
            [
                int(self.dialog.ui.gVCarrier.view_rect().width()) - 1,
                int(self.dialog.ui.gVCarrier.view_rect().width()),
                int(self.dialog.ui.gVCarrier.view_rect().width() + 1),
            ],
        )

        self.assertIn(
            int(self.dialog.ui.gVModulated.view_rect().width()),
            [
                int(self.dialog.ui.gVData.view_rect().width()) - 1,
                int(self.dialog.ui.gVData.view_rect().width()),
                int(self.dialog.ui.gVData.view_rect().width() + 1),
            ],
        )

        self.dialog.ui.gVModulated.zoom(1.01)

        self.assertIn(
            int(self.dialog.ui.gVModulated.view_rect().width()),
            [
                int(self.dialog.ui.gVCarrier.view_rect().width()) - 1,
                int(self.dialog.ui.gVCarrier.view_rect().width()),
                int(self.dialog.ui.gVCarrier.view_rect().width() + 1),
            ],
        )

        self.assertIn(
            int(self.dialog.ui.gVModulated.view_rect().width()),
            [
                int(self.dialog.ui.gVData.view_rect().width()) - 1,
                int(self.dialog.ui.gVData.view_rect().width()),
                int(self.dialog.ui.gVData.view_rect().width() + 1),
            ],
        )

    def test_edit_modulation(self):
        self.dialog.ui.comboBoxModulationType.setCurrentText(
            "Amplitude Shift Keying (ASK)"
        )
        self.assertEqual(self.dialog.ui.labelParameters.text(), "Amplitudes in %:")

        self.dialog.ui.comboBoxModulationType.setCurrentText(
            "Frequency Shift Keying (FSK)"
        )
        self.assertEqual(self.dialog.ui.labelParameters.text(), "Frequencies in Hz:")

        self.dialog.ui.comboBoxModulationType.setCurrentText(
            "Gaussian Frequency Shift Keying (GFSK)"
        )
        self.assertEqual(self.dialog.ui.labelParameters.text(), "Frequencies in Hz:")
        self.dialog.ui.spinBoxGaussBT.setValue(0.5)
        self.dialog.ui.spinBoxGaussBT.editingFinished.emit()
        self.assertEqual(self.dialog.current_modulator.gauss_bt, 0.5)
        self.dialog.ui.spinBoxGaussFilterWidth.setValue(5)
        self.dialog.ui.spinBoxGaussFilterWidth.editingFinished.emit()
        self.assertEqual(self.dialog.current_modulator.gauss_filter_width, 5)

        self.dialog.ui.comboBoxModulationType.setCurrentText("Phase Shift Keying (PSK)")
        self.assertEqual(self.dialog.ui.labelParameters.text(), "Phases in degree:")

        self.dialog.ui.comboBoxModulationType.setCurrentText(
            "Amplitude Shift Keying (ASK)"
        )
        self.assertEqual(self.dialog.ui.labelParameters.text(), "Amplitudes in %:")

        self.assertEqual(
            int(self.dialog.ui.lSamplesInViewModulated.text()),
            int(self.dialog.ui.gVModulated.view_rect().width()),
        )

    def test_signal_view(self):
        self.add_signal_to_form("esaver.complex16s")
        signal = self.form.signal_tab_controller.signal_frames[0].signal

        tree_view = self.dialog.ui.treeViewSignals
        tree_model = tree_view.model()
        item = tree_model.rootItem.children[0].children[0]
        index = tree_model.createIndex(0, 0, item)
        rect = tree_view.visualRect(index)
        QTest.mousePress(tree_view.viewport(), Qt.LeftButton, pos=rect.center())
        mime_data = tree_model.mimeData([index])
        drag_drop = QDropEvent(
            rect.center(),
            Qt.CopyAction | Qt.MoveAction,
            mime_data,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        drag_drop.acceptProposedAction()
        self.dialog.ui.gVOriginalSignal.dropEvent(drag_drop)
        self.assertEqual(
            self.dialog.ui.gVOriginalSignal.sceneRect().width(), signal.num_samples
        )

        self.dialog.ui.cbShowDataBitsOnly.click()
        self.dialog.ui.chkBoxLockSIV.click()

        self.assertEqual(
            int(self.dialog.ui.gVOriginalSignal.view_rect().width()),
            int(self.dialog.ui.gVModulated.view_rect().width()),
        )

        freq = self.dialog.ui.doubleSpinBoxCarrierFreq.value()
        self.dialog.ui.btnAutoDetect.click()
        self.assertNotEqual(freq, self.dialog.ui.doubleSpinBoxCarrierFreq.value())

        self.dialog.ui.comboBoxModulationType.setCurrentText(
            "Frequency Shift Keying (FSK)"
        )
        self.dialog.ui.btnAutoDetect.click()

        self.assertEqual(self.dialog.ui.lCurrentSearchResult.text(), "1")
        self.dialog.ui.btnSearchNext.click()
        self.assertEqual(self.dialog.ui.lCurrentSearchResult.text(), "2")
        self.dialog.ui.btnSearchPrev.click()
        self.assertEqual(self.dialog.ui.lCurrentSearchResult.text(), "1")
