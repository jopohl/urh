from PyQt5.QtCore import QSize, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtGui import QCursor, QKeyEvent, QKeySequence, QMouseEvent, QPainter, QPen, QPixmap, QWheelEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QActionGroup
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QUndoGroup
from PyQt5.QtWidgets import QUndoStack

from urh import constants
from urh.plugins.InsertSine.InsertSinePlugin import InsertSinePlugin
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.ui.ROI import ROI
from urh.ui.actions.EditSignalAction import EditSignalAction, EditAction
from urh.ui.views.SelectableGraphicView import SelectableGraphicView


class EditableGraphicView(SelectableGraphicView):
    ctrl_state_changed = pyqtSignal(bool)
    save_as_clicked = pyqtSignal()
    zoomed = pyqtSignal()
    create_clicked = pyqtSignal(int, int)
    set_noise_clicked = pyqtSignal()
    participant_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.participants = []
        self.__sample_rate = None   # For default sample rate in insert sine dialog

        self.autoRangeY = True
        self.show_full_signal = True
        self.save_enabled = False  # Signal is can be saved
        self.create_new_signal_enabled = False
        self.participants_assign_enabled = False
        self.cache_qad = False  # cache qad demod after edit operations?

        self.__signal = None  # type: Signal

        self.stored_item = None  # For copy/paste
        self.paste_position = 0  # Where to paste? Set in contextmenuevent

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

    @property
    def y_center(self):
        if not hasattr(self, "scene_type") or self.scene_type == 0:
            # Normal scene
            return 0
        else:
            return -self.signal.qad_center

    def set_signal(self, signal: Signal):
        self.__signal = signal

    def zoom(self, factor, suppress_signal=False, event: QWheelEvent=None):
        self.show_full_signal = False
        if factor > 1 and self.view_rect().width() / factor < 300:
            factor = self.view_rect().width() / 300

        old_pos = self.mapToScene(event.pos()) if event else None

        self.scale(factor, 1)

        if self.view_rect().width() > self.sceneRect().width():
            self.draw_full_signal()

        if not suppress_signal:
            self.zoomed.emit()

        if event:
            move = self.mapToScene(event.pos()) - old_pos
            self.translate(move.x(), 0)
        else:
            self.centerOn(self.view_rect().x() + self.view_rect().width() / 2, self.y_center)

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.001 ** event.angleDelta().y()
        self.zoom(zoom_factor, event=event)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if self.ctrl_mode and event.buttons() == Qt.LeftButton:
            self.zoom(1.1)
        elif self.ctrl_mode and event.buttons() == Qt.RightButton:
            self.zoom(0.9)

    def resizeEvent(self, event):
        if self.view_rect().width() > self.sceneRect().width():
            x_factor = self.width() / self.sceneRect().width()
            self.scale(x_factor / self.transform().m11(), 1)

        self.autofit_view()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        self.show_full_signal = False

        super().keyPressEvent(event)

        if key == Qt.Key_Control and not self.shift_mode:
            self.set_loupe_cursor()
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

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self.ctrl_mode:
            return

        self.paste_position = int(self.mapToScene(event.pos()).x())

        menu = QMenu(self)
        if self.save_enabled:
            menu.addAction(self.save_action)

        menu.addAction(self.save_as_action)
        menu.addSeparator()

        zoom_action = None
        create_action = None
        noise_action = None
        crop_action = None
        mute_action = None

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
            mute_action = menu.addAction(self.tr("Mute selection"))

            menu.addSeparator()
            zoom_action = menu.addAction(self.tr("Zoom selection"))
            zoom_action.setIcon(QIcon.fromTheme("zoom-in"))
            if self.create_new_signal_enabled:
                create_action = menu.addAction(self.tr("Create signal from selection"))
                create_action.setIcon(QIcon.fromTheme("document-new"))

        if hasattr(self, "selected_messages"):
            selected_messages = self.selected_messages
        else:
            selected_messages = []

        if len(selected_messages) == 1:
            selected_msg = selected_messages[0]
        else:
            selected_msg = None

        participant_actions = {}

        if len(selected_messages) > 0 and self.participants_assign_enabled:
            participant_group = QActionGroup(self)
            participant_menu = menu.addMenu("Participant")
            none_participant_action = participant_menu.addAction("None")
            none_participant_action.setCheckable(True)
            none_participant_action.setActionGroup(participant_group)

            if selected_msg and selected_msg.participant is None:
                none_participant_action.setChecked(True)

            for participant in self.participants:
                pa = participant_menu.addAction(participant.name + " (" + participant.shortname + ")")
                pa.setCheckable(True)
                pa.setActionGroup(participant_group)
                if selected_msg and selected_msg.participant == participant:
                    pa.setChecked(True)

                participant_actions[pa] = participant
        else:
            none_participant_action = 42

        if hasattr(self, "scene_type") and self.scene_type == 0:
            if not self.selection_area.is_empty:
                menu.addSeparator()
                noise_action = menu.addAction(self.tr("Set noise level from Selection"))

        menu.addSeparator()
        menu.addAction(self.undo_action)
        menu.addAction(self.redo_action)

        QApplication.processEvents()  # without this the menu flickers on first create
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action is None:
            return
        elif action == zoom_action:
            self.zoom_to_selection(self.selection_area.x, self.selection_area.end)
        elif action == create_action:
            self.create_clicked.emit(self.selection_area.x, self.selection_area.end)
        elif action == crop_action:
            if not self.selection_area.is_empty:
                crop_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                               start=self.selection_area.start, end=self.selection_area.end,
                                               mode=EditAction.crop, cache_qad=self.cache_qad)
                self.undo_stack.push(crop_action)
        elif action == noise_action:
            self.set_noise_clicked.emit()
        elif action == mute_action:
            mute_action = EditSignalAction(signal=self.signal, protocol=self.protocol,
                                           start=self.selection_area.start, end=self.selection_area.end,
                                           mode=EditAction.mute, cache_qad=self.cache_qad)
            self.undo_stack.push(mute_action)
        elif action == none_participant_action:
            for msg in selected_messages:
                msg.participant = None
            self.participant_changed.emit()
        elif action in participant_actions:
            for msg in selected_messages:
                msg.participant = participant_actions[action]
            self.participant_changed.emit()

    def clear_selection(self):
        self.set_selection_area(0, 0)

    def draw_full_signal(self):
        y_factor = self.transform().m22()
        self.resetTransform()
        x_factor = self.width() / self.sceneRect().width()
        self.scale(x_factor, y_factor)
        self.centerOn(0, self.y_center)

    def set_loupe_cursor(self):
        pixmap = QPixmap(QSize(20, 20))
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setPen(QPen(constants.AXISCOLOR, 2))
        painter.Antialiasing = True
        painter.HighQualityAntialiasing = True

        painter.drawEllipse(0, 0, 10, 10)
        painter.drawLine(10, 10, 20, 20)
        del painter
        self.setCursor(QCursor(pixmap))

    def autofit_view(self):

        h_tar = self.sceneRect().height()
        h_view = self.view_rect().height()

        if abs(h_tar) > 0:
            self.scale(1, h_view / h_tar)
        self.centerOn(self.view_rect().x() + self.view_rect().width() / 2, self.y_center)

    def zoom_to_selection(self, start: int, end: int):
        if start == end:
            return

        x_factor = self.view_rect().width() / (end - start)
        self.zoom(x_factor)
        self.centerOn(start + (end - start) / 2, self.y_center)

    @pyqtSlot()
    def on_insert_sine_action_triggered(self):
        self.insert_sine_plugin.show_insert_sine_dialog(sample_rate=self.sample_rate)

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
