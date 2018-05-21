from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QAction, QActionGroup, QMenu, QUndoStack

from urh.plugins.InsertSine.InsertSinePlugin import InsertSinePlugin
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.Signal import Signal
from urh.ui.actions.EditSignalAction import EditSignalAction, EditAction
from urh.ui.painting.HorizontalSelection import HorizontalSelection
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView


class EditableGraphicView(ZoomableGraphicView):
    save_as_clicked = pyqtSignal()
    export_demodulated_clicked = pyqtSignal()
    create_clicked = pyqtSignal(int, int)
    set_noise_clicked = pyqtSignal()
    participant_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.participants = []
        self.__sample_rate = None  # For default sample rate in insert sine dialog
        self.protocol = None  # gets overwritten in epic graphic view

        self.autoRangeY = True
        self.save_enabled = False  # Signal is can be saved
        self.create_new_signal_enabled = False
        self.participants_assign_enabled = False
        self.cache_qad = False  # cache qad demod after edit operations?

        self.__signal = None  # type: Signal

        self.stored_item = None  # For copy/paste
        self.paste_position = 0  # Where to paste? Set in contextmenuevent

        self.init_undo_stack(QUndoStack())

        self.addAction(self.undo_action)
        self.addAction(self.redo_action)

        self.copy_action = QAction(self.tr("Copy selection"), self)  # type: QAction
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.on_copy_action_triggered)
        self.copy_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.copy_action.setIcon(QIcon.fromTheme("edit-copy"))
        self.addAction(self.copy_action)

        self.paste_action = QAction(self.tr("Paste"), self)  # type: QAction
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.triggered.connect(self.on_paste_action_triggered)
        self.paste_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.paste_action.setIcon(QIcon.fromTheme("edit-paste"))
        self.addAction(self.paste_action)

        self.delete_action = QAction(self.tr("Delete selection"), self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.triggered.connect(self.on_delete_action_triggered)
        self.delete_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.delete_action.setIcon(QIcon.fromTheme("edit-delete"))
        self.addAction(self.delete_action)

        self.save_as_action = QAction(self.tr("Save Signal as..."), self)  # type: QAction
        self.save_as_action.setIcon(QIcon.fromTheme("document-save-as"))
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.triggered.connect(self.save_as_clicked.emit)
        self.save_as_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.save_as_action)

        self.insert_sine_action = QAction(self.tr("Insert sine wave..."), self)
        font = self.insert_sine_action.font()
        font.setBold(True)
        self.insert_sine_action.setFont(font)
        self.insert_sine_action.triggered.connect(self.on_insert_sine_action_triggered)

        self.insert_sine_plugin = InsertSinePlugin()
        self.insert_sine_plugin.insert_sine_wave_clicked.connect(self.on_insert_sine_wave_clicked)

    def init_undo_stack(self, undo_stack):
        self.undo_stack = undo_stack

        self.undo_action = self.undo_stack.createUndoAction(self)
        self.undo_action.setIcon(QIcon.fromTheme("edit-undo"))
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)

        self.redo_action = self.undo_stack.createRedoAction(self)
        self.redo_action.setIcon(QIcon.fromTheme("edit-redo"))
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)

        self.undo_stack.indexChanged.connect(self.on_undo_stack_index_changed)

    def eliminate(self):
        self.participants = None
        self.stored_item = None
        if self.signal is not None:
            self.signal.eliminate()
        self.__signal = None
        self.insert_sine_plugin = None
        self.undo_action = None
        self.redo_action = None
        self.undo_stack = None
        super().eliminate()

    @property
    def sample_rate(self) -> float:
        return self.__sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        self.__sample_rate = value

    @property
    def signal(self) -> Signal:
        return self.__signal

    @property
    def selection_area(self) -> HorizontalSelection:
        return self.scene().selection_area

    @selection_area.setter
    def selection_area(self, value):
        self.scene().selection_area = value

    def set_signal(self, signal: Signal):
        self.__signal = signal

    def create_context_menu(self):
        self.paste_position = int(self.mapToScene(self.context_menu_position).x())

        menu = QMenu(self)
        menu.addAction(self.copy_action)
        self.copy_action.setEnabled(self.something_is_selected)
        menu.addAction(self.paste_action)
        self.paste_action.setEnabled(self.stored_item is not None)

        menu.addSeparator()
        if PluginManager().is_plugin_enabled("InsertSine"):
            menu.addAction(self.insert_sine_action)

        self._add_zoom_actions_to_menu(menu)

        if self.something_is_selected:
            menu.addAction(self.delete_action)
            crop_action = menu.addAction(self.tr("Crop to selection"))
            crop_action.triggered.connect(self.on_crop_action_triggered)
            mute_action = menu.addAction(self.tr("Mute selection"))
            mute_action.triggered.connect(self.on_mute_action_triggered)

            if self.create_new_signal_enabled:
                create_action = menu.addAction(self.tr("Create signal from selection"))
                create_action.setIcon(QIcon.fromTheme("document-new"))
                create_action.triggered.connect(self.on_create_action_triggered)

            menu.addSeparator()

        if hasattr(self, "selected_messages"):
            selected_messages = self.selected_messages
        else:
            selected_messages = []

        if len(selected_messages) == 1:
            selected_msg = selected_messages[0]
        else:
            selected_msg = None

        self.participant_actions = {}

        if len(selected_messages) > 0 and self.participants_assign_enabled:
            participant_group = QActionGroup(self)
            participant_menu = menu.addMenu("Participant")
            none_participant_action = participant_menu.addAction("None")
            none_participant_action.setCheckable(True)
            none_participant_action.setActionGroup(participant_group)
            none_participant_action.triggered.connect(self.on_none_participant_action_triggered)

            if selected_msg and selected_msg.participant is None:
                none_participant_action.setChecked(True)

            for participant in self.participants:
                pa = participant_menu.addAction(participant.name + " (" + participant.shortname + ")")
                pa.setCheckable(True)
                pa.setActionGroup(participant_group)
                if selected_msg and selected_msg.participant == participant:
                    pa.setChecked(True)

                self.participant_actions[pa] = participant
                pa.triggered.connect(self.on_participant_action_triggered)

        if self.scene_type == 0 and self.something_is_selected:
            menu.addSeparator()
            noise_action = menu.addAction(self.tr("Set noise level from Selection"))
            noise_action.triggered.connect(self.on_noise_action_triggered)

        menu.addSeparator()
        menu.addAction(self.undo_action)
        menu.addAction(self.redo_action)

        if self.scene_type == 0:
            menu.addSeparator()
            if self.save_enabled:
                menu.addAction(self.save_action)

            menu.addAction(self.save_as_action)
        elif self.scene_type == 1:
            menu.addSeparator()
            export_demod_action = menu.addAction("Export demodulated...")
            export_demod_action.triggered.connect(self.export_demodulated_clicked.emit)

        return menu

    def clear_horizontal_selection(self):
        self.set_horizontal_selection(0, 0)

    @pyqtSlot()
    def on_insert_sine_action_triggered(self):
        if self.something_is_selected:
            num_samples = self.selection_area.width
        else:
            num_samples = None

        original_data = self.signal.data if self.signal is not None else None
        dialog = self.insert_sine_plugin.get_insert_sine_dialog(original_data=original_data,
                                                                position=self.paste_position,
                                                                sample_rate=self.sample_rate,
                                                                num_samples=num_samples)
        dialog.show()

    @pyqtSlot()
    def on_insert_sine_wave_clicked(self):
        if self.insert_sine_plugin.complex_wave is not None:
            self.clear_horizontal_selection()
            insert_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                             data_to_insert=self.insert_sine_plugin.complex_wave,
                                             position=self.paste_position,
                                             mode=EditAction.insert, cache_qad=self.cache_qad)
            self.undo_stack.push(insert_action)

    @pyqtSlot()
    def on_copy_action_triggered(self):
        if self.something_is_selected:
            self.stored_item = self.signal._fulldata[int(self.selection_area.start):int(self.selection_area.end)]

    @pyqtSlot()
    def on_paste_action_triggered(self):
        if self.stored_item is not None:
            # paste_position is set in ContextMenuEvent
            self.clear_horizontal_selection()
            paste_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                            start=self.selection_area.start, end=self.selection_area.end,
                                            data_to_insert=self.stored_item, position=self.paste_position,
                                            mode=EditAction.paste, cache_qad=self.cache_qad)
            self.undo_stack.push(paste_action)

    @pyqtSlot()
    def on_delete_action_triggered(self):
        if self.something_is_selected:
            start, end = self.selection_area.start, self.selection_area.end
            self.clear_horizontal_selection()
            del_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                          start=start, end=end,
                                          mode=EditAction.delete, cache_qad=self.cache_qad)
            self.undo_stack.push(del_action)

    @pyqtSlot()
    def on_crop_action_triggered(self):
        if self.something_is_selected:
            start, end = self.selection_area.start, self.selection_area.end
            self.clear_horizontal_selection()
            crop_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                           start=start, end=end,
                                           mode=EditAction.crop, cache_qad=self.cache_qad)
            self.undo_stack.push(crop_action)

    @pyqtSlot()
    def on_mute_action_triggered(self):
        mute_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                       start=self.selection_area.start, end=self.selection_area.end,
                                       mode=EditAction.mute, cache_qad=self.cache_qad)
        self.undo_stack.push(mute_action)

    @pyqtSlot()
    def on_create_action_triggered(self):
        self.create_clicked.emit(self.selection_area.start, self.selection_area.end)

    @pyqtSlot()
    def on_none_participant_action_triggered(self):
        for msg in self.selected_messages:
            msg.participant = None
        self.participant_changed.emit()

    @pyqtSlot()
    def on_participant_action_triggered(self):
        for msg in self.selected_messages:
            msg.participant = self.participant_actions[self.sender()]
        self.participant_changed.emit()

    @pyqtSlot()
    def on_noise_action_triggered(self):
        self.set_noise_clicked.emit()

    @pyqtSlot(int)
    def on_undo_stack_index_changed(self, index: int):
        view_width, scene_width = self.view_rect().width(), self.sceneRect().width()
        if view_width > scene_width:
            self.show_full_scene(reinitialize=True)
