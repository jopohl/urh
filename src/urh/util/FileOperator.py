import os
import shutil
import tarfile
import tempfile
import wave
import zipfile

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from urh.cythonext.signalFunctions import Symbol

from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.util.Errors import Errors

VIEW_TYPES = ["Bits", "Hex", "ASCII"]

archives = {}
""":type: dict of [str, str]
   :param: archives[extracted_filename] = filename"""

RECENT_PATH = QDir.homePath()


def save_protocol(filename: str, viewtype: int, groups, decoding_names: list, symbols):
    """
    :type symbols: set of Symbol
    :type groups: list of ProtocolGroup
    :type proto_labels: list of ProtocolLabel
    :return:
    """
    if not filename.endswith(".txt"):
        filename += ".txt"
    with open(filename, mode="w") as f:
        f.write("# Viewtype of Protocol\n")
        f.write("# Possible Values: {0}\n".format(", ".join(VIEW_TYPES)))
        f.write("\n")
        f.write("VIEWTYPE = {0}\n".format(VIEW_TYPES[viewtype]))
        if len(symbols) > 0:
            f.write("SYMBOLS: \n")
        for s in symbols:
            f.write("- {0} {1:d} {2:d} {3:d}\n".format(s.name, s.nbits, s.pulsetype, s.nsamples))
        f.write("\n\n")

        for group in groups:
            f.write("GROUPNAME = {0}\n".format(group.name) )
            f.write("# Encodingindex for Group\n")
            f.write("# Possible Encodings: {0}\n".format(", ".join(decoding_names)))
            f.write("\n")
            f.write("ENCODING = {0:d}\n".format(decoding_names.index(group.decoding.name)))
            f.write("\n\n")

            f.write("PROTOCOL:\n\n")
            f.write("\n".join(group.decoded_bits_str))

            f.write("\n\n\nPROTOCOL-LABELS:")
            for label in group.labels:
                f.write("\n\n")
                f.write("Name: {0}\n".format(label.name))
                f.write("Bits: {0}-{1}\n".format(label.start+1, label.end))
                f.write("DO NOT CHANGE NEXT LINE:\n")
                f.write("Applies for Blocks: {0}\n".format(", ".join(map(str, label.block_numbers))))
                f.write("Apply Decoding: {0}\n".format(label.apply_decoding))
            f.write("\n\n")

def read_protocol(filename: str):
    if not os.path.isfile(filename):
        raise FileNotFoundError("{0} could not be found".format(filename))

    with open(filename, mode="r") as f:
        viewtype = 0
        reading_proto = False
        reading_labels = False
        reading_symbols = False
        label_name = None
        label_start = label_end = label_ref_block = -1
        label_blocks = None
        apply_decoding = None
        symbols = dict()
        cur_group = -1
        groups = []
        for line in f:
            line = line.strip()
            line = line.strip("\n")
            if line.startswith("#") or len(line) == 0:
                continue
            elif line.startswith("VIEWTYPE"):
                _, viewtype_str = line.split("=")
                viewtype_str = viewtype_str.strip()
                if viewtype_str not in VIEW_TYPES:
                    raise SyntaxError("Unknown Viewtype {0} in file {1}".format(viewtype_str, filename))
                else:
                    viewtype = VIEW_TYPES.index(viewtype_str)
            elif line.startswith("GROUPNAME"):
                _, name = line.split("=")
                cur_group += 1
                groups.append({})
                groups[cur_group]["name"] = name.strip()
                groups[cur_group]["blocks"] = []
                groups[cur_group]["labels"] = []
            elif line.startswith("ENCODING"):
                _, encoding_str = line.split("=")
                encoding_str = encoding_str.strip()
                decoding = int(encoding_str)
                groups[cur_group]["decoding_index"] = decoding
            elif line.startswith("SYMBOLS:"):
                reading_symbols = True
                reading_labels = False
                reading_proto = False
            elif line.startswith("PROTOCOL:"):
                reading_proto = True
                reading_symbols = False
                reading_labels = False
            elif line.startswith("PROTOCOL-LABELS:"):
                reading_proto = False
                reading_symbols = False
                reading_labels = True
            elif reading_symbols and line.startswith("-"):
                try:
                    _, symbol_name, nbits, pulsetype, nsamples = line.split(" ")
                    symbols[symbol_name] = Symbol(symbol_name, int(nbits), int(pulsetype),
                                                  int(nsamples))
                except ValueError:
                    continue
            elif reading_proto and len(line) > 0:
                groups[cur_group]["blocks"].append(ProtocolBlock.from_plain_bits_str(line, symbols))
            elif reading_labels and line.startswith("Name"):
                label_name = line.replace("Name: ","")
            elif reading_labels and line.startswith("Bits"):
                label_start, label_end = map(int, line.replace("Bits: ", "").split("-"))
                label_start -= 1
                label_end -= 1
            elif reading_labels and line.startswith("Reference Block"):
                label_ref_block = int(line.replace("Reference Block: ", "")) - 1
            elif reading_labels and line.startswith("Applies for Blocks: "):
                label_blocks = list(map(int, line.replace("Applies for Blocks: ", "").split(",")))
            elif reading_labels and line.startswith("Apply Decoding: "):
                apply_decoding = False if line.replace("Apply Decoding: ", "") == "False" else True


            if label_name is not None and label_start >= 0 and label_end >= 0\
                    and label_ref_block >= 0 and label_blocks is not None and apply_decoding is not None:
                color_index = len(groups[cur_group]["labels"])
                proto_label = ProtocolLabel(name=label_name, start=label_start, end=label_end,
                                            val_type_index=0, color_index=color_index)
                proto_label.block_numbers = label_blocks[:]
                proto_label.apply_decoding = apply_decoding
                groups[cur_group]["labels"].append(proto_label)

                label_name = None
                label_start = label_end = label_ref_block = -1
                label_blocks = None

        if len(groups) == 0:
            raise SyntaxError("Did not find a PROTOCOL in file " + filename)

        return viewtype, groups, set(symbols.values())


def uncompress_archives(filenames, temp_dir):
    """
    Extrahiert jedes Archiv aus der Liste von Dateinamen,
    normale Dateien bleiben unverändert.
    Fügt außerdem alle Dateien zu den Recent Files hinzu
    :type filenames: list of str
    :type temp_dir: str
    :rtype: list of str
    """
    fileNames = []
    for filename in filenames:
        if filename.endswith(".tar") or filename.endswith(".tar.gz") or filename.endswith(".tar.bz2"):
            obj = tarfile.open(filename, "r")
            extracted_filenames = []
            for j, member in enumerate(obj.getmembers()):
                obj.extract(member, temp_dir)
                extracted_filename = os.path.join(temp_dir, obj.getnames()[j])
                extracted_filenames.append(extracted_filename)
                archives[extracted_filename] = filename
            fileNames.extend(extracted_filenames[:])
        elif filename.endswith(".zip"):
            obj = zipfile.ZipFile(filename)
            extracted_filenames = []
            for j, info in enumerate(obj.infolist()):
                obj.extract(info, path=temp_dir)
                extracted_filename = os.path.join(temp_dir, obj.namelist()[j])
                extracted_filenames.append(extracted_filename)
                archives[extracted_filename] = filename
            fileNames.extend(extracted_filenames[:])
        else:
            fileNames.append(filename)

    return fileNames


def get_save_file_name(initial_name: str, wav_only=False, parent=None, caption="Save signal"):
    global RECENT_PATH
    if caption == "Save signal":
        filter = "Complex files (*.complex);;Compressed complex files (*.coco);;wav files (*.wav);;all files (*)"
        if wav_only:
            filter = "wav files (*.wav);;all files (*)"
    elif caption == "Save fuzz profile":
        filter = "Fuzzfiles (*.fuzz);;All files (*)"
    else:
        filter = "Textfiles (*.txt);;All files (*)"

    filename = None
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.AnyFile)
    dialog.setNameFilter(filter)
    dialog.setViewMode(QFileDialog.Detail)
    dialog.setDirectory(RECENT_PATH)
    dialog.setLabelText(QFileDialog.Accept, "Save")
    dialog.setWindowTitle(caption)
    dialog.setAcceptMode(QFileDialog.AcceptSave)
    dialog.selectFile(initial_name)

    if (dialog.exec()):
        filename = dialog.selectedFiles()[0]
        filter = dialog.selectedNameFilter()
        ext = filter[filter.index('*'):filter.index(')')][1:]
        if not os.path.exists(filename) and len(ext) > 0 and not filename.endswith(ext):
            filename += ext

    if filename:
        RECENT_PATH = os.path.split(filename)[0]

    return filename


def save_data_dialog(signalname: str, data, wav_only=False, parent=None) -> str:
    filename = get_save_file_name(signalname, wav_only, parent)

    if filename:
        try:
            save_data(data, filename)
        except Exception as e:
            QMessageBox.critical(parent, "Error saving signal", e.args[0])
            filename = None
    else:
        filename = None

    return filename

def save_data(data, filename: str):
    if filename.endswith(".wav"):
        f = wave.open(filename, "w")
        f.setnchannels(1)
        f.setsampwidth(1)
        f.setframerate(1000000)
        f.writeframes(data)
        f.my_close()
    elif filename.endswith(".coco"):
        with tarfile.open(filename, 'w:bz2') as tarwrite:
            tmp_name = os.path.join(QDir.tempPath(), "tmpfile")
            data.tofile(tmp_name)
            tarwrite.add(tmp_name)
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
    data = signal.data if not filename.endswith(".wav") else signal.wave_data
    save_data(data, filename)

def rewrite_zip(zipfname):
    tempdir = tempfile.mkdtemp()
    try:
        tempname = os.path.join(tempdir, 'new.zip')
        files_in_archive = [f for f in archives.keys() if archives[f] == zipfname]
        with zipfile.ZipFile(tempname, 'w') as zipwrite:
            for filename in files_in_archive:
                zipwrite.write(filename)
        shutil.move(tempname, zipfname)
    finally:
        shutil.rmtree(tempdir)


def rewrite_tar(tarname: str):
    tempdir = tempfile.mkdtemp()
    compression = ""
    if tarname.endswith("gz"):
        compression = "gz"
    elif tarname.endswith("bz2"):
        compression = "bz2"
    try:
        ext = "" if len(compression) == 0 else "." + compression
        tempname = os.path.join(tempdir, 'new.tar' + ext)
        files_in_archive = [f for f in archives.keys() if archives[f] == tarname]
        with tarfile.open(tempname, 'w:' + compression) as tarwrite:
            for file in files_in_archive:
                tarwrite.add(file)
        shutil.move(tempname, tarname)
    finally:
        shutil.rmtree(tempdir)


def get_directory():
    directory = QFileDialog.getExistingDirectory(None, "Choose Directory", QDir.homePath(),
                                                 QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    return directory
