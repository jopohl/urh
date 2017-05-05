from urh.SimulatorProtocolManager import SimulatorProtocolManager

class SimulatorFormulaParser(object):
    def __init__(self, sim_proto_manager: SimulatorProtocolManager):
        self.sim_proto_manager = sim_proto_manager
        self.label_list = []
        self.create_connects()

    def create_connects(self):
        self.sim_proto_manager.item_added.connect(self.update_label_list)
        self.sim_proto_manager.item_moved.connect(self.update_label_list)
        self.sim_proto_manager.item_updated.connect(self.update_label_list)
        self.sim_proto_manager.item_deleted.connect(self.update_label_list)

    def update_label_list(self):
        self.label_list.clear()

        for msg in self.sim_proto_manager.get_all_messages():
            for lbl in msg.children:
                self.label_list.append("item" + msg.index().replace(".", "_") + "." + lbl.name.replace(" ", "_"))