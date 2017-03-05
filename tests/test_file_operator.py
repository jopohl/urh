import hashlib
import unittest
import tempfile
import os
import tarfile
from zipfile import ZipFile

import numpy as np
from PyQt5.QtCore import QDir

import tests.utils_testing
from urh.controller.MainController import MainController

from urh.util import FileOperator

app = tests.utils_testing.app


class TestFileOperator(unittest.TestCase):
    def test_save_wav(self):
        temp_dir = tempfile.gettempdir()
        os.chdir(temp_dir)
        self.assertFalse(os.path.isfile("test.wav"))
        FileOperator.save_data(bytearray([1, 2]), "test.wav")
        self.assertTrue(os.path.isfile("test.wav"))
        os.remove("test.wav")

    def test_uncompress_archives(self):
        temp_dir = tempfile.gettempdir()
        os.chdir(temp_dir)

        with tarfile.open("test.tar.gz", "w:gz") as tar:
            for name in ["1.complex", "2.complex", "3.complex"]:
                data = np.ndarray(10, dtype=np.complex64)
                data.tofile(name)
                tar.add(name)

        with ZipFile('test.zip', 'w') as zip:
            for name in ["4.complex", "5.complex"]:
                data = np.ndarray(10, dtype=np.complex64)
                data.tofile(name)
                zip.write(name)

        form = MainController()
        form.add_files(FileOperator.uncompress_archives(["test.tar.gz", "test.zip"], QDir.tempPath()))
        self.assertEqual(len(form.signal_tab_controller.signal_frames), 5)

        tar_md5 = hashlib.md5(open(os.path.join(temp_dir, "test.tar.gz"), 'rb').read()).hexdigest()
        form.signal_tab_controller.signal_frames[0].signal._fulldata = np.ones(5, dtype=np.complex64)
        form.signal_tab_controller.signal_frames[0].signal.changed = True
        form.signal_tab_controller.signal_frames[0].ui.btnSaveSignal.click()

        tar_md5_after_save = hashlib.md5(open(os.path.join(temp_dir, "test.tar.gz"), 'rb').read()).hexdigest()
        self.assertNotEqual(tar_md5, tar_md5_after_save)

        zip_md5 = hashlib.md5(open(os.path.join(temp_dir, "test.zip"), 'rb').read()).hexdigest()
        form.signal_tab_controller.signal_frames[4].signal._fulldata = np.ones(5, dtype=np.complex64)
        form.signal_tab_controller.signal_frames[4].signal.changed = True
        form.signal_tab_controller.signal_frames[4].ui.btnSaveSignal.click()

        zip_md5_after_save = hashlib.md5(open(os.path.join(temp_dir, "test.zip"), 'rb').read()).hexdigest()
        self.assertNotEqual(zip_md5, zip_md5_after_save)
