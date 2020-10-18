import os
import xml.etree.ElementTree as ET

from PyQt5.QtCore import QDir, Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QApplication

from urh import settings
from urh.dev import config
from urh.models.ProtocolTreeItem import ProtocolTreeItem
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.Signal import Signal
from urh.util import FileOperator, util
from urh.util.Logger import logger


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
                                name="USRP")

        self.simulator_rx_conf = dict()
        self.simulator_tx_conf = dict()

        self.simulator_num_repeat = 1
        self.simulator_retries = 10
        self.simulator_timeout_ms = 2500
        self.simulator_error_handling_index = 2

        self.__project_file = None

        self.__modulators = [Modulator("Modulator")]  # type: list[Modulator]

        self.__decodings = []  # type: list[Encoding]
        self.load_decodings()

        self.modulation_was_edited = False
        self.description = ""
        self.project_path = ""
        self.broadcast_address_hex = "ffff"
        self.participants = []

        self.field_types = []  # type: list[FieldType]
        self.field_types_by_caption = dict()
        self.reload_field_types()

    @property
    def modulators(self):
        return self.__modulators

    @modulators.setter
    def modulators(self, value):
        if value:
            self.__modulators[:] = value
            if hasattr(self.main_controller, "generator_tab_controller"):
                self.main_controller.generator_tab_controller.refresh_modulators()

    @property
    def decodings(self):
        return self.__decodings

    @decodings.setter
    def decodings(self, value):
        if value:
            self.__decodings[:] = value
            if hasattr(self.main_controller, "compare_frame_controller"):
                self.main_controller.compare_frame_controller.fill_decoding_combobox()

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

    def reload_field_types(self):
        self.field_types = FieldType.load_from_xml()
        self.field_types_by_caption = {field_type.caption: field_type for field_type in self.field_types}

    def set_device_parameters(self, kwargs: dict):
        for key, value in kwargs.items():
            self.device_conf[key] = value

    def on_simulator_rx_parameters_changed(self, kwargs: dict):
        for key, value in kwargs.items():
            self.simulator_rx_conf[key] = value

    def on_simulator_tx_parameters_changed(self, kwargs: dict):
        for key, value in kwargs.items():
            self.simulator_tx_conf[key] = value

    def on_simulator_sniff_parameters_changed(self, kwargs: dict):
        for key, value in kwargs.items():
            # Save sniff values in common device conf
            self.device_conf[key] = value

    def load_decodings(self):
        if self.project_file:
            return
        else:
            prefix = os.path.realpath(os.path.join(settings.get_qt_settings_filename(), ".."))

        fallback = [Encoding(["Non Return To Zero (NRZ)"]),

                    Encoding(["Non Return To Zero + Invert",
                              settings.DECODING_INVERT]),

                    Encoding(["Manchester I",
                              settings.DECODING_EDGE]),

                    Encoding(["Manchester II",
                              settings.DECODING_EDGE,
                              settings.DECODING_INVERT]),

                    Encoding(["Differential Manchester",
                              settings.DECODING_EDGE,
                              settings.DECODING_DIFFERENTIAL])
                    ]

        try:
            f = open(os.path.join(prefix, settings.DECODINGS_FILE), "r")
        except FileNotFoundError:
            self.decodings = fallback
            return

        decodings = []
        for line in map(str.strip, f):
            tmp_conf = []
            for j in map(str.strip, line.split(",")):
                tmp_conf.append(j.replace("'", ""))
            decodings.append(Encoding(tmp_conf))
        f.close()

        self.decodings = decodings if decodings else fallback

    @staticmethod
    def read_device_conf_dict(tag: ET.Element, target_dict):
        if tag is None:
            return

        for dev_tag in tag:
            if dev_tag.text is None:
                logger.warn("{} has None text".format(str(dev_tag)))
                continue
            try:
                try:
                    value = int(dev_tag.text)
                except ValueError:
                    value = float(dev_tag.text)
            except ValueError:
                value = dev_tag.text

            if dev_tag.tag == "bit_len":
                target_dict["samples_per_symbol"] = value   # legacy
            else:
                target_dict[dev_tag.tag] = value

    @staticmethod
    def __device_conf_dict_to_xml(key_name: str, device_conf: dict):
        result = ET.Element(key_name)
        for key in sorted(device_conf):
            device_val_tag = ET.SubElement(result, key)
            device_val_tag.text = str(device_conf[key])
        return result

    def simulator_rx_conf_to_xml(self) -> ET.Element:
        return self.__device_conf_dict_to_xml("simulator_rx_conf", self.simulator_rx_conf)

    def simulator_tx_conf_to_xml(self) -> ET.Element:
        return self.__device_conf_dict_to_xml("simulator_tx_conf", self.simulator_tx_conf)

    def read_parameters(self, root):
        self.read_device_conf_dict(root.find("device_conf"), target_dict=self.device_conf)
        self.read_device_conf_dict(root.find("simulator_rx_conf"), target_dict=self.simulator_rx_conf)
        self.read_device_conf_dict(root.find("simulator_tx_conf"), target_dict=self.simulator_tx_conf)

        self.description = root.get("description", "").replace(self.NEWLINE_CODE, "\n")
        self.broadcast_address_hex = root.get("broadcast_address_hex", "ffff")

    def read_message_types(self):
        if self.project_file is None:
            return None

        tree = ET.parse(self.project_file)
        root = tree.getroot()
        result = []
        for msg_type_tag in root.find("protocol").find("message_types").findall("message_type"):
            result.append(MessageType.from_xml(msg_type_tag))

        return result

    def set_project_folder(self, path, ask_for_new_project=True, close_all=True):
        if self.project_file is not None or close_all:
            # Close existing project (if any) or existing files if requested
            self.main_controller.close_all_files()
        FileOperator.RECENT_PATH = path
        util.PROJECT_PATH = path
        self.project_path = path
        self.project_file = os.path.join(self.project_path, settings.PROJECT_FILE)
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
                self.modulation_was_edited = False
        else:
            tree = ET.parse(self.project_file)
            root = tree.getroot()

            collapse_project_tabs = bool(int(root.get("collapse_project_tabs", 0)))
            self.modulation_was_edited = bool(int(root.get("modulation_was_edited", 0)))
            cfc = self.main_controller.compare_frame_controller
            self.read_parameters(root)
            self.participants[:] = Participant.read_participants_from_xml_tag(xml_tag=root.find("protocol"))
            self.main_controller.add_files(self.read_opened_filenames())
            self.read_compare_frame_groups(root)
            self.decodings = Encoding.read_decoders_from_xml_tag(root.find("protocol"))

            cfc.proto_analyzer.message_types[:] = self.read_message_types()
            cfc.message_type_table_model.update()
            cfc.proto_analyzer.from_xml_tag(root=root.find("protocol"), participants=self.participants,
                                            decodings=cfc.decodings)

            cfc.updateUI()

            try:
                for message_type in cfc.proto_analyzer.message_types:
                    for lbl in filter(lambda x: not x.show, message_type):
                        cfc.set_protocol_label_visibility(lbl)
            except Exception as e:
                logger.exception(e)

            self.modulators = self.read_modulators_from_project_file()
            self.main_controller.simulator_tab_controller.load_config_from_xml_tag(root.find("simulator_config"))

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
        self.project_file = os.path.join(self.project_path, settings.PROJECT_FILE)
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

        try:
            file_path = os.path.relpath(signal.filename, self.project_path)
        except ValueError:
            # Can happen e.g. on Windows when Project is in C:\ and signal on D:\
            file_path = signal.filename

        if file_path in existing_filenames.keys():
            signal_tag = existing_filenames[file_path]
        else:
            # Create new tag
            signal_tag = ET.SubElement(root, "signal")

        signal_tag.set("name", signal.name)
        signal_tag.set("filename", file_path)
        signal_tag.set("samples_per_symbol", str(signal.samples_per_symbol))
        signal_tag.set("center", str(signal.center))
        signal_tag.set("center_spacing", str(signal.center_spacing))
        signal_tag.set("tolerance", str(signal.tolerance))
        signal_tag.set("noise_threshold", str(signal.noise_threshold))
        signal_tag.set("noise_minimum", str(signal.noise_min_plot))
        signal_tag.set("noise_maximum", str(signal.noise_max_plot))
        signal_tag.set("modulation_type", str(signal.modulation_type))
        signal_tag.set("sample_rate", str(signal.sample_rate))
        signal_tag.set("pause_threshold", str(signal.pause_threshold))
        signal_tag.set("message_length_divisor", str(signal.message_length_divisor))
        signal_tag.set("bits_per_symbol", str(signal.bits_per_symbol))
        signal_tag.set("costas_loop_bandwidth", str(signal.costas_loop_bandwidth))

        messages = ET.SubElement(signal_tag, "messages")
        for message in messages:
            messages.append(message.to_xml())

        tree.write(self.project_file)

    def write_modulators_to_project_file(self, tree=None):
        """
        :type modulators: list of Modulator
        :return:
        """
        if self.project_file is None or not self.modulators:
            return

        if tree is None:
            tree = ET.parse(self.project_file)

        root = tree.getroot()
        root.append(Modulator.modulators_to_xml_tag(self.modulators))

        tree.write(self.project_file)

    def read_modulators_from_project_file(self):
        """
        :rtype: list of Modulator
        """
        return ProjectManager.read_modulators_from_file(self.project_file)

    @staticmethod
    def read_modulators_from_file(filename: str):
        if not filename:
            return []

        tree = ET.parse(filename)
        root = tree.getroot()

        return Modulator.modulators_from_xml_tag(root)

    def save_project(self, simulator_config=None):
        if self.project_file is None or not os.path.isfile(self.project_file):
            return

        # Recreate file
        open(self.project_file, 'w').close()
        root = ET.Element("UniversalRadioHackerProject")
        tree = ET.ElementTree(root)
        tree.write(self.project_file)

        # self.write_labels(self.maincontroller.compare_frame_controller.proto_analyzer)
        self.write_modulators_to_project_file(tree=tree)

        tree = ET.parse(self.project_file)
        root = tree.getroot()
        root.append(self.__device_conf_dict_to_xml("device_conf", self.device_conf))
        root.append(self.simulator_rx_conf_to_xml())
        root.append(self.simulator_tx_conf_to_xml())
        root.set("description", str(self.description).replace("\n", self.NEWLINE_CODE))
        root.set("collapse_project_tabs", str(int(not self.main_controller.ui.tabParticipants.isVisible())))
        root.set("modulation_was_edited", str(int(self.modulation_was_edited)))
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
                try:
                    file_path = os.path.relpath(open_filename, self.project_path)
                except ValueError:
                    file_path = open_filename

                file_tag.set("name", file_path)
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
                    try:
                        rel_file_name = os.path.relpath(proto_frame.filename, self.project_path)
                    except ValueError:
                        rel_file_name = proto_frame.filename

                    proto_tag.set("filename", rel_file_name)

        root.append(cfc.proto_analyzer.to_xml_tag(decodings=cfc.decodings, participants=self.participants,
                                                  messages=[msg for proto in cfc.full_protocol_list for msg in
                                                            proto.messages]))

        if simulator_config is not None:
            root.append(simulator_config.save_to_xml())

        util.write_xml_to_file(root, self.project_file)

    def read_participants_for_signal(self, signal: Signal, messages):
        if self.project_file is None or len(signal.filename) == 0:
            return False

        tree = ET.parse(self.project_file)
        root = tree.getroot()

        try:
            signal_filename = os.path.relpath(signal.filename, self.project_path)
        except ValueError:
            signal_filename = signal.filename

        for sig_tag in root.iter("signal"):
            if sig_tag.attrib["filename"] == signal_filename:
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

        try:
            signal_filename = os.path.relpath(signal.filename, self.project_path)
        except ValueError:
            signal_filename = signal.filename

        for sig_tag in root.iter("signal"):
            if sig_tag.attrib["filename"] == signal_filename:
                signal.name = sig_tag.attrib["name"]
                center = sig_tag.get("qad_center", None)  # legacy support
                signal.center = float(sig_tag.get("center", 0)) if center is None else float(center)
                signal.center_spacing = float(sig_tag.get("center_spacing", 0.1))
                signal.tolerance = int(sig_tag.get("tolerance", 5))
                signal.bits_per_symbol = int(sig_tag.get("bits_per_symbol", 1))
                signal.costas_loop_bandwidth = float(sig_tag.get("costas_loop_bandwidth", 0.1))

                signal.noise_threshold = float(sig_tag.get("noise_threshold", 0.1))
                signal.sample_rate = float(sig_tag.get("sample_rate", 1e6))
                signal.samples_per_symbol = int(sig_tag.get("bit_length", 0))   # Legacy for old project files
                if signal.samples_per_symbol == 0:
                    signal.samples_per_symbol = int(sig_tag.get("samples_per_symbol", 100))

                try:
                    # Legacy support when modulation type was integer
                    signal.modulation_type = Signal.MODULATION_TYPES[int(sig_tag.get("modulation_type", 0))]
                except (ValueError, IndexError):
                    signal.modulation_type = sig_tag.get("modulation_type", "ASK")
                signal.pause_threshold = int(sig_tag.get("pause_threshold", 8))
                signal.message_length_divisor = int(sig_tag.get("message_length_divisor", 1))
                break

        return True

    def read_opened_filenames(self):
        if self.project_file is not None:
            tree = ET.parse(self.project_file)
            root = tree.getroot()
            file_names = []

            for file_tag in root.findall("open_file"):
                pos = int(file_tag.attrib["position"])
                filename = file_tag.attrib["name"]
                if not os.path.isfile(filename):
                    filename = os.path.normpath(os.path.join(self.project_path, filename))
                file_names.insert(pos, filename)

            QApplication.setOverrideCursor(Qt.WaitCursor)
            file_names = FileOperator.uncompress_archives(file_names, QDir.tempPath())
            QApplication.restoreOverrideCursor()
            return file_names
        return []

    def read_compare_frame_groups(self, root):
        proto_tree_model = self.main_controller.compare_frame_controller.proto_tree_model
        tree_root = proto_tree_model.rootItem
        pfi = proto_tree_model.protocol_tree_items
        proto_frame_items = [item for item in pfi[0]]  # type:  list[ProtocolTreeItem]

        for group_tag in root.iter("group"):
            name = group_tag.attrib["name"]
            id = group_tag.attrib["id"]

            if id == "0":
                tree_root.child(0).setData(name)
            else:
                tree_root.addGroup(name=name)

            group = tree_root.child(int(id))

            for proto_tag in group_tag.iter("cf_protocol"):
                filename = proto_tag.attrib["filename"]
                if not os.path.isfile(filename):
                    filename = os.path.normpath(os.path.join(self.project_path, filename))
                try:
                    proto_frame_item = next((p for p in proto_frame_items if p.protocol.filename == filename))
                except StopIteration:
                    proto_frame_item = None

                if proto_frame_item is not None:
                    group.appendChild(proto_frame_item)

            self.main_controller.compare_frame_controller.expand_group_node(int(id))

        self.main_controller.compare_frame_controller.refresh()

    def from_dialog(self, dialog):
        if dialog.committed:
            if dialog.new_project or not os.path.isfile(os.path.join(dialog.path, settings.PROJECT_FILE)):
                self.set_project_folder(dialog.path, ask_for_new_project=False, close_all=False)
            self.device_conf["frequency"] = dialog.freq
            self.device_conf["sample_rate"] = dialog.sample_rate
            self.device_conf["gain"] = dialog.gain
            self.device_conf["bandwidth"] = dialog.bandwidth
            self.description = dialog.description
            self.broadcast_address_hex = dialog.broadcast_address_hex.lower().replace(" ", "")
            if dialog.new_project:
                self.participants[:] = dialog.participants
            self.project_updated.emit()
