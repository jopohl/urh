from PyQt5.QtWidgets import QGraphicsView, QMenu, QAction
from PyQt5.QtGui import QKeySequence

class LoggingGraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.log_selected_action = QAction(self.tr("Log selected items"), self)
        self.log_selected_action.setShortcut(QKeySequence("L"))
        self.log_selected_action.triggered.connect(self.on_log_selected_action_triggered)

        self.do_not_log_selected_action = QAction(self.tr("Do not log selected items"), self)
        self.do_not_log_selected_action.setShortcut(QKeySequence("N"))
        self.do_not_log_selected_action.triggered.connect(self.on_do_not_log_selected_action_triggered)

        self.select_all_action = QAction(self.tr("Select all"), self)
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.triggered.connect(self.on_select_all_action_triggered)

        self.addAction(self.log_selected_action)
        self.addAction(self.do_not_log_selected_action)
        self.addAction(self.select_all_action)

    def contextMenuEvent(self, event):
        menu = self.create_context_menu()
        action = menu.exec_(event.globalPos())

    def create_context_menu(self):
        menu = QMenu()

        if len(self.scene().selectedItems()):
            menu.addAction(self.log_selected_action)
            menu.addAction(self.do_not_log_selected_action)

        if len(self.scene().visible_participants):
            menu.addSeparator()

            select_from_menu = menu.addMenu("Select all messages from")

            for vp in self.scene().visible_participants:
                if vp is self.scene().broadcast_part:
                    continue

                vpa = select_from_menu.addAction(vp.text.toPlainText())
                vpa.setData(vp)
                vpa.triggered.connect(self.on_select_from_action_triggered)

            select_to_menu = menu.addMenu("Select all messages to")

            for vp in self.scene().visible_participants:
                vpa = select_to_menu.addAction(vp.text.toPlainText())
                vpa.setData(vp)
                vpa.triggered.connect(self.on_select_to_action_triggered)

        return menu

    def on_select_from_action_triggered(self):
        self.scene().select_messages_with_participant(self.sender().data())

    def on_select_to_action_triggered(self):
        self.scene().select_messages_with_participant(self.sender().data(), from_part=False)

    def on_log_selected_action_triggered(self):
        self.scene().log_selected_items(True)

    def on_do_not_log_selected_action_triggered(self):
        self.scene().log_selected_items(False)

    def on_select_all_action_triggered(self):
        self.scene().select_all_items()