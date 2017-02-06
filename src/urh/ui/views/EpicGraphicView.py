from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QCursor, QPen, QPainter, QPixmap, QIcon, QKeySequence, \
    QContextMenuEvent, QWheelEvent
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication, QMenu, QActionGroup

from urh import constants
from urh.plugins.InsertSine.InsertSinePlugin import InsertSinePlugin
from urh.plugins.PluginManager import PluginManager
from urh.ui.ROI import ROI
from urh.ui.views.SelectableGraphicView import SelectableGraphicView


class EpicGraphicView(SelectableGraphicView):
    save_clicked = pyqtSignal()
    save_as_clicked = pyqtSignal()
    create_clicked = pyqtSignal(int, int)
    show_crop_range_clicked = pyqtSignal()
    crop_clicked = pyqtSignal()
    set_noise_clicked = pyqtSignal()
    zoomed = pyqtSignal()
    deletion_wanted = pyqtSignal(int, int)
    mute_wanted = pyqtSignal(int, int)
    ctrl_state_changed = pyqtSignal(bool)
    participant_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.autoRangeY = True
        self.show_full_signal = True
        self.nsamples = 0

        self.participants = []

        self.y_sep = 0
        self.is_locked = False

        self.stored_item = None  # For copy/paste
        self.paste_position = 0  # Where to paste? Set in contextmenuevent

        self.parent_frame = self.parent().parent().parent()

        self.save_action = QAction(self.tr("Save"), self)  # type: QAction
        self.save_action.setIcon(QIcon.fromTheme("document-save"))
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.on_save_action_triggered)
        self.save_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.save_action)

        self.save_as_action = QAction(self.tr("Save Signal as..."), self)  # type: QAction
        self.save_as_action.setIcon(QIcon.fromTheme("document-save-as"))
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.triggered.connect(self.on_save_as_action_triggered)
        self.save_as_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.save_as_action)

        self.copy_action = QAction(self.tr("Copy selection"), self)  # type: QAction
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.on_copy_action_triggered)
        self.copy_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.copy_action)

        self.paste_action = QAction(self.tr("Paste"), self)  # type: QAction
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.triggered.connect(self.on_paste_action_triggered)
        self.paste_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.paste_action)

        self.delete_action = QAction(self.tr("Delete selection"), self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.triggered.connect(self.on_delete_action_triggered)
        self.delete_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.delete_action)

        self.insert_sine_action = QAction(self.tr("Insert sine wave..."), self)
        font = self.insert_sine_action.font()
        font.setBold(True)
        self.insert_sine_action.setFont(font)
        self.insert_sine_action.triggered.connect(self.on_insert_sine_action_triggered)

        self.insert_sine_plugin = InsertSinePlugin()
        self.insert_sine_plugin.insert_sine_wave_clicked.connect(self.on_insert_sine_wave_clicked)


    @property
    def signal(self):
        return self.parent_frame.signal

    @property
    def selection_area(self) -> ROI:
        return self.scene().selection_area

    @selection_area.setter
    def selection_area(self, value):
        self.scene().selection_area = value

    @property
    def scene_type(self):
        return self.parent_frame.ui.cbSignalView.currentIndex()

    @property
    def y_center(self):
        if self.scene_type == 0:
            # Normal scene
            return 0
        else:
            return -self.signal.qad_center

    @property
    def selected_messages(self):
        if not self.selection_area.is_empty:
            pa = self.parent_frame.proto_analyzer
            sb, _, eb, _ = pa.get_bitseq_from_selection(self.selection_area.start, abs(self.selection_area.width), self.signal.bit_len)
            return pa.messages[sb:eb + 1]
        else:
            return []

    def is_pos_in_separea(self, pos: QPoint):
        if self.scene_type == 0:
            return False
        padding = constants.SEPARATION_PADDING * self.view_rect().height()
        return self.y_sep - padding <= pos.y() <= self.y_sep + padding

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.001 ** event.angleDelta().y()
        self.zoom_all_signals(zoom_factor, event=event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self.ctrl_mode:
            return

        self.paste_position = int(self.mapToScene(event.pos()).x())

        menu = QMenu(self)
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

        #autorangeAction = menu.addAction(self.tr("Show Autocrop Range"))

        if not self.selection_area.is_empty:
            menu.addAction(self.delete_action)
            crop_action = menu.addAction(self.tr("Crop to selection"))
            mute_action = menu.addAction(self.tr("Mute selection"))

            menu.addSeparator()
            zoom_action = menu.addAction(self.tr("Zoom selection"))
            create_action = menu.addAction(self.tr("Create signal from selection"))

        selected_messages = self.selected_messages

        if len(selected_messages) == 1:
            selected_msg = selected_messages[0]
        else:
            selected_msg = None

        particpnt_actions = {}

        if len(selected_messages) > 0:
            partigroup = QActionGroup(self)
            participant_menu = menu.addMenu("Participant")
            none_partipnt_action = participant_menu.addAction("None")
            none_partipnt_action.setCheckable(True)
            none_partipnt_action.setActionGroup(partigroup)

            if selected_msg and selected_msg.participant is None:
                none_partipnt_action.setChecked(True)

            for particpnt in self.participants:
                pa = participant_menu.addAction(particpnt.name + " (" + particpnt.shortname + ")")
                pa.setCheckable(True)
                pa.setActionGroup(partigroup)
                if selected_msg and selected_msg.participant == particpnt:
                    pa.setChecked(True)

                particpnt_actions[pa] = particpnt
        else:
            none_partipnt_action = 42

        if self.scene_type == 0:
            if not self.selection_area.is_empty:
                menu.addSeparator()
                noise_action = menu.addAction(self.tr("Set noise level from Selection"))

        QApplication.processEvents()  # Ohne dies flackert das Menü beim ersten Erscheinen
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action is None:
            return
        elif action == zoom_action:
            self.zoom_to_selection(self.selection_area.x, self.selection_area.end)
        elif action == create_action:
            self.create_clicked.emit(self.selection_area.x, self.selection_area.end)
        #elif action == autorangeAction:
        #    self.show_crop_range_clicked.emit()
        elif action == crop_action:
            self.crop_clicked.emit()
        elif action == noise_action:
            self.set_noise_clicked.emit()
        elif action == mute_action:
            self.mute_wanted.emit(self.selection_area.start, self.selection_area.end)
        elif action == none_partipnt_action:
            for msg in selected_messages:
                msg.participant = None
            self.participant_changed.emit()

        elif action in particpnt_actions:
            for msg in selected_messages:
                msg.participant = particpnt_actions[action]
            self.participant_changed.emit()

    def zoom_all_signals(self, factor, event:QWheelEvent=None):
        if self.parent_frame.common_zoom:
            self.parent_frame.zoom_all_signals(factor)
        else:
            self.zoom(factor, event=event)

    def zoom(self, factor, supress_signal=False, event:QWheelEvent=None):
        self.show_full_signal = False
        if factor > 1 and self.view_rect().width() / factor < 300:
            factor = self.view_rect().width() / 300

        old_pos = self.mapToScene(event.pos()) if event else None

        self.scale(factor, 1)

        if self.view_rect().width() > self.sceneRect().width():
            self.draw_full_signal()

        if not supress_signal:
            self.zoomed.emit()

        if event:
            move = self.mapToScene(event.pos()) - old_pos
            self.translate(move.x(), 0)
        else:
            self.centerOn(self.view_rect().x() + self.view_rect().width() / 2, self.y_center)

    def set_lupen_cursor(self):
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

    def keyReleaseEvent(self, event: QKeyEvent):
        super().keyReleaseEvent(event)
        if event.key() == Qt.Key_Control:
            self.ctrl_mode = False
            self.ctrl_state_changed.emit(False)
            self.unsetCursor()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        self.show_full_signal = False

        super().keyPressEvent(event)

        if key == Qt.Key_Control and not self.shift_mode:
            self.set_lupen_cursor()
            self.ctrl_mode = True
            self.ctrl_state_changed.emit(True)

        if self.ctrl_mode and (key == Qt.Key_Plus or key == Qt.Key_Up):
            self.zoom_all_signals(1.1)
        elif self.ctrl_mode and (key == Qt.Key_Minus or key == Qt.Key_Down):
            self.zoom_all_signals(0.9)
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

    def draw_full_signal(self):
        if hasattr(self.parent_frame, "scene_creator"):
            self.parent_frame.scene_creator.show_full_scene()
            y_factor = self.transform().m22()
            self.resetTransform()
            x_factor = self.width() / self.sceneRect().width()
            self.scale(x_factor, y_factor)
            self.centerOn(0, self.y_center)

    def zoom_to_selection(self, start: int, end: int):
        if start == end:
            return

        x_factor = self.view_rect().width() / (end - start)
        self.zoom(x_factor)
        self.centerOn(start + (end - start) / 2, self.y_center)

    def autofit_view(self):

        h_tar = self.sceneRect().height()
        h_view = self.view_rect().height()

        if abs(h_tar) > 0:
            self.scale(1, h_view / h_tar)
        self.centerOn(self.view_rect().x() + self.view_rect().width() / 2, self.y_center)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if self.ctrl_mode and event.buttons() == Qt.LeftButton:
            self.zoom_all_signals(1.1)
        elif self.ctrl_mode and event.buttons() == Qt.RightButton:
            self.zoom_all_signals(0.9)

    def clear_selection(self):
        self.set_selection_area(0, 0)

    def resizeEvent(self, event):
        if self.view_rect().width() > self.sceneRect().width():
            x_factor = self.width() / self.sceneRect().width()
            self.scale(x_factor / self.transform().m11(), 1)

        self.autofit_view()

    @pyqtSlot()
    def on_copy_action_triggered(self):
        if not self.selection_area.is_empty:
            self.stored_item = self.signal._fulldata[int(self.selection_area.start):int(self.selection_area.end)]

    @pyqtSlot()
    def on_paste_action_triggered(self):
        if self.stored_item is not None:
            # paste_position is set in ContextMenuEvent
            self.signal.insert_data(self.paste_position, self.stored_item)

    @pyqtSlot()
    def on_delete_action_triggered(self):
        if not self.selection_area.is_empty:
            self.deletion_wanted.emit(self.selection_area.start, self.selection_area.end)

    @pyqtSlot()
    def on_save_action_triggered(self):
        self.save_clicked.emit()

    @pyqtSlot()
    def on_save_as_action_triggered(self):
        self.save_as_clicked.emit()

    @pyqtSlot()
    def on_insert_sine_action_triggered(self):
        self.insert_sine_plugin.show_insert_sine_dialog()

    @pyqtSlot()
    def on_insert_sine_wave_clicked(self):
        if self.insert_sine_plugin.complex_wave is not None:
            self.signal.insert_data(self.paste_position, self.insert_sine_plugin.complex_wave)
