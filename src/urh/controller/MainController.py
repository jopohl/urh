import copy
import os
import traceback

from PyQt5.QtCore import QDir, Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon, QCloseEvent, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QUndoGroup, QActionGroup, QHeaderView, QAction, QFileDialog, \
    QMessageBox, QApplication

from urh import constants, version
from urh.controller.dialogs.CSVImportDialog import CSVImportDialog
from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.dialogs.DecoderDialog import DecoderDialog
from urh.controller.GeneratorTabController import GeneratorTabController
from urh.controller.dialogs.OptionsDialog import OptionsDialog
from urh.controller.dialogs.ProjectDialog import ProjectDialog
from urh.controller.dialogs.ProtocolSniffDialog import ProtocolSniffDialog
from urh.controller.dialogs.ReceiveDialog import ReceiveDialog
from urh.controller.widgets.SignalFrame import SignalFrame
from urh.controller.SignalTabController import SignalTabController
from urh.controller.SimulatorTabController import SimulatorTabController
from urh.controller.dialogs.SpectrumDialogController import SpectrumDialogController
from urh.models.FileFilterProxyModel import FileFilterProxyModel
from urh.models.FileIconProvider import FileIconProvider
from urh.models.FileSystemModel import FileSystemModel
from urh.models.ParticipantLegendListModel import ParticipantLegendListModel
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.ui.ui_main import Ui_MainWindow
from urh.util import FileOperator, util
from urh.util.Errors import Errors
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class MainController(QMainWindow):
    def __init__(self, *args):
        super().__init__(*args)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        util.set_splitter_stylesheet(self.ui.splitter)

        OptionsDialog.write_default_options()

        self.project_save_timer = QTimer()
        self.project_manager = ProjectManager(self)
        self.plugin_manager = PluginManager()
        self.signal_tab_controller = SignalTabController(self.project_manager,
                                                         parent=self.ui.tab_interpretation)
        self.ui.tab_interpretation.layout().addWidget(self.signal_tab_controller)
        self.compare_frame_controller = CompareFrameController(parent=self.ui.tab_protocol,
                                                               plugin_manager=self.plugin_manager,
                                                               project_manager=self.project_manager)
        self.compare_frame_controller.ui.splitter.setSizes([1, 1000000])

        self.ui.tab_protocol.layout().addWidget(self.compare_frame_controller)

        self.generator_tab_controller = GeneratorTabController(self.compare_frame_controller,
                                                               self.project_manager,
                                                               parent=self.ui.tab_generator)

        self.simulator_tab_controller = SimulatorTabController(parent=self.ui.tab_simulator,
                                                               compare_frame_controller=self.compare_frame_controller,
                                                               generator_tab_controller=self.generator_tab_controller,
                                                               project_manager=self.project_manager)

        self.ui.tab_simulator.layout().addWidget(self.simulator_tab_controller)

        self.undo_group = QUndoGroup()
        self.undo_group.addStack(self.signal_tab_controller.signal_undo_stack)
        self.undo_group.addStack(self.compare_frame_controller.protocol_undo_stack)
        self.undo_group.addStack(self.generator_tab_controller.generator_undo_stack)
        self.undo_group.setActiveStack(self.signal_tab_controller.signal_undo_stack)

        self.cancel_action = QAction(self.tr("Cancel"), self)
        self.cancel_action.setShortcut(QKeySequence.Cancel if hasattr(QKeySequence, "Cancel") else "Esc")
        self.cancel_action.triggered.connect(self.on_cancel_triggered)
        self.cancel_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.cancel_action.setIcon(QIcon.fromTheme("dialog-cancel"))
        self.addAction(self.cancel_action)

        self.participant_legend_model = ParticipantLegendListModel(self.project_manager.participants)
        self.ui.listViewParticipants.setModel(self.participant_legend_model)

        gtc = self.generator_tab_controller
        gtc.ui.splitter.setSizes([gtc.width() / 0.7, gtc.width() / 0.3])

        self.ui.tab_generator.layout().addWidget(self.generator_tab_controller)

        self.signal_protocol_dict = {}  # type: dict[SignalFrame, ProtocolAnalyzer]

        self.ui.lnEdtTreeFilter.setClearButtonEnabled(True)

        group = QActionGroup(self)
        self.ui.actionFSK.setActionGroup(group)
        self.ui.actionOOK.setActionGroup(group)
        self.ui.actionNone.setActionGroup(group)
        self.ui.actionPSK.setActionGroup(group)

        self.recentFileActionList = []
        self.create_connects()
        self.init_recent_file_action_list(constants.SETTINGS.value("recentFiles", []))

        self.filemodel = FileSystemModel(self)
        path = QDir.homePath()

        self.filemodel.setIconProvider(FileIconProvider())
        self.filemodel.setRootPath(path)
        self.file_proxy_model = FileFilterProxyModel(self)
        self.file_proxy_model.setSourceModel(self.filemodel)
        self.ui.fileTree.setModel(self.file_proxy_model)

        self.ui.fileTree.setRootIndex(self.file_proxy_model.mapFromSource(self.filemodel.index(path)))
        self.ui.fileTree.setToolTip(path)
        self.ui.fileTree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.fileTree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.fileTree.setFocus()

        self.generator_tab_controller.table_model.cfc = self.compare_frame_controller

        self.ui.actionConvert_Folder_to_Project.setEnabled(False)

        undo_action = self.undo_group.createUndoAction(self)
        undo_action.setIcon(QIcon.fromTheme("edit-undo"))
        undo_action.setShortcut(QKeySequence.Undo)
        self.ui.menuEdit.insertAction(self.ui.actionDecoding, undo_action)

        redo_action = self.undo_group.createRedoAction(self)
        redo_action.setIcon(QIcon.fromTheme("edit-redo"))
        redo_action.setShortcut(QKeySequence.Redo)
        self.ui.menuEdit.insertAction(self.ui.actionDecoding, redo_action)
        self.ui.menuEdit.insertSeparator(self.ui.actionDecoding)

        self.ui.actionAbout_Qt.setIcon(QIcon(":/qt-project.org/qmessagebox/images/qtlogo-64.png"))

        self.__set_non_project_warning_visibility()

        self.ui.splitter.setSizes([0, 1])
        self.refresh_main_menu()

        self.apply_default_view(constants.SETTINGS.value('default_view', type=int))
        self.project_save_timer.start(ProjectManager.AUTOSAVE_INTERVAL_MINUTES * 60 * 1000)

        self.ui.actionProject_settings.setVisible(False)
        self.ui.actionSave_project.setVisible(False)

    def __set_non_project_warning_visibility(self):
        show = constants.SETTINGS.value("show_non_project_warning", True, bool) and not self.project_manager.project_loaded
        self.ui.labelNonProjectMode.setVisible(show)

    def create_connects(self):
        self.ui.actionFullscreen_mode.setShortcut(QKeySequence.FullScreen)
        self.ui.actionOpen.setShortcut(QKeySequence(QKeySequence.Open))
        self.ui.actionOpen_directory.setShortcut(QKeySequence("Ctrl+Shift+O"))

        self.ui.menuEdit.aboutToShow.connect(self.on_edit_menu_about_to_show)

        self.ui.actionNew_Project.triggered.connect(self.on_new_project_action_triggered)
        self.ui.actionNew_Project.setShortcut(QKeySequence.New)
        self.ui.actionProject_settings.triggered.connect(self.on_project_settings_action_triggered)
        self.ui.actionSave_project.triggered.connect(self.save_project)

        self.ui.actionAbout_AutomaticHacker.triggered.connect(self.on_show_about_clicked)
        self.ui.actionRecord.triggered.connect(self.on_show_record_dialog_action_triggered)

        self.ui.actionFullscreen_mode.triggered.connect(self.on_fullscreen_action_triggered)
        self.ui.actionSaveAllSignals.triggered.connect(self.signal_tab_controller.save_all)
        self.ui.actionClose_all.triggered.connect(self.on_close_all_action_triggered)
        self.ui.actionOpen.triggered.connect(self.on_open_file_action_triggered)
        self.ui.actionOpen_directory.triggered.connect(self.on_open_directory_action_triggered)
        self.ui.actionDecoding.triggered.connect(self.on_show_decoding_dialog_triggered)
        self.ui.actionSpectrum_Analyzer.triggered.connect(self.on_show_spectrum_dialog_action_triggered)
        self.ui.actionOptions.triggered.connect(self.show_options_dialog_action_triggered)
        self.ui.actionSniff_protocol.triggered.connect(self.show_proto_sniff_dialog)
        self.ui.actionAbout_Qt.triggered.connect(QApplication.instance().aboutQt)
        self.ui.actionSamples_from_csv.triggered.connect(self.on_import_samples_from_csv_action_triggered)

        self.ui.btnFileTreeGoUp.clicked.connect(self.on_btn_file_tree_go_up_clicked)
        self.ui.fileTree.directory_open_wanted.connect(self.project_manager.set_project_folder)

        self.signal_tab_controller.frame_closed.connect(self.close_signal_frame)
        self.signal_tab_controller.signal_created.connect(self.on_signal_created)
        self.signal_tab_controller.ui.scrollArea.files_dropped.connect(self.on_files_dropped)
        self.signal_tab_controller.files_dropped.connect(self.on_files_dropped)
        self.signal_tab_controller.frame_was_dropped.connect(self.set_frame_numbers)

        self.simulator_tab_controller.open_in_analysis_requested.connect(self.on_simulator_open_in_analysis_requested)
        self.simulator_tab_controller.rx_file_saved.connect(self.adjust_for_current_file)

        self.compare_frame_controller.show_interpretation_clicked.connect(
            self.show_protocol_selection_in_interpretation)
        self.compare_frame_controller.files_dropped.connect(self.on_files_dropped)
        self.compare_frame_controller.show_decoding_clicked.connect(self.on_show_decoding_dialog_triggered)
        self.compare_frame_controller.ui.treeViewProtocols.files_dropped_on_group.connect(
            self.on_files_dropped_on_group)
        self.compare_frame_controller.participant_changed.connect(self.signal_tab_controller.on_participant_changed)
        self.compare_frame_controller.ui.treeViewProtocols.close_wanted.connect(self.on_cfc_close_wanted)
        self.compare_frame_controller.show_config_field_types_triggered.connect(
            self.on_show_field_types_config_action_triggered)

        self.compare_frame_controller.load_protocol_clicked.connect(self.on_compare_frame_controller_load_protocol_clicked)

        self.ui.lnEdtTreeFilter.textChanged.connect(self.on_file_tree_filter_text_changed)

        self.ui.tabWidget.currentChanged.connect(self.on_selected_tab_changed)
        self.project_save_timer.timeout.connect(self.save_project)

        self.ui.actionConvert_Folder_to_Project.triggered.connect(self.project_manager.convert_folder_to_project)
        self.project_manager.project_loaded_status_changed.connect(self.on_project_loaded_status_changed)
        self.project_manager.project_updated.connect(self.on_project_updated)

        self.ui.textEditProjectDescription.textChanged.connect(self.on_text_edit_project_description_text_changed)
        self.ui.tabWidget_Project.tabBarDoubleClicked.connect(self.on_project_tab_bar_double_clicked)

        self.ui.listViewParticipants.doubleClicked.connect(self.on_project_settings_action_triggered)

        self.ui.actionShowFileTree.triggered.connect(self.on_action_show_filetree_triggered)
        self.ui.actionShowFileTree.setShortcut(QKeySequence("F10"))

        self.ui.labelNonProjectMode.linkActivated.connect(self.on_label_non_project_mode_link_activated)

        self.ui.menuFile.addSeparator()
        for i in range(constants.MAX_RECENT_FILE_NR):
            recent_file_action = QAction(self)
            recent_file_action.setVisible(False)
            recent_file_action.triggered.connect(self.on_open_recent_action_triggered)
            self.recentFileActionList.append(recent_file_action)
            self.ui.menuFile.addAction(self.recentFileActionList[i])

    def add_plain_bits_from_txt(self, filename: str):
        with open(filename) as f:
            protocol = ProtocolAnalyzer.get_protocol_from_string(f.readlines())

        protocol.filename = filename
        protocol.name = util.get_name_from_filename(filename)

        self.compare_frame_controller.add_protocol(protocol)
        self.compare_frame_controller.refresh()
        self.__add_empty_frame_for_filename(protocol, filename)

    def __add_empty_frame_for_filename(self, protocol: ProtocolAnalyzer, filename: str):
        sf = self.signal_tab_controller.add_empty_frame(filename, protocol)
        self.signal_protocol_dict[sf] = protocol
        self.set_frame_numbers()
        self.file_proxy_model.open_files.add(filename)

    def add_protocol_file(self, filename):
        proto = self.compare_frame_controller.add_protocol_from_file(filename)
        if proto:
            self.__add_empty_frame_for_filename(proto, filename)

    def add_fuzz_profile(self, filename):
        self.ui.tabWidget.setCurrentIndex(2)
        self.generator_tab_controller.load_from_file(filename)

    def add_simulator_profile(self, filename):
        self.ui.tabWidget.setCurrentIndex(3)
        self.simulator_tab_controller.load_simulator_file(filename)

    def add_signalfile(self, filename: str, group_id=0, enforce_sample_rate=None):
        if not os.path.exists(filename):
            QMessageBox.critical(self, self.tr("File not Found"),
                                 self.tr("The file {0} could not be found. Was it moved or renamed?").format(
                                     filename))
            return

        sig_name = os.path.splitext(os.path.basename(filename))[0]

        # Use default sample rate for signal
        # Sample rate will be overriden in case of a project later
        if enforce_sample_rate is not None:
            sample_rate = enforce_sample_rate
        else:
            sample_rate = self.project_manager.device_conf["sample_rate"]

        signal = Signal(filename, sig_name, sample_rate=sample_rate)

        self.file_proxy_model.open_files.add(filename)
        self.add_signal(signal, group_id)

    def add_signal(self, signal, group_id=0, index=-1):
        self.setCursor(Qt.WaitCursor)
        pa = ProtocolAnalyzer(signal)
        sig_frame = self.signal_tab_controller.add_signal_frame(pa, index=index)
        pa = self.compare_frame_controller.add_protocol(pa, group_id)

        signal.blockSignals(True)
        has_entry = self.project_manager.read_project_file_for_signal(signal)

        if not has_entry and not signal.changed:
            signal.auto_detect()

        signal.blockSignals(False)

        self.signal_protocol_dict[sig_frame] = pa

        sig_frame.refresh(draw_full_signal=True)  # protocol is derived here
        if self.project_manager.read_participants_for_signal(signal, pa.messages):
            sig_frame.ui.gvSignal.redraw_view()

        sig_frame.ui.gvSignal.auto_fit_view()
        self.set_frame_numbers()

        self.compare_frame_controller.filter_search_results()
        self.refresh_main_menu()
        self.unsetCursor()

    def close_protocol(self, protocol):
        self.compare_frame_controller.remove_protocol(protocol)
        # Needs to be removed in generator also, otherwise program crashes,
        # if item from tree in generator is selected and corresponding signal is closed
        self.generator_tab_controller.tree_model.remove_protocol(protocol)
        protocol.eliminate()

    def close_signal_frame(self, signal_frame: SignalFrame):
        try:
            self.project_manager.write_signal_information_to_project_file(signal_frame.signal)
            try:
                proto = self.signal_protocol_dict[signal_frame]
            except KeyError:
                proto = None

            if proto is not None:
                self.close_protocol(proto)
                del self.signal_protocol_dict[signal_frame]

            if self.signal_tab_controller.ui.scrlAreaSignals.minimumHeight() > signal_frame.height():
                self.signal_tab_controller.ui.scrlAreaSignals.setMinimumHeight(
                    self.signal_tab_controller.ui.scrlAreaSignals.minimumHeight() - signal_frame.height())

            if signal_frame.signal is not None:
                # Non-Empty Frame (when a signal and not a protocol is opened)
                self.file_proxy_model.open_files.discard(signal_frame.signal.filename)

            signal_frame.eliminate()

            self.compare_frame_controller.ui.treeViewProtocols.expandAll()
            self.set_frame_numbers()
            self.refresh_main_menu()
        except Exception as e:
            Errors.generic_error(self.tr("Failed to close"), str(e), traceback.format_exc())
            self.unsetCursor()

    def add_files(self, filepaths, group_id=0, enforce_sample_rate=None):
        num_files = len(filepaths)
        if num_files == 0:
            return

        for i, filename in enumerate(filepaths):
            if not os.path.exists(filename):
                continue

            if os.path.isdir(filename):
                for f in self.signal_tab_controller.signal_frames:
                    self.close_signal_frame(f)

                FileOperator.RECENT_PATH = filename
                self.project_manager.set_project_folder(filename)
                return

            FileOperator.RECENT_PATH = os.path.split(filename)[0]

            if filename.endswith(".complex"):
                self.add_signalfile(filename, group_id, enforce_sample_rate=enforce_sample_rate)
            elif filename.endswith(".coco"):
                self.add_signalfile(filename, group_id, enforce_sample_rate=enforce_sample_rate)
            elif filename.endswith(".proto") or filename.endswith(".proto.xml") or filename.endswith(".bin"):
                self.add_protocol_file(filename)
            elif filename.endswith(".wav"):
                try:
                    import wave
                    w = wave.open(filename)
                    w.close()
                except wave.Error as e:
                    Errors.generic_error("Unsupported WAV type", "Only uncompressed WAVs (PCM) are supported.", str(e))
                    continue
                self.add_signalfile(filename, group_id, enforce_sample_rate=enforce_sample_rate)
            elif filename.endswith(".fuzz") or filename.endswith(".fuzz.xml"):
                self.add_fuzz_profile(filename)
            elif filename.endswith(".sim") or filename.endswith(".sim.xml"):
                self.add_simulator_profile(filename)
            elif filename.endswith(".txt"):
                self.add_plain_bits_from_txt(filename)
            elif filename.endswith(".csv"):
                self.__import_csv(filename, group_id)
                continue
            elif os.path.basename(filename) == constants.PROJECT_FILE:
                self.project_manager.set_project_folder(os.path.split(filename)[0])
            else:
                self.add_signalfile(filename, group_id, enforce_sample_rate=enforce_sample_rate)

            if self.project_manager.project_file is None:
                self.adjust_for_current_file(filename)

            self.refresh_main_menu()

    def set_frame_numbers(self):
        self.signal_tab_controller.set_frame_numbers()

    def closeEvent(self, event: QCloseEvent):
        self.save_project()
        super().closeEvent(event)

    def close_all(self):

        self.filemodel.setRootPath(QDir.homePath())
        self.ui.fileTree.setRootIndex(self.file_proxy_model.mapFromSource(self.filemodel.index(QDir.homePath())))
        self.save_project()

        self.signal_tab_controller.close_all()
        self.compare_frame_controller.reset()
        self.generator_tab_controller.table_model.protocol.clear()
        self.generator_tab_controller.refresh_tree()
        self.generator_tab_controller.refresh_table()
        self.generator_tab_controller.refresh_label_list()

        self.project_manager.project_path = ""
        self.project_manager.project_file = None
        self.signal_tab_controller.signal_undo_stack.clear()
        self.compare_frame_controller.protocol_undo_stack.clear()
        self.generator_tab_controller.generator_undo_stack.clear()

        self.simulator_tab_controller.close_all()

    def show_options_dialog_specific_tab(self, tab_index: int):
        op = OptionsDialog(self.plugin_manager.installed_plugins, parent=self)
        op.values_changed.connect(self.on_options_changed)
        op.ui.tabWidget.setCurrentIndex(tab_index)
        op.show()

    def refresh_main_menu(self):
        enable = len(self.signal_protocol_dict) > 0
        self.ui.actionSaveAllSignals.setEnabled(enable)
        self.ui.actionClose_all.setEnabled(enable)

    def apply_default_view(self, view_index: int):
        self.compare_frame_controller.ui.cbProtoView.setCurrentIndex(view_index)
        self.generator_tab_controller.ui.cbViewType.setCurrentIndex(view_index)
        self.simulator_tab_controller.ui.cbViewType.setCurrentIndex(view_index)
        for sig_frame in self.signal_tab_controller.signal_frames:
            sig_frame.ui.cbProtoView.setCurrentIndex(view_index)

    def show_project_settings(self):
        pdc = ProjectDialog(new_project=False, project_manager=self.project_manager, parent=self)
        pdc.finished.connect(self.on_project_dialog_finished)
        pdc.show()

    def collapse_project_tab_bar(self):
        self.ui.tabParticipants.hide()
        self.ui.tabDescription.hide()
        self.ui.tabWidget_Project.setMaximumHeight(self.ui.tabWidget_Project.tabBar().height())

    def expand_project_tab_bar(self):
        self.ui.tabDescription.show()
        self.ui.tabParticipants.show()
        self.ui.tabWidget_Project.setMaximumHeight(9000)

    def save_project(self):
        self.project_manager.save_project(simulator_config=self.simulator_tab_controller.simulator_config)

    @pyqtSlot()
    def on_project_tab_bar_double_clicked(self):
        if self.ui.tabParticipants.isVisible():
            self.collapse_project_tab_bar()
        else:
            self.expand_project_tab_bar()

    @pyqtSlot()
    def on_project_updated(self):
        self.participant_legend_model.update()
        self.compare_frame_controller.refresh()
        self.ui.textEditProjectDescription.setText(self.project_manager.description)

    @pyqtSlot()
    def on_fullscreen_action_triggered(self):
        if self.ui.actionFullscreen_mode.isChecked():
            self.showFullScreen()
        else:
            self.showMaximized()

    def adjust_for_current_file(self, file_path):
        if file_path is None:
            return

        if file_path in FileOperator.archives.keys():
            file_path = copy.copy(FileOperator.archives[file_path])

        settings = constants.SETTINGS
        recent_file_paths = settings.value("recentFiles", [])
        recent_file_paths = [] if recent_file_paths is None else recent_file_paths  # check None for OSX
        recent_file_paths = [p for p in recent_file_paths if p != file_path and p is not None and os.path.exists(p)]
        recent_file_paths.insert(0, file_path)
        recent_file_paths = recent_file_paths[:constants.MAX_RECENT_FILE_NR]

        self.init_recent_file_action_list(recent_file_paths)

        settings.setValue("recentFiles", recent_file_paths)

    def init_recent_file_action_list(self, recent_file_paths: list):
        for i in range(len(self.recentFileActionList)):
            self.recentFileActionList[i].setVisible(False)

        if recent_file_paths is None:
            return

        for i, file_path in enumerate(recent_file_paths):
            if os.path.isfile(file_path):
                display_text = os.path.basename(file_path)
                self.recentFileActionList[i].setIcon(QIcon())
            elif os.path.isdir(file_path):
                head, tail = os.path.split(file_path)
                display_text = tail
                head, tail = os.path.split(head)
                if tail:
                    display_text = tail + "/" + display_text

                self.recentFileActionList[i].setIcon(QIcon.fromTheme("folder"))
            else:
                continue

            self.recentFileActionList[i].setText(display_text)
            self.recentFileActionList[i].setData(file_path)
            self.recentFileActionList[i].setVisible(True)

    @pyqtSlot()
    def on_show_field_types_config_action_triggered(self):
        self.show_options_dialog_specific_tab(tab_index=2)

    @pyqtSlot()
    def on_open_recent_action_triggered(self):
        action = self.sender()
        try:
            if os.path.isdir(action.data()):
                self.project_manager.set_project_folder(action.data())
            elif os.path.isfile(action.data()):
                self.setCursor(Qt.WaitCursor)
                self.add_files(FileOperator.uncompress_archives([action.data()], QDir.tempPath()))
                self.unsetCursor()
        except Exception as e:
            Errors.generic_error(self.tr("Failed to open"), str(e), traceback.format_exc())
            self.unsetCursor()

    @pyqtSlot()
    def on_show_about_clicked(self):
        descr = "<b><h2>Universal Radio Hacker</h2></b>Version: {0}<br />" \
                "GitHub: <a href='https://github.com/jopohl/urh'>https://github.com/jopohl/urh</a><br /><br />" \
                "Creators:<i><ul><li>" \
                "Johannes Pohl &lt;<a href='mailto:joahnnes.pohl90@gmail.com'>johannes.pohl90@gmail.com</a>&gt;</li>" \
                "<li>Andreas Noack &lt;<a href='mailto:andreas.noack@hochschule-stralsund.de'>andreas.noack@hochschule-stralsund.de</a>&gt;</li>" \
                "</ul></i>".format(version.VERSION)

        QMessageBox.about(self, self.tr("About"), self.tr(descr))

    @pyqtSlot(int, int, int, int)
    def show_protocol_selection_in_interpretation(self, start_message, start, end_message, end):
        try:
            cfc = self.compare_frame_controller
            msg_total = 0
            last_sig_frame = None
            for protocol in cfc.protocol_list:
                if not protocol.show:
                    continue
                n = protocol.num_messages
                view_type = cfc.ui.cbProtoView.currentIndex()
                messages = [i - msg_total for i in range(msg_total, msg_total + n) if start_message <= i <= end_message]
                if len(messages) > 0:
                    try:
                        signal_frame = next((sf for sf, pf in self.signal_protocol_dict.items() if pf == protocol))
                    except StopIteration:
                        QMessageBox.critical(self, self.tr("Error"),
                                             self.tr("Could not find corresponding signal frame."))
                        return
                    signal_frame.set_roi_from_protocol_analysis(min(messages), start, max(messages), end + 1, view_type)
                    last_sig_frame = signal_frame
                msg_total += n
            focus_frame = last_sig_frame
            if last_sig_frame is not None:
                self.signal_tab_controller.ui.scrollArea.ensureWidgetVisible(last_sig_frame, 0, 0)

            QApplication.instance().processEvents()
            self.ui.tabWidget.setCurrentIndex(0)
            if focus_frame is not None:
                focus_frame.ui.txtEdProto.setFocus()
        except Exception as e:
            logger.exception(e)

    @pyqtSlot(str)
    def on_file_tree_filter_text_changed(self, text: str):
        if len(text) > 0:
            self.filemodel.setNameFilters(["*" + text + "*"])
        else:
            self.filemodel.setNameFilters(["*"])

    @pyqtSlot()
    def on_show_decoding_dialog_triggered(self):
        signals = [sf.signal for sf in self.signal_tab_controller.signal_frames]
        decoding_controller = DecoderDialog(
            self.compare_frame_controller.decodings, signals,
            self.project_manager, parent=self)
        decoding_controller.finished.connect(self.update_decodings)
        decoding_controller.show()
        decoding_controller.decoder_update()

    @pyqtSlot()
    def update_decodings(self):
        self.project_manager.load_decodings()
        self.compare_frame_controller.fill_decoding_combobox()
        self.compare_frame_controller.refresh_existing_encodings()

        self.generator_tab_controller.refresh_existing_encodings(self.compare_frame_controller.decodings)

    @pyqtSlot(int)
    def on_selected_tab_changed(self, index: int):
        if index == 0:
            self.undo_group.setActiveStack(self.signal_tab_controller.signal_undo_stack)
        elif index == 1:
            self.undo_group.setActiveStack(self.compare_frame_controller.protocol_undo_stack)
            self.compare_frame_controller.ui.tblViewProtocol.resize_columns()
            self.compare_frame_controller.ui.tblViewProtocol.resize_vertical_header()
            h = max(self.compare_frame_controller.ui.btnSaveProto.height(),
                    self.generator_tab_controller.ui.btnSave.height())
            self.compare_frame_controller.ui.btnSaveProto.setMinimumHeight(h)

            th = self.compare_frame_controller.ui.tabWidget.tabBar().height()
            for i in range(self.compare_frame_controller.ui.tabWidget.count()):
                self.compare_frame_controller.ui.tabWidget.widget(i).layout().setContentsMargins(0, 7 + h - th, 0, 0)

        elif index == 2:
            self.undo_group.setActiveStack(self.generator_tab_controller.generator_undo_stack)
            h = max(self.compare_frame_controller.ui.btnSaveProto.height(),
                    self.generator_tab_controller.ui.btnSave.height())
            self.generator_tab_controller.ui.btnSave.setMinimumHeight(h)
            th = self.generator_tab_controller.ui.tabWidget.tabBar().height()
            for i in range(self.generator_tab_controller.ui.tabWidget.count()):
                self.generator_tab_controller.ui.tabWidget.widget(i).layout().setContentsMargins(0, 7 + h - th, 0, 0)
            # Modulators may got changed from Simulator Dialog
            self.generator_tab_controller.refresh_modulators()

    @pyqtSlot()
    def on_show_record_dialog_action_triggered(self):
        pm = self.project_manager
        try:
            r = ReceiveDialog(pm, parent=self)
        except OSError as e:
            logger.error(repr(e))
            return

        if r.has_empty_device_list:
            Errors.no_device()
            r.close()
            return

        r.device_parameters_changed.connect(pm.set_device_parameters)
        r.files_recorded.connect(self.on_signals_recorded)
        r.show()

    def create_protocol_sniff_dialog(self, testing_mode=False):
        pm = self.project_manager
        signal = next((proto.signal for proto in self.compare_frame_controller.protocol_list), None)
        signals = [f.signal for f in self.signal_tab_controller.signal_frames if f.signal]

        psd = ProtocolSniffDialog(project_manager=pm, signal=signal, signals=signals,
                                  testing_mode=testing_mode, parent=self)

        if psd.has_empty_device_list:
            Errors.no_device()
            psd.close()
            return None
        else:
            psd.device_parameters_changed.connect(pm.set_device_parameters)
            psd.protocol_accepted.connect(self.compare_frame_controller.add_sniffed_protocol_messages)
            return psd

    @pyqtSlot()
    def show_proto_sniff_dialog(self):
        psd = self.create_protocol_sniff_dialog()
        if psd:
            psd.show()

    @pyqtSlot()
    def on_show_spectrum_dialog_action_triggered(self):
        pm = self.project_manager
        r = SpectrumDialogController(pm, parent=self)
        if r.has_empty_device_list:
            Errors.no_device()
            r.close()
            return

        r.device_parameters_changed.connect(pm.set_device_parameters)
        r.show()

    @pyqtSlot(list, float)
    def on_signals_recorded(self, file_names: list, sample_rate: float):
        QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        for filename in file_names:
            self.add_signalfile(filename, enforce_sample_rate=sample_rate)
        QApplication.instance().restoreOverrideCursor()

    @pyqtSlot()
    def show_options_dialog_action_triggered(self):
        self.show_options_dialog_specific_tab(tab_index=4)

    @pyqtSlot()
    def on_new_project_action_triggered(self):
        pdc = ProjectDialog(parent=self)
        try:
            path = os.path.dirname(self.signal_tab_controller.signal_frames[0].signal.filename)
        except (IndexError, AttributeError, TypeError):
            path = None

        if path:
            pdc.set_path(path)
        pdc.finished.connect(self.on_project_dialog_finished)
        pdc.show()

    @pyqtSlot()
    def on_project_settings_action_triggered(self):
        self.show_project_settings()

    @pyqtSlot()
    def on_edit_menu_about_to_show(self):
        self.ui.actionShowFileTree.setChecked(self.ui.splitter.sizes()[0] > 0)

    @pyqtSlot()
    def on_action_show_filetree_triggered(self):
        if self.ui.splitter.sizes()[0] > 0:
            self.ui.splitter.setSizes([0, 1])
        else:
            self.ui.splitter.setSizes([1, 1])

    @pyqtSlot()
    def on_project_dialog_finished(self):
        if self.sender().committed:
            self.project_manager.from_dialog(self.sender())

    @pyqtSlot()
    def on_open_file_action_triggered(self):
        self.show_open_dialog(directory=False)

    @pyqtSlot()
    def on_open_directory_action_triggered(self):
        self.show_open_dialog(directory=True)

    def show_open_dialog(self, directory=False):
        dialog = FileOperator.get_open_dialog(directory_mode=directory, parent=self, name_filter="full")
        if dialog.exec_():
            try:
                file_names = dialog.selectedFiles()
                folders = [folder for folder in file_names if os.path.isdir(folder)]

                if len(folders) > 0:
                    folder = folders[0]
                    for f in self.signal_tab_controller.signal_frames:
                        self.close_signal_frame(f)

                    self.project_manager.set_project_folder(folder)
                else:
                    self.setCursor(Qt.WaitCursor)
                    file_names = FileOperator.uncompress_archives(file_names, QDir.tempPath())
                    self.add_files(file_names)
                    self.unsetCursor()
            except Exception as e:
                Errors.generic_error(self.tr("Failed to open"), str(e), traceback.format_exc())
                self.unsetCursor()

    @pyqtSlot()
    def on_close_all_action_triggered(self):
        self.close_all()

    @pyqtSlot(list)
    def on_files_dropped(self, files):
        """
        :type files: list of QtCore.QUrl
        """
        self.__add_urls_to_group(files, group_id=0)

    @pyqtSlot(list, int)
    def on_files_dropped_on_group(self, files, group_id: int):
        """
        :param group_id:
        :type files: list of QtCore.QUrl
        """
        self.__add_urls_to_group(files, group_id=group_id)

    def __add_urls_to_group(self, file_urls, group_id=0):
        local_files = [file_url.toLocalFile() for file_url in file_urls if file_url.isLocalFile()]
        if len(local_files) > 0:
            self.setCursor(Qt.WaitCursor)
            self.add_files(FileOperator.uncompress_archives(local_files, QDir.tempPath()), group_id=group_id)
            self.unsetCursor()

    @pyqtSlot(list)
    def on_cfc_close_wanted(self, protocols: list):
        frame_protos = {sframe: protocol for sframe, protocol in self.signal_protocol_dict.items() if
                        protocol in protocols}

        for frame in frame_protos:
            self.close_signal_frame(frame)

        for proto in (proto for proto in protocols if proto not in frame_protos.values()):
            # close protocols without associated signal frame
            self.close_protocol(proto)

    @pyqtSlot(dict)
    def on_options_changed(self, changed_options: dict):
        refresh_protocol_needed = "show_pause_as_time" in changed_options

        if refresh_protocol_needed:
            for sf in self.signal_tab_controller.signal_frames:
                sf.refresh_protocol()

        self.project_manager.reload_field_types()

        self.compare_frame_controller.refresh_field_types_for_labels()
        self.compare_frame_controller.set_shown_protocols()
        self.generator_tab_controller.set_network_sdr_send_button_visibility()
        self.generator_tab_controller.init_rfcat_plugin()
        self.generator_tab_controller.set_modulation_profile_status()
        self.simulator_tab_controller.refresh_field_types_for_labels()

        if "num_sending_repeats" in changed_options:
            self.project_manager.device_conf["num_sending_repeats"] = changed_options["num_sending_repeats"]

        if "default_view" in changed_options:
            self.apply_default_view(int(changed_options["default_view"]))

        if "spectrogram_colormap" in changed_options:
            self.signal_tab_controller.redraw_spectrograms()

    @pyqtSlot()
    def on_text_edit_project_description_text_changed(self):
        self.project_manager.description = self.ui.textEditProjectDescription.toPlainText()

    @pyqtSlot()
    def on_btn_file_tree_go_up_clicked(self):
        cur_dir = self.filemodel.rootDirectory()
        if cur_dir.cdUp():
            path = cur_dir.path()
            self.filemodel.setRootPath(path)
            self.ui.fileTree.setRootIndex(self.file_proxy_model.mapFromSource(self.filemodel.index(path)))

    @pyqtSlot(int, Signal)
    def on_signal_created(self, index: int, signal: Signal):
        self.add_signal(signal, index=index)

    @pyqtSlot()
    def on_cancel_triggered(self):
        for signal_frame in self.signal_tab_controller.signal_frames:
            signal_frame.cancel_filtering()

    @pyqtSlot()
    def on_import_samples_from_csv_action_triggered(self):
        self.__import_csv(file_name="")

    def __import_csv(self, file_name, group_id=0):
        def on_data_imported(complex_file, sample_rate):
            sample_rate = None if sample_rate == 0 else sample_rate
            self.add_files([complex_file], group_id=group_id, enforce_sample_rate=sample_rate)

        dialog = CSVImportDialog(file_name, parent=self)
        dialog.data_imported.connect(on_data_imported)
        dialog.exec_()

    @pyqtSlot(str)
    def on_label_non_project_mode_link_activated(self, link: str):
        if link == "dont_show_non_project_again":
            self.ui.labelNonProjectMode.hide()
            constants.SETTINGS.setValue("show_non_project_warning", False)
        elif link == "open_new_project_dialog":
            self.on_new_project_action_triggered()

    @pyqtSlot(bool)
    def on_project_loaded_status_changed(self, project_loaded: bool):
        self.ui.actionProject_settings.setVisible(project_loaded)
        self.ui.actionSave_project.setVisible(project_loaded)
        self.ui.actionConvert_Folder_to_Project.setDisabled(project_loaded)
        self.__set_non_project_warning_visibility()

    @pyqtSlot()
    def on_compare_frame_controller_load_protocol_clicked(self):
        dialog = FileOperator.get_open_dialog(directory_mode=False, parent=self, name_filter="proto")
        if dialog.exec_():
            for filename in dialog.selectedFiles():
                self.add_protocol_file(filename)

    @pyqtSlot(str)
    def on_simulator_open_in_analysis_requested(self, text: str):
        protocol = ProtocolAnalyzer.get_protocol_from_string(text.split("\n"))
        protocol.name = "Transcript"

        self.ui.tabWidget.setCurrentIndex(1)
        self.compare_frame_controller.add_protocol(protocol)
        self.compare_frame_controller.refresh()
