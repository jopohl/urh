import os
import tempfile

from tests.QtTestCase import QtTestCase
from urh import settings
from urh.controller.MainController import MainController
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer


class TestFuzzingProfile(QtTestCase):
    def test_load_profile(self):
        filename = os.path.join(tempfile.gettempdir(), "test.fuzz.xml")
        mod = Modulator("mod 2")
        mod.parameters[1] = 42

        decoders = [Encoding(["NRZ"]), Encoding(["NRZ-I", settings.DECODING_INVERT])]

        pac = ProtocolAnalyzerContainer()
        pac.messages.append(
            Message(
                [True, False, False, True],
                100,
                decoder=decoders[0],
                message_type=pac.default_message_type,
            )
        )
        pac.messages.append(
            Message(
                [False, False, False, False],
                200,
                decoder=decoders[1],
                message_type=pac.default_message_type,
            )
        )
        pac.create_fuzzing_label(1, 10, 0)
        assert isinstance(self.form, MainController)
        pac.to_xml_file(
            filename,
            decoders=decoders,
            participants=self.form.project_manager.participants,
        )

        self.form.add_files([os.path.join(tempfile.gettempdir(), "test.fuzz.xml")])

        self.assertEqual(
            self.form.ui.tabWidget.currentWidget(), self.form.ui.tab_generator
        )

        pac = self.form.generator_tab_controller.table_model.protocol

        self.assertEqual(len(pac.messages), 2)
        self.assertEqual(pac.messages[1][0], False)
        self.assertEqual(len(pac.protocol_labels), 1)
