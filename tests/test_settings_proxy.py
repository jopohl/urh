from tests.QtTestCase import QtTestCase
from urh import constants
from urh.util.SettingsProxy import SettingsProxy


class TestSettingsProxy(QtTestCase):
    def test_get_receive_buffer_size(self):
        SettingsProxy.OVERWRITE_RECEIVE_BUFFER_SIZE = None
        ns = SettingsProxy.get_receive_buffer_size(resume_on_full_receive_buffer=True, spectrum_mode=True)
        self.assertEqual(ns, constants.SPECTRUM_BUFFER_SIZE)

        ns = SettingsProxy.get_receive_buffer_size(resume_on_full_receive_buffer=True, spectrum_mode=False)
        self.assertEqual(ns, constants.SNIFF_BUFFER_SIZE)

        ns1 = SettingsProxy.get_receive_buffer_size(resume_on_full_receive_buffer=False, spectrum_mode=True)
        ns2 = SettingsProxy.get_receive_buffer_size(resume_on_full_receive_buffer=False, spectrum_mode=False)
        self.assertEqual(len(str(ns1)), len(str(ns2)))
