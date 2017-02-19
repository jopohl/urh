from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QSize, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtGui import QCursor, QKeyEvent, QKeySequence, QPainter, QPen, QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QActionGroup
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QUndoStack

from urh import constants
from urh.plugins.InsertSine.InsertSinePlugin import InsertSinePlugin
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.ui.ROI import ROI
from urh.ui.actions.EditSignalAction import EditSignalAction, EditAction
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView


class EditableGraphicView(ZoomableGraphicView):
    ctrl_state_changed = pyqtSignal(bool)
    save_as_clicked = pyqtSignal()
    create_clicked = pyqtSignal(int, int)
    set_noise_clicked = pyqtSignal()
    participant_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.participants = []
        self.__sample_rate = None   # For default sample rate in insert sine dialog

        self.autoRangeY = True
        self.save_enabled = False  # Signal is can be saved
        self.create_new_signal_enabled = False
        self.participants_assign_enabled = False
        self.cache_qad = False  # cache qad demod after edit operations?

        self.__signal = None  # type: Signal

        self.stored_item = None  # For copy/paste
        self.paste_position = 0  # Where to paste? Set in contextmenuevent
        self.context_menu_position = None  # type: QPoint

        self._init_undo_stack(QUndoStack())

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

    def _init_undo_stack(self, undo_stack):
        self.undo_stack = undo_stack

        self.undo_action = self.undo_stack.createUndoAction(self)
        self.undo_action.setIcon(QIcon.fromTheme("edit-undo"))
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)

        self.redo_action = self.undo_stack.createRedoAction(self)
        self.redo_action.setIcon(QIcon.fromTheme("edit-redo"))
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)

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
    def protocol(self) -> ProtocolAnalyzer:
        return None  # Gets overwritten in EpicGraphicView

    @property
    def selection_area(self) -> ROI:
        return self.scene().selection_area

    @selection_area.setter
    def selection_area(self, value):
        self.scene().selection_area = value

    def set_signal(self, signal: Signal):
        self.__signal = signal

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        super().keyPressEvent(event)

        if key == Qt.Key_Control and not self.shift_mode:
            self.set_zoom_cursor()
            self.ctrl_mode = True
            self.ctrl_state_changed.emit(True)

        if self.ctrl_mode and (key == Qt.Key_Plus or key == Qt.Key_Up):
            self.zoom(1.1)
        elif self.ctrl_mode and (key == Qt.Key_Minus or key == Qt.Key_Down):
            self.zoom(0.9)
        elif self.ctrl_mode and key == Qt.Key_Right:
            cur_val = self.horizontalScrollBar().value()
            step = self.horizontalScrollBar().pageStep()
            self.horizontalScrollBar().setValue(cur_val + step)
        elif key == Qt.Key_Right:
            cur_val = self.horizontalScrollBar().value()
            step = self.horizontalScrollBar().singleStep()
            self.horizontalScrollBar().setValue(cur_val + step)

        elif self.ctrl_mode and key == Qt.Key_Left:
            cur_val = self.horizontalScrollBar().value()
            step = self.horizontalScrollBar().pageStep()
            self.horizontalScrollBar().setValue(cur_val - step)

        elif key == Qt.Key_Left:
            cur_val = self.horizontalScrollBar().value()
            step = self.horizontalScrollBar().singleStep()
            self.horizontalScrollBar().setValue(cur_val - step)

    def keyReleaseEvent(self, event: QKeyEvent):
        super().keyReleaseEvent(event)
        if event.key() == Qt.Key_Control:
            self.ctrl_mode = False
            self.ctrl_state_changed.emit(False)
            self.unsetCursor()

    def create_context_menu(self):
        self.paste_position = int(self.mapToScene(self.context_menu_position).x())

        menu = QMenu(self)
        if self.save_enabled:
            menu.addAction(self.save_action)

        menu.addAction(self.save_as_action)
        menu.addSeparator()

        menu.addAction(self.copy_action)
        self.copy_action.setEnabled(not self.selection_area.is_empty)
        menu.addAction(self.paste_action)
        self.paste_action.setEnabled(self.stored_item is not None)

        menu.addSeparator()
        if PluginManager().is_plugin_enabled("InsertSine"):
            menu.addAction(self.insert_sine_action)
            if not self.selection_area.is_empty:
                menu.addSeparator()

        if not self.selection_area.is_empty:
            menu.addAction(self.delete_action)
            crop_action = menu.addAction(self.tr("Crop to selection"))
            crop_action.triggered.connect(self.on_crop_action_triggered)
            mute_action = menu.addAction(self.tr("Mute selection"))
            mute_action.triggered.connect(self.on_mute_action_triggered)

            menu.addSeparator()
            zoom_action = menu.addAction(self.tr("Zoom selection"))
            zoom_action.setIcon(QIcon.fromTheme("zoom-in"))
            zoom_action.triggered.connect(self.on_zoom_action_triggered)
            if self.create_new_signal_enabled:
                create_action = menu.addAction(self.tr("Create signal from selection"))
                create_action.setIcon(QIcon.fromTheme("document-new"))
                create_action.triggered.connect(self.on_create_action_triggered)

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

                self.articipant_actions[pa] = participant
                pa.triggered.connect(self.on_participant_action_triggered)

        if hasattr(self, "scene_type") and self.scene_type == 0:
            if not self.selection_area.is_empty:
                menu.addSeparator()
                noise_action = menu.addAction(self.tr("Set noise level from Selection"))
                noise_action.triggered.connect(self.on_noise_action_triggered)

        menu.addSeparator()
        menu.addAction(self.undo_action)
        menu.addAction(self.redo_action)

        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self.ctrl_mode:
            return
        self.context_menu_position = event.pos()
        menu = self.create_context_menu()
        menu.exec_(self.mapToGlobal(event.pos()))
        self.context_menu_position = None

    def clear_selection(self):
        self.set_selection_area(0, 0)

    def set_zoom_cursor(self):
        self.setCursor(QCursor(QIcon.fromTheme("zoom-in").pixmap(16, 16)))

    @pyqtSlot()
    def on_insert_sine_action_triggered(self):
        if not self.selection_area.is_empty:
            num_samples = self.selection_area.width
        else:
            num_samples = None

        self.insert_sine_plugin.show_insert_sine_dialog(sample_rate=self.sample_rate, num_samples=num_samples)

    @pyqtSlot()
    def on_insert_sine_wave_clicked(self):
        if self.insert_sine_plugin.complex_wave is not None:
            self.clear_selection()
            insert_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                             data_to_insert=self.insert_sine_plugin.complex_wave,
                                             position=self.paste_position,
                                             mode=EditAction.insert, cache_qad=self.cache_qad)
            self.undo_stack.push(insert_action)

    @pyqtSlot()
    def on_copy_action_triggered(self):
        if not self.selection_area.is_empty:
            self.stored_item = self.signal._fulldata[int(self.selection_area.start):int(self.selection_area.end)]

    @pyqtSlot()
    def on_paste_action_triggered(self):
        if self.stored_item is not None:
            # paste_position is set in ContextMenuEvent
            self.clear_selection()
            paste_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                            start=self.selection_area.start, end=self.selection_area.end,
                                            data_to_insert=self.stored_item, position=self.paste_position,
                                            mode=EditAction.paste, cache_qad=self.cache_qad)
            self.undo_stack.push(paste_action)

    @pyqtSlot()
    def on_delete_action_triggered(self):
        if not self.selection_area.is_empty:
            start, end = self.selection_area.start, self.selection_area.end
            self.clear_selection()
            del_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                          start=start, end=end,
                                          mode=EditAction.delete, cache_qad=self.cache_qad)
            self.undo_stack.push(del_action)
            self.centerOn(start, self.y_center)

    @pyqtSlot()
    def on_crop_action_triggered(self):
        if not self.selection_area.is_empty:
            crop_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                           start=self.selection_area.start, end=self.selection_area.end,
                                           mode=EditAction.crop, cache_qad=self.cache_qad)
            self.undo_stack.push(crop_action)

    @pyqtSlot()
    def on_mute_action_triggered(self):
        mute_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                       start=self.selection_area.start, end=self.selection_area.end,
                                       mode=EditAction.mute, cache_qad=self.cache_qad)
        self.undo_stack.push(mute_action)

    @pyqtSlot()
    def on_zoom_action_triggered(self):
        self.zoom_to_selection(self.selection_area.x, self.selection_area.end)

    @pyqtSlot()
    def on_create_action_triggered(self):
        self.create_clicked.emit(self.selection_area.x, self.selection_area.end)

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
