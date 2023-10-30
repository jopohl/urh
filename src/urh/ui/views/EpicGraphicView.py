import math

from PyQt5.QtCore import Qt, QPoint, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QAction

from urh import settings
from urh.ui.views.EditableGraphicView import EditableGraphicView


class EpicGraphicView(EditableGraphicView):
    """
    Tied to Signal Frame (Interpretation)
    """

    save_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.save_enabled = True
        self.create_new_signal_enabled = True
        self.participants_assign_enabled = True
        self.cache_qad = True
        self.y_sep = 0

        self.save_action = QAction(self.tr("Save"), self)  # type: QAction
        self.save_action.setIcon(QIcon.fromTheme("document-save"))
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.on_save_action_triggered)
        self.save_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.save_action)

    @property
    def sample_rate(self):
        try:
            return self.signal.sample_rate
        except AttributeError:
            return None

    @sample_rate.setter
    def sample_rate(self, value):
        raise ValueError("Not implemented for epic graphic view")

    @property
    def selected_messages(self):
        if self.something_is_selected and self.protocol:
            sb, _, eb, _ = self.protocol.get_bitseq_from_selection(
                self.selection_area.start, abs(self.selection_area.width)
            )
            return self.protocol.messages[sb : eb + 1]
        else:
            return []

    def is_pos_in_separea(self, pos: QPoint):
        if self.scene_type != 1:
            return False
        padding = settings.SEPARATION_PADDING * self.view_rect().height()
        return self.y_sep - padding <= pos.y() <= self.y_sep + padding

    def _get_sub_path_ranges_and_colors(self, start: float, end: float):
        sub_path_ranges = []
        colors = []
        start = max(0, int(start))
        end = int(math.ceil(end))

        if not self.protocol.messages:
            return None, None

        for message in self.protocol.messages:
            if message.bit_sample_pos[-2] < start:
                continue

            color = (
                None
                if message.participant is None
                else settings.PARTICIPANT_COLORS[message.participant.color_index]
            )

            if color is None:
                continue

            # Append the pause until first bit of message
            sub_path_ranges.append((start, message.bit_sample_pos[0]))
            if start < message.bit_sample_pos[0]:
                colors.append(None)
            else:
                colors.append(color)  # Zoomed inside a message

            if message.bit_sample_pos[-2] > end:
                sub_path_ranges.append((message.bit_sample_pos[0], end))
                colors.append(color)
                break

            # Data part of the message
            sub_path_ranges.append(
                (message.bit_sample_pos[0], message.bit_sample_pos[-2] + 1)
            )
            colors.append(color)

            start = message.bit_sample_pos[-2] + 1

        if sub_path_ranges and sub_path_ranges[-1][1] != end:
            sub_path_ranges.append((sub_path_ranges[-1][1], end))
            colors.append(None)

        sub_path_ranges = sub_path_ranges if sub_path_ranges else None
        colors = colors if colors else None
        return sub_path_ranges, colors

    @pyqtSlot()
    def on_save_action_triggered(self):
        self.save_clicked.emit()
