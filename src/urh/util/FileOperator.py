import os
import shutil
import tarfile
import tempfile
import zipfile

import numpy as np
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from urh.signalprocessing.IQArray import IQArray

archives = {}
""":type: dict of [str, str]
   :param: archives[extracted_filename] = filename"""

RECENT_PATH = QDir.homePath()

SIGNAL_FILE_EXTENSIONS_BY_TYPE = {
    np.int8: ".complex16s",
    np.uint8: ".complex16u",
    np.int16: ".complex32s",
    np.uint16: ".complex32u",
    np.float32: ".complex",
    np.complex64: ".complex"
}

SIGNAL_NAME_FILTERS_BY_TYPE = {
    np.int8: "Complex16 signed (*.complex16s *.cs8)",
    np.uint8: "Complex16 unsigned (*.complex16u *.cu8)",
    np.uint16: "Complex32 unsigned (*.complex32u *.cu16)",
    np.int16: "Complex32 signed (*.complex32s *.cs16)",
    np.float32: "Complex (*.complex)",
    np.complex64: "Complex (*.complex)"
}

EVERYTHING_FILE_FILTER = "All Files (*)"

SIGNAL_NAME_FILTERS = list(sorted(set(SIGNAL_NAME_FILTERS_BY_TYPE.values())))

COMPRESSED_COMPLEX_FILE_FILTER = "Compressed Complex File (*.coco)"
WAV_FILE_FILTER = "Waveform Audio File Format (*.wav *.wave)"
PROTOCOL_FILE_FILTER = "Protocol (*.proto.xml *.proto)"
BINARY_PROTOCOL_FILE_FILTER = "Binary Protocol (*.bin)"
PLAIN_BITS_FILE_FILTER = "Plain Bits (*.txt)"
FUZZING_FILE_FILTER = "Fuzzing Profile (*.fuzz.xml *.fuzz)"
SIMULATOR_FILE_FILTER = "Simulator Profile (*.sim.xml *.sim)"
TAR_FILE_FILTER = "Tar Archive (*.tar *.tar.gz *.tar.bz2)"
ZIP_FILE_FILTER = "Zip Archive (*.zip)"


def __get__name_filter_for_signals() -> str:
    return ";;".join([EVERYTHING_FILE_FILTER] + SIGNAL_NAME_FILTERS + [COMPRESSED_COMPLEX_FILE_FILTER, WAV_FILE_FILTER])


def get_open_dialog(directory_mode=False, parent=None, name_filter="full") -> QFileDialog:
    dialog = QFileDialog(parent=parent, directory=RECENT_PATH)

    if directory_mode:
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setWindowTitle("Open Folder")
    else:
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setWindowTitle("Open Files")
        if name_filter == "full":
            name_filter = __get__name_filter_for_signals() + ";;" \
                          + ";;".join([PROTOCOL_FILE_FILTER, BINARY_PROTOCOL_FILE_FILTER, PLAIN_BITS_FILE_FILTER,
                                       FUZZING_FILE_FILTER, SIMULATOR_FILE_FILTER, TAR_FILE_FILTER, ZIP_FILE_FILTER])
        elif name_filter == "signals_only":
            name_filter = __get__name_filter_for_signals()
        elif name_filter == "proto":
            name_filter = ";;".join([PROTOCOL_FILE_FILTER, BINARY_PROTOCOL_FILE_FILTER])
        elif name_filter == "fuzz":
            name_filter = FUZZING_FILE_FILTER
        elif name_filter == "simulator":
            name_filter = SIMULATOR_FILE_FILTER

        dialog.setNameFilter(name_filter)

    return dialog


def ask_save_file_name(initial_name: str, caption="Save signal", selected_name_filter=None):
    global RECENT_PATH
    if caption == "Save signal":
        name_filter = __get__name_filter_for_signals()
    elif caption == "Save fuzzing profile":
        name_filter = FUZZING_FILE_FILTER
    elif caption == "Save encoding":
        name_filter = ""
    elif caption == "Save simulator profile":
        name_filter = SIMULATOR_FILE_FILTER
    elif caption == "Export spectrogram":
        name_filter = "Frequency Time (*.ft);;Frequency Time Amplitude (*.fta)"
    elif caption == "Save protocol":
        name_filter = ";;".join([PROTOCOL_FILE_FILTER, BINARY_PROTOCOL_FILE_FILTER])
    elif caption == "Export demodulated":
        name_filter = WAV_FILE_FILTER
    else:
        name_filter = EVERYTHING_FILE_FILTER

    filename = None
    dialog = QFileDialog(directory=RECENT_PATH, caption=caption, filter=name_filter)
    dialog.setFileMode(QFileDialog.AnyFile)
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


def ask_signal_file_name_and_save(signal_name: str, data, sample_rate=1e6, wav_only=False, parent=None) -> str:
    if wav_only:
        if not signal_name.endswith(".wav") and not signal_name.endswith(".wave"):
            signal_name += ".wav"
        selected_name_filter = WAV_FILE_FILTER
    else:
        if not any(signal_name.endswith(e) for e in SIGNAL_NAME_FILTERS_BY_TYPE.values()):
            try:
                dtype = next(d for d in SIGNAL_FILE_EXTENSIONS_BY_TYPE.keys() if d == data.dtype)
                signal_name += SIGNAL_FILE_EXTENSIONS_BY_TYPE[dtype]
                selected_name_filter = SIGNAL_NAME_FILTERS_BY_TYPE[dtype]
            except StopIteration:
                selected_name_filter = None
        else:
            selected_name_filter = None

    filename = ask_save_file_name(signal_name, selected_name_filter=selected_name_filter)

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


def get_directory():
    directory = QFileDialog.getExistingDirectory(None, "Choose Directory", QDir.homePath(),
                                                 QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    return directory
