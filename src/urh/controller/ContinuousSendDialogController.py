from urh.SceneManager import SceneManager
from urh.controller.SendRecvDialogController import SendRecvDialogController
from urh.dev.VirtualDevice import VirtualDevice, Mode


class ContinuousSendDialogController(SendRecvDialogController):
    def __init__(self, project_manager, messages, modulators, parent, testing_mode=False):
        super().__init__(project_manager, is_tx=True, parent=parent, testing_mode=testing_mode)
        self.messages = messages
        self.modulators = modulators

        self.graphics_view = self.ui.graphicsViewContinuousSend
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_continuous_send)
        self.scene_manager = SceneManager(parent=self)

        self.init_device()

        self.create_connects()

    def create_connects(self):
        super().create_connects()
        self.ui.spinBoxNRepeat.editingFinished.connect(self.on_num_repeats_changed)

    def init_device(self):
        device_name = self.ui.cbDevice.currentText()
        num_repeats = self.ui.spinBoxNRepeat.value()

        # TODO: Consider Continous Send Mode in Virtual Device
        self.device = VirtualDevice(self.backend_handler, device_name, Mode.send,
                                    device_ip="192.168.10.2", sending_repeats=num_repeats, parent=self)

        self._create_device_connects()
