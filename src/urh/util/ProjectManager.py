import os
import xml.etree.ElementTree as ET

from PyQt5.QtCore import QDir, Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from urh import constants
from urh.dev import config
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from xml.dom import minidom
from urh.signalprocessing.Signal import Signal
from urh.util import FileOperator


class ProjectManager(QObject):
    NEWLINE_CODE = "###~~~***~~~###_--:;;-__***~~~###"  # Newlines don't get loaded from xml properly
    AUTOSAVE_INTERVAL_MINUTES = 5

    project_loaded_status_changed = pyqtSignal(bool)
    project_updated = pyqtSignal()

    def __init__(self, main_controller):
        super().__init__()
        self.main_controller = main_controller
        self.device_conf = dict(frequency=config.DEFAULT_FREQUENCY,
                                sample_rate=config.DEFAULT_SAMPLE_RATE,
                                bandwidth=config.DEFAULT_BANDWIDTH,
                                gain=config.DEFAULT_GAIN)

        self.device = "USRP"
        self.description = ""
        self.project_path = ""
        self.broadcast_address_hex = "ffff"
        self.__project_file = None
        self.participants = []

    @property
    def project_loaded(self) -> bool:
        return self.project_file is not None

    @property
    def project_file(self):
        return self.__project_file

    @project_file.setter
    def project_file(self, value):
        self.__project_file = value
        self.project_loaded_status_changed.emit(self.project_loaded)

    def set_recording_parameters(self, device: str, kwargs: dict):
        for key, value in kwargs.items():
            self.device_conf[key] = value
        self.device = device

    def read_parameters(self, root):
        device_conf_tag = root.find("device_conf")
        if device_conf_tag is not None:
            for dev_tag in device_conf_tag:
                self.device_conf[dev_tag.tag] = float(dev_tag.text)

        self.description = root.get("description", "").replace(self.NEWLINE_CODE, "\n")
        self.broadcast_address_hex = root.get("broadcast_address_hex", "ffff")

    def read_message_types(self):
        if self.project_file is None:
            return None

        tree = ET.parse(self.project_file)
        root = tree.getroot()
        try:
            return [MessageType.from_xml(msg_type_tag) for msg_type_tag in
                    root.find("protocol").find("message_types").findall("message_type")]
        except AttributeError:
            return []

    def set_project_folder(self, path, ask_for_new_project=True):
        if path != self.project_path:
            self.main_controller.close_all()
        self.project_path = path
        self.project_file = os.path.join(self.project_path, constants.PROJECT_FILE)
        collapse_project_tabs = False
        if not os.path.isfile(self.project_file):
            if ask_for_new_project:
                reply = QMessageBox.question(self.main_controller, "Project File",
                                             "Do you want to create a Project File for this folder?\n"
                                             "If you chose No, you can do it later via File->Convert Folder to Project.",
                                             QMessageBox.Yes | QMessageBox.No)

                if reply == QMessageBox.Yes:
                    self.main_controller.show_project_settings()
                else:
                    self.project_file = None

            if self.project_file is not None:
                root = ET.Element("UniversalRadioHackerProject")
                tree = ET.ElementTree(root)
                tree.write(self.project_file)
        else:
            tree = ET.parse(self.project_file)
            root = tree.getroot()

            collapse_project_tabs = bool(int(root.get("collapse_project_tabs", 0)))
            cfc = self.main_controller.compare_frame_controller
            self.read_parameters(root)
            self.participants = cfc.proto_analyzer.read_participants_from_xml_tag(root=root.find("protocol"))
            self.main_controller.add_files(self.read_opened_filenames())
            self.read_compare_frame_groups(root)
            decodings = cfc.proto_analyzer.read_decoders_from_xml_tag(root.find("protocol"))
            if decodings:
                cfc.decodings = decodings
            cfc.fill_decoding_combobox()

            cfc.proto_analyzer.message_types = self.read_message_types()
            cfc.fill_message_type_combobox()
            cfc.proto_analyzer.from_xml_tag(root=root.find("protocol"), participants=self.participants,
                                            decodings=cfc.decodings)

            cfc.updateUI()
            modulators = self.read_modulators_from_project_file()
            self.main_controller.generator_tab_controller.modulators = modulators if modulators else [
                Modulator("Modulation")]
            self.main_controller.generator_tab_controller.refresh_modulators()

        if len(self.project_path) > 0 and self.project_file is None:
            self.main_controller.ui.actionConvert_Folder_to_Project.setEnabled(True)
        else:
            self.main_controller.ui.actionConvert_Folder_to_Project.setEnabled(False)

        self.main_controller.adjust_for_current_file(path)
        self.main_controller.filemodel.setRootPath(path)
        self.main_controller.ui.fileTree.setRootIndex(
            self.main_controller.file_proxy_model.mapFromSource(self.main_controller.filemodel.index(path)))
        self.main_controller.ui.fileTree.setToolTip(path)
        self.main_controller.ui.splitter.setSizes([1, 1])
        if collapse_project_tabs:
            self.main_controller.collapse_project_tab_bar()
        else:
            self.main_controller.expand_project_tab_bar()

        self.main_controller.setWindowTitle("Universal Radio Hacker [" + path + "]")

        self.project_loaded_status_changed.emit(self.project_loaded)
        self.project_updated.emit()

    def convert_folder_to_project(self):
        self.project_file = os.path.join(self.project_path, constants.PROJECT_FILE)
        self.main_controller.show_project_settings()

    def write_signal_information_to_project_file(self, signal: Signal, tree=None):
        if self.project_file is None or signal is None or len(signal.filename) == 0:
            return

        if tree is None:
            tree = ET.parse(self.project_file)

        root = tree.getroot()

        existing_filenames = {}

        for signal_tag in root.iter("signal"):
            existing_filenames[signal_tag.attrib["filename"]] = signal_tag

        if os.path.relpath(signal.filename, self.project_path) in existing_filenames.keys():
            signal_tag = existing_filenames[os.path.relpath(signal.filename, self.project_path)]
        else:
            # Neuen Tag anlegen
            signal_tag = ET.SubElement(root, "signal")

        signal_tag.set("name", signal.name)
        signal_tag.set("filename", os.path.relpath(signal.filename, self.project_path))
        signal_tag.set("bit_length", str(signal.bit_len))
        signal_tag.set("qad_center", str(signal.qad_center))
        signal_tag.set("tolerance", str(signal.tolerance))
        signal_tag.set("noise_threshold", str(signal.noise_threshold))
        signal_tag.set("noise_minimum", str(signal.noise_min_plot))
        signal_tag.set("noise_maximum", str(signal.noise_max_plot))
        signal_tag.set("auto_detect_on_modulation_changed", str(signal.auto_detect_on_modulation_changed))
        signal_tag.set("modulation_type", str(signal.modulation_type))
        signal_tag.set("sample_rate", str(signal.sample_rate))

        messages = ET.SubElement(signal_tag, "messages")
        for message in messages:
            messages.append(message.to_xml())

        tree.write(self.project_file)

    def write_modulators_to_project_file(self, modulators, tree=None):
        """
        :type modulators: list of Modulator
        :return:
        """
        if self.project_file is None or not modulators:
            return

        if tree is None:
            tree = ET.parse(self.project_file)

        root = tree.getroot()
        # Clear Modulations
        for mod_tag in root.findall("modulator"):
            root.remove(mod_tag)

        for i, mod in enumerate(modulators):
            root.append(mod.to_xml(i))

        tree.write(self.project_file)

    def read_modulators_from_project_file(self):
        """
        :rtype: list of Modulator
        """
        if not self.project_file:
            return []

        tree = ET.parse(self.project_file)
        root = tree.getroot()

        result = []
        for mod_tag in root.iter("modulator"):
            result.append(Modulator.from_xml(mod_tag))

        return result

    def saveProject(self):
        if self.project_file is None or not os.path.isfile(self.project_file):
            return

        # Recreate file
        open(self.project_file, 'w').close()
        root = ET.Element("UniversalRadioHackerProject")
        tree = ET.ElementTree(root)
        tree.write(self.project_file)

        # self.write_labels(self.maincontroller.compare_frame_controller.proto_analyzer)
        self.write_modulators_to_project_file(self.main_controller.generator_tab_controller.modulators, tree=tree)

        tree = ET.parse(self.project_file)
        root = tree.getroot()
        device_conf_tag = ET.SubElement(root, "device_conf")
        for key in sorted(self.device_conf):
            device_val_tag = ET.SubElement(device_conf_tag, key)
            device_val_tag.text = str(self.device_conf[key])
        root.set("description", str(self.description).replace("\n", self.NEWLINE_CODE))
        root.set("collapse_project_tabs", str(int(not self.main_controller.ui.tabParticipants.isVisible())))
        root.set("broadcast_address_hex", str(self.broadcast_address_hex))

        open_files = []
        for i, sf in enumerate(self.main_controller.signal_tab_controller.signal_frames):
            self.write_signal_information_to_project_file(sf.signal, tree=tree)
            try:
                pf = self.main_controller.signal_protocol_dict[sf]
                filename = pf.filename

                if filename in FileOperator.archives.keys():
                    open_filename = FileOperator.archives[filename]
                else:
                    open_filename = filename

                if not open_filename or open_filename in open_files:
                    continue
                open_files.append(open_filename)

                file_tag = ET.SubElement(root, "open_file")
                file_tag.set("name", os.path.relpath(open_filename, self.project_path))
                file_tag.set("position", str(i))
            except Exception:
                pass

        for group_tag in root.findall("group"):
            root.remove(group_tag)

        cfc = self.main_controller.compare_frame_controller

        for i, group in enumerate(cfc.groups):
            group_tag = ET.SubElement(root, "group")
            group_tag.set("name", str(group.name))
            group_tag.set("id", str(i))

            for proto_frame in cfc.protocols[i]:
                if proto_frame.filename:
                    proto_tag = ET.SubElement(group_tag, "cf_protocol")
                    proto_tag.set("filename", os.path.relpath(proto_frame.filename, self.project_path))
                    show = "1" if proto_frame.show else "0"
                    proto_tag.set("show", show)

        root.append(cfc.proto_analyzer.to_xml_tag(decodings=cfc.decodings, participants=self.participants))

        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(self.project_file, "w") as f:
            for line in xmlstr.split("\n"):
                if line.strip():
                    f.write(line + "\n")

    def read_participants_for_signal(self, signal: Signal, messages):
        if self.project_file is None or len(signal.filename) == 0:
            return False

        tree = ET.parse(self.project_file)
        root = tree.getroot()

        for sig_tag in root.iter("signal"):
            if sig_tag.attrib["filename"] == os.path.relpath(signal.filename, self.project_path):
                messages_tag = sig_tag.find("messages")

                try:
                    if messages_tag:
                        for i, message_tag in enumerate(messages_tag.iter("message")):
                            messages[i].from_xml(message_tag, self.participants)
                except IndexError:
                    return False

                return True

        return False

    def read_project_file_for_signal(self, signal: Signal):
        if self.project_file is None or len(signal.filename) == 0:
            return False

        tree = ET.parse(self.project_file)
        root = tree.getroot()
        for sig_tag in root.iter("signal"):
            if sig_tag.attrib["filename"] == os.path.relpath(signal.filename,
                                                             self.project_path):
                signal.name = sig_tag.attrib["name"]
                signal.qad_center = float(sig_tag.get("qad_center", 0))
                signal.tolerance = int(sig_tag.get("tolerance", 5))
                signal.auto_detect_on_modulation_changed = False if \
                    sig_tag.attrib[
                        "auto_detect_on_modulation_changed"] == 'False' else True

                signal.noise_threshold = float(sig_tag.get("noise_threshold", 0.1))
                signal.sample_rate = float(sig_tag.get("sample_rate", 1e6))
                signal.bit_len = int(sig_tag.get("bit_length", 100))
                signal.modulation_type = int(sig_tag.get("modulation_type", 0))
                break

        return True

    def read_opened_filenames(self):
        if self.project_file is not None:
            tree = ET.parse(self.project_file)
            root = tree.getroot()
            fileNames = []

            for ftag in root.findall("open_file"):
                pos = int(ftag.attrib["position"])
                filename = os.path.join(self.project_path, ftag.attrib["name"])
                fileNames.insert(pos, filename)

            fileNames = FileOperator.uncompress_archives(fileNames, QDir.tempPath())
            return fileNames
        return []

    def read_compare_frame_groups(self, root):
        proto_tree_model = self.main_controller.compare_frame_controller.proto_tree_model
        tree_root = proto_tree_model.rootItem
        pfi = proto_tree_model.protocol_tree_items
        proto_frame_items = [item for item in pfi[0]]
        """:type: list of ProtocolTreeItem """

        for group_tag in root.iter("group"):
            name = group_tag.attrib["name"]
            id = group_tag.attrib["id"]

            if id == "0":
                tree_root.child(0).setData(name)
            else:
                tree_root.addGroup(name=name)

            group = tree_root.child(int(id))

            for proto_tag in group_tag.iter("cf_protocol"):
                filename = os.path.join(self.project_path, proto_tag.attrib["filename"])
                show = proto_tag.attrib["show"]
                try:
                    proto_frame_item = next((p for p in proto_frame_items if p.protocol.filename == filename))
                except StopIteration:
                    proto_frame_item = None

                if proto_frame_item is not None:
                    group.appendChild(proto_frame_item)
                    proto_frame_item.show_in_compare_frame = Qt.Checked if show == "1" else Qt.Unchecked

            self.main_controller.compare_frame_controller.expand_group_node(int(id))

        self.main_controller.compare_frame_controller.refresh()

    def from_dialog(self, dialog):
        if dialog.committed:
            if dialog.new_project or not os.path.isfile(os.path.join(dialog.path, constants.PROJECT_FILE)):
                self.set_project_folder(dialog.path, ask_for_new_project=False)
            self.device_conf["frequency"] = dialog.freq
            self.device_conf["sample_rate"] = dialog.sample_rate
            self.device_conf["gain"] = dialog.gain
            self.device_conf["bandwidth"] = dialog.bandwidth
            self.description = dialog.description
            self.broadcast_address_hex = dialog.broadcast_address_hex.lower().replace(" ", "")
            if dialog.new_project:
                self.participants = dialog.participants
            self.project_updated.emit()
