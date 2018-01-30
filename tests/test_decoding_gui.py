import tempfile

import os
from PyQt5.QtCore import QPoint

from tests.QtTestCase import QtTestCase
from urh import constants
from urh.controller.dialogs.DecoderDialog import DecoderDialog
from urh.signalprocessing.Encoding import Encoding

class TestDecodingGUI(QtTestCase):
    def setUp(self):
        super().setUp()
        self.add_signal_to_form("esaver.complex")

        # add empty signal
        path = os.path.join(tempfile.gettempdir(), "empty.complex")
        open(path, "w").close()
        self.wait_before_new_file()
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
        chain = [(constants.DECODING_INVERT,),
                 (constants.DECODING_ENOCEAN,),
                 (constants.DECODING_DIFFERENTIAL,),
                 (constants.DECODING_CARRIER,),
                 (constants.DECODING_BITORDER,),
                 (constants.DECODING_EDGE,),
                 (constants.DECODING_DATAWHITENING,),
                 (constants.DECODING_REDUNDANCY, "2"),
                 (constants.DECODING_MORSE, "1;3;1"),
                 (constants.DECODING_SUBSTITUTION, "0:1;1:0;"),
                 (constants.DECODING_EXTERNAL, "./;./"),
                 (constants.DECODING_CUT, "0;1010")]

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
        decoding = Encoding(chain=[constants.DECODING_INVERT])
        self.dialog.decodings[4] = decoding
        self.dialog.set_e()

        self.assertEqual(1, self.dialog.ui.decoderchain.count())

        self.dialog.ui.decoderchain.context_menu_pos = QPoint(0, 0)
        menu = self.dialog.ui.decoderchain.create_context_menu()
        menu_actions = [action.text() for action in menu.actions() if action.text()]
        self.assertEqual(3, len(menu_actions))
