import os
import shutil
import tarfile
import tempfile
import wave
import zipfile

import numpy as np
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from urh.util.Errors import Errors

VIEW_TYPES = ["Bits", "Hex", "ASCII"]

archives = {}
""":type: dict of [str, str]
   :param: archives[extracted_filename] = filename"""

RECENT_PATH = QDir.homePath()


def uncompress_archives(file_names, temp_dir):
    """
    Extract each archive from the list of filenames.
    Normal files stay untouched.
    Add all files to the Recent Files.
    :type file_names: list of str
    :type temp_dir: str
    :rtype: list of str
    """
    result = []
    for filename in file_names:
        if filename.endswith(".tar") or filename.endswith(".tar.gz") or filename.endswith(".tar.bz2"):
            obj = tarfile.open(filename, "r")
            extracted_file_names = []
            for j, member in enumerate(obj.getmembers()):
                obj.extract(member, temp_dir)
                extracted_filename = os.path.join(temp_dir, obj.getnames()[j])
                extracted_file_names.append(extracted_filename)
                archives[extracted_filename] = filename
            result.extend(extracted_file_names[:])
        elif filename.endswith(".zip"):
            obj = zipfile.ZipFile(filename)
            extracted_file_names = []
            for j, info in enumerate(obj.infolist()):
                obj.extract(info, path=temp_dir)
                extracted_filename = os.path.join(temp_dir, obj.namelist()[j])
                extracted_file_names.append(extracted_filename)
                archives[extracted_filename] = filename
            result.extend(extracted_file_names[:])
        else:
            result.append(filename)

    return result


def get_save_file_name(initial_name: str, wav_only=False, caption="Save signal"):
    global RECENT_PATH
    if caption == "Save signal":
        name_filter = "Complex files (*.complex);;Complex16 files (2 unsigned int8) " \
                 "(*.complex16u);;Complex16 files (2 signed int8) (*.complex16s);;" \
                 "Compressed complex files (*.coco);;wav files (*.wav);;all files (*)"
        if wav_only:
            name_filter = "wav files (*.wav);;all files (*)"
    elif caption == "Save fuzz profile":
        name_filter = "Fuzzfiles (*.fuzz.xml *.fuzz);;All files (*)"
    elif caption == "Save encoding":
        name_filter = ""
    else:
        name_filter = "Protocols (*.proto.xml *.proto);;All files (*)"

    filename = None
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.AnyFile)
    dialog.setNameFilter(name_filter)
    dialog.setViewMode(QFileDialog.Detail)
    dialog.setDirectory(RECENT_PATH)
    dialog.setLabelText(QFileDialog.Accept, "Save")
    dialog.setWindowTitle(caption)
    dialog.setAcceptMode(QFileDialog.AcceptSave)
    dialog.selectFile(initial_name)

    if dialog.exec():
        filename = dialog.selectedFiles()[0]

    if filename:
        RECENT_PATH = os.path.split(filename)[0]

    return filename


def save_data_dialog(signal_name: str, data, wav_only=False, parent=None) -> str:
    filename = get_save_file_name(signal_name, wav_only)

    if filename:
        try:
            save_data(data, filename)
        except Exception as e:
            QMessageBox.critical(parent, "Error saving signal", e.args[0])
            filename = None
    else:
        filename = None

    return filename


def save_data(data, filename: str, sample_rate=1e6):
    if filename.endswith(".wav"):
        f = wave.open(filename, "w")
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(data)
        f.close()
    elif filename.endswith(".coco"):
        with tarfile.open(filename, 'w:bz2') as tar_write:
            tmp_name = os.path.join(QDir.tempPath(), "tmpfile")
            data.tofile(tmp_name)
            tar_write.add(tmp_name)
        os.remove(tmp_name)
    else:
        try:
            data.tofile(filename)
        except Exception as e:
            Errors.write_error(e)

    if filename in archives.keys():
        archive = archives[filename]
        if archive.endswith("zip"):
            rewrite_zip(archive)
        elif archive.endswith("tar") or archive.endswith("bz2") or archive.endswith("gz"):
            rewrite_tar(archive)


def save_signal(signal):
    filename = signal.filename
    if filename.endswith(".wav"):
        data = signal.wave_data
    elif filename.endswith(".complex16u"):
        data = (127.5 * (signal.data.view(np.float32) + 1.0)).astype(np.uint8)
    elif filename.endswith(".complex16s"):
        data = (127.5 * ((signal.data.view(np.float32)) - 0.5 / 127.5)).astype(np.int8)
    else:
        data = signal.data

    save_data(data, filename, sample_rate=signal.sample_rate)


def rewrite_zip(zip_name):
    tempdir = tempfile.mkdtemp()
    try:
        temp_name = os.path.join(tempdir, 'new.zip')
        files_in_archive = [f for f in archives.keys() if archives[f] == zip_name]
        with zipfile.ZipFile(temp_name, 'w') as zip_write:
            for filename in files_in_archive:
                zip_write.write(filename)
        shutil.move(temp_name, zip_name)
    finally:
        shutil.rmtree(tempdir)


def rewrite_tar(tar_name: str):
    tempdir = tempfile.mkdtemp()
    compression = ""
    if tar_name.endswith("gz"):
        compression = "gz"
    elif tar_name.endswith("bz2"):
        compression = "bz2"
    try:
        ext = "" if len(compression) == 0 else "." + compression
        temp_name = os.path.join(tempdir, 'new.tar' + ext)
        files_in_archive = [f for f in archives.keys() if archives[f] == tar_name]
        with tarfile.open(temp_name, 'w:' + compression) as tar_write:
            for file in files_in_archive:
                tar_write.add(file)
        shutil.move(temp_name, tar_name)
    finally:
        shutil.rmtree(tempdir)


def get_directory():
    directory = QFileDialog.getExistingDirectory(None, "Choose Directory", QDir.homePath(),
                                                 QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    return directory
