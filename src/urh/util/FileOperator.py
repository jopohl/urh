import os
import shutil
import tarfile
import tempfile
import zipfile

import numpy as np
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from urh.models.FileIconProvider import FileIconProvider
from urh.signalprocessing.IQArray import IQArray

VIEW_TYPES = ["Bits", "Hex", "ASCII"]

archives = {}
""":type: dict of [str, str]
   :param: archives[extracted_filename] = filename"""

RECENT_PATH = QDir.homePath()

EXT = {np.int8: ".complex16s", np.uint8: ".complex16u", np.int16: ".complex32s", np.uint16: ".complex32u",
       np.float32: ".complex", np.complex64: ".complex"}
FILTER = {np.int8: "Complex16 signed (*.complex16s *.cs8)", np.uint8: "Complex16 unsigned (*.complex16u *.cu8)",
          np.uint16: "Complex32 unsigned (*.complex32u *.cu16)", np.int16: "Complex32 signed (*.complex32s *.cs16)",
          np.float32: "Complex (*.complex)", np.complex64: "Complex (*.complex)"}


def get_open_dialog(directory_mode=False, parent=None, name_filter="full") -> QFileDialog:
    fip = FileIconProvider()
    dialog = QFileDialog(parent=parent, directory=RECENT_PATH)
    dialog.setIconProvider(fip)

    if directory_mode:
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setWindowTitle("Open Folder")
    else:
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setWindowTitle("Open Files")
        if name_filter == "full":
            name_filter = "All Files (*);;" \
                          "Complex (*.complex);;" \
                          "Complex16 unsigned (*.complex16u *.cu8);;" \
                          "Complex16 signed (*.complex16s *.cs8);;" \
                          "Complex32 unsigned (*.complex32u *.cu16);;" \
                          "Complex32 signed (*.complex32s *.cs16);;" \
                          "WAV (*.wav);;" \
                          "Protocols (*.proto.xml *.proto);;" \
                          "Binary Protocols (*.bin);;" \
                          "Fuzzing Profiles (*.fuzz.xml *.fuzz);;" \
                          "Simulator (*.sim.xml *.sim)" \
                          "Plain Bits (*.txt);;" \
                          "Tar Archives (*.tar *.tar.gz *.tar.bz2);;" \
                          "Zip Archives (*.zip)"
        elif name_filter == "proto":
            name_filter = "Protocols (*.proto.xml *.proto);; Binary Protocols (*.bin)"
        elif name_filter == "fuzz":
            name_filter = "Fuzzprofiles (*.fuzz.xml *.fuzz)"
        elif name_filter == "simulator":
            name_filter = "Simulator (*.sim.xml *.sim)"

        dialog.setNameFilter(name_filter)

    dialog.setOptions(QFileDialog.DontResolveSymlinks)
    dialog.setViewMode(QFileDialog.Detail)

    return dialog


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


def get_save_file_name(initial_name: str, wav_only=False, caption="Save signal", selected_name_filter=None):
    global RECENT_PATH
    if caption == "Save signal":
        name_filter = "Complex (*.complex);;" \
                      "Complex16 unsigned (*.complex16u *.cu8);;" \
                      "Complex16 signed (*.complex16s *.cs8);;" \
                      "Complex32 unsigned (*.complex32u *.cu16);;" \
                      "Complex32 signed (*.complex32s *.cs16);;" \
                      "Complex compressed (*.coco);;" \
                      "WAV (*.wav);;" \
                      "All Files (*)"
        if wav_only:
            name_filter = "WAV (*.wav);;All Files (*)"
    elif caption == "Save fuzz profile":
        name_filter = "Fuzzing Profile (*.fuzz.xml *.fuzz);;All Files (*)"
    elif caption == "Save encoding":
        name_filter = ""
    elif caption == "Save simulator profile":
        name_filter = "Simulator (*.sim.xml *.sim);;All Files (*)"
    elif caption == "Export spectrogram":
        name_filter = "Frequency Time (*.ft);;Frequency Time Amplitude (*.fta)"
    else:
        name_filter = "Protocols (*.proto.xml *.proto);;Binary Protocol (*.bin);;All Files (*)"

    filename = None
    dialog = QFileDialog(directory=RECENT_PATH, caption=caption, filter=name_filter)
    dialog.setFileMode(QFileDialog.AnyFile)
    dialog.setViewMode(QFileDialog.Detail)
    dialog.setLabelText(QFileDialog.Accept, "Save")
    dialog.setAcceptMode(QFileDialog.AcceptSave)

    if selected_name_filter is not None:
        dialog.selectNameFilter(selected_name_filter)

    dialog.selectFile(initial_name)

    if dialog.exec():
        filename = dialog.selectedFiles()[0]

    if filename:
        RECENT_PATH = os.path.split(filename)[0]

    return filename


def save_data_dialog(signal_name: str, data, sample_rate=1e6, wav_only=False, parent=None) -> str:
    if wav_only:
        if not signal_name.endswith(".wav"):
            signal_name += ".wav"
        name_filter = "WAV (*.wav)"
    else:
        if not any(signal_name.endswith(e) for e in FILTER.values()):
            try:
                dtype = next(d for d in EXT.keys() if d == data.dtype)
                signal_name += EXT[dtype]
                name_filter = FILTER[dtype]
            except StopIteration:
                name_filter = None
        else:
            name_filter = None

    filename = get_save_file_name(signal_name, wav_only, selected_name_filter=name_filter)

    if filename:
        try:
            save_data(data, filename, sample_rate=sample_rate)
        except Exception as e:
            QMessageBox.critical(parent, "Error saving signal", e.args[0])
            filename = None
    else:
        filename = None

    return filename


def save_data(data, filename: str, sample_rate=1e6, num_channels=2):
    if not isinstance(data, IQArray):
        data = IQArray(data)

    if filename.endswith(".wav"):
        data.export_to_wav(filename, num_channels, sample_rate)
    elif filename.endswith(".coco"):
        data.save_compressed(filename)
    else:
        data.tofile(filename)

    if filename in archives.keys():
        archive = archives[filename]
        if archive.endswith("zip"):
            rewrite_zip(archive)
        elif archive.endswith("tar") or archive.endswith("bz2") or archive.endswith("gz"):
            rewrite_tar(archive)


def save_signal(signal):
    save_data(signal.iq_array.data, signal.filename, signal.sample_rate)


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
