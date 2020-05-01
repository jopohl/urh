import os
import tempfile

from PyQt5.QtCore import QPoint, QTimer
from PyQt5.QtWidgets import qApp, QInputDialog, QMessageBox

from tests.QtTestCase import QtTestCase
from urh import settings
from urh.controller.dialogs.DecoderDialog import DecoderDialog
from urh.signalprocessing.Encoding import Encoding


class TestDecodingGUI(QtTestCase):
    def setUp(self):
        super().setUp()
        self.add_signal_to_form("esaver.complex16s")

        # add empty signal
        path = os.path.join(tempfile.gettempdir(), "empty.complex")
        open(path, "w").close()
        self.form.add_signalfile(path)

        signal = self.form.signal_tab_controller.signal_frames[0].signal
        empty_signal = self.form.signal_tab_controller.signal_frames[1].signal
        self.dialog = DecoderDialog(decodings=self.form.compare_frame_controller.decodings,
                                    signals=[signal, empty_signal], parent=self.form,
                                    project_manager=self.form.project_manager)

        if self.SHOW:
            self.dialog.show()

    def test_edit_decoding(self):
        self.dialog.ui.combobox_decodings.setCurrentIndex(1)  # NRZI
        self.assertEqual(self.dialog.ui.decoderchain.count(), 1)  # One Invert
        self.dialog.save_to_file()

    def test_build_decoding(self):
        self.dialog.ui.combobox_decodings.setCurrentIndex(4)
        chain = [(settings.DECODING_INVERT,),
                 (settings.DECODING_ENOCEAN,),
                 (settings.DECODING_DIFFERENTIAL,),
                 (settings.DECODING_CARRIER,),
                 (settings.DECODING_BITORDER,),
                 (settings.DECODING_EDGE,),
                 (settings.DECODING_INVERT,),
                 (settings.DECODING_DATAWHITENING,),
                 (settings.DECODING_REDUNDANCY, "2"),
                 (settings.DECODING_MORSE, "1;3;1"),
                 (settings.DECODING_SUBSTITUTION, "0:1;1:0;"),
                 (settings.DECODING_EXTERNAL, "./;./"),
                 (settings.DECODING_CUT, "0;1010")]

        decoding = Encoding(chain=[c for chain_item in chain for c in chain_item])
        self.dialog.decodings[4] = decoding
        self.dialog.set_e()

        self.assertEqual(len(chain), self.dialog.ui.decoderchain.count())

        for i in range(0, self.dialog.ui.decoderchain.count()):
            self.dialog.ui.decoderchain.setCurrentRow(i)
            self.dialog.set_information(2)
            self.assertIn(chain[i][0], self.dialog.ui.info.text())

    def test_set_signal(self):
        self.dialog.ui.combobox_signals.setCurrentText("esaver")
        bits = "".join(self.form.signal_tab_controller.signal_frames[0].proto_analyzer.plain_bits_str)
        self.assertEqual(self.dialog.ui.inpt.text(), bits)

        self.dialog.ui.combobox_signals.setCurrentIndex(0)
        self.assertEqual(self.dialog.ui.inpt.text(), "10010110")

    def test_set_signal_empty_message(self):
        self.dialog.ui.combobox_signals.setCurrentText("empty")
        self.assertEqual(self.dialog.ui.inpt.text(), "")

    def test_select_items(self):
        for i in range(0, self.dialog.ui.basefunctions.count()):
            self.dialog.ui.basefunctions.setCurrentRow(i)
            self.assertIn(self.dialog.ui.basefunctions.currentItem().text(), self.dialog.ui.info.text())

        for i in range(0, self.dialog.ui.additionalfunctions.count()):
            self.dialog.ui.additionalfunctions.setCurrentRow(i)
            self.assertIn(self.dialog.ui.additionalfunctions.currentItem().text(), self.dialog.ui.info.text())

    def test_context_menu(self):
        self.dialog.ui.combobox_decodings.setCurrentIndex(4)
        decoding = Encoding(chain=[settings.DECODING_INVERT])
        self.dialog.decodings[4] = decoding
        self.dialog.set_e()

        self.assertEqual(1, self.dialog.ui.decoderchain.count())

        self.dialog.ui.decoderchain.context_menu_pos = QPoint(0, 0)
        menu = self.dialog.ui.decoderchain.create_context_menu()
        menu_actions = [action.text() for action in menu.actions() if action.text()]
        self.assertEqual(3, len(menu_actions))

    def test_disable_enable_decoding_item(self):
        self.dialog.ui.decoderchain.addItem(settings.DECODING_INVERT)
        self.dialog.decoderchainUpdate()

        self.assertEqual(self.dialog.ui.decoderchain.count(), 1)

        self.dialog.ui.decoderchain.context_menu_pos = QPoint(0, 0)
        self.dialog.ui.decoderchain.on_disable_function_triggered()
        self.assertIn(settings.DECODING_DISABLED_PREFIX, self.dialog.ui.decoderchain.item(0).text())
        self.dialog.ui.decoderchain.on_disable_function_triggered()
        self.assertNotIn(self.dialog.ui.decoderchain.item(0).text(), settings.DECODING_DISABLED_PREFIX)

    def test_save_remove_decoding(self):
        def set_save_name():
            timer.stop()
            input_dialog = next(w for w in qApp.topLevelWidgets() if isinstance(w, QInputDialog))
            input_dialog.setTextValue("Test decoding")
            input_dialog.accept()

        def accept_delete():
            timer.stop()
            message_box = next(w for w in qApp.topLevelWidgets() if isinstance(w, QMessageBox))
            message_box.button(QMessageBox.Yes).click()

        self.dialog.ui.decoderchain.addItem(settings.DECODING_CUT)
        self.dialog.decoderchainUpdate()

        self.assertEqual(self.dialog.ui.decoderchain.count(), 1)

        timer = QTimer(self.dialog)
        timer.setSingleShot(True)
        timer.timeout.connect(set_save_name)
        timer.start(10)
        self.dialog.ui.saveas.click()

        self.assertEqual(self.dialog.ui.combobox_decodings.currentText(), "Test decoding")

        timer.timeout.disconnect(set_save_name)
        timer.timeout.connect(accept_delete)
        timer.start(10)

        self.dialog.ui.delete_decoding.click()

        self.assertNotEqual(self.dialog.ui.combobox_decodings.currentText(), "Test decoding")
