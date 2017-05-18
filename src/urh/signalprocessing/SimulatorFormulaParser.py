import ast
import operator as op

from urh.SimulatorProtocolManager import SimulatorProtocolManager

class SimulatorFormulaParser(object):
    operators = {
                    ast.Add: op.add,
                    ast.Sub: op.sub,
                    ast.Mult: op.mul,
                    ast.BitOr: op.or_,
                    ast.BitXor: op.xor,
                    ast.BitAnd: op.and_,
                    ast.LShift: op.lshift,
                    ast.RShift: op.rshift,
                    ast.Invert: op.invert,
                    ast.USub: op.neg,
                    ast.UAdd: op.pos
                }

    def __init__(self, sim_proto_manager: SimulatorProtocolManager):
        self.sim_proto_manager = sim_proto_manager
        self.label_list = []
        self.create_connects()

    def create_connects(self):
        self.sim_proto_manager.items_added.connect(self.update_label_list)
        self.sim_proto_manager.items_moved.connect(self.update_label_list)
        self.sim_proto_manager.items_updated.connect(self.update_label_list)
        self.sim_proto_manager.items_deleted.connect(self.update_label_list)

    def validate_exp(self, expr):
        try:
            node = ast.parse(expr, mode='eval').body
        except SyntaxError:
            return False

        return self.validate_node(node)

    def validate_node(self, node):
        if isinstance(node, ast.Num):
            return True
        elif isinstance(node, ast.BinOp):
            return (type(node.op) in self.operators and self.validate_node(node.left) and
                        self.validate_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return type(node.op) in self.operators and self.validate_node(node.operand)
        elif isinstance(node, ast.Attribute):
            return (isinstance(node.value, ast.Name) and
                    (node.value.id + "." + node.attr in self.label_list))
        else:
            return False

    def update_label_list(self):
        self.label_list.clear()

        for msg in self.sim_proto_manager.get_all_messages():
            for lbl in msg.children:
                label_name = "item" + msg.index().replace(".", "_") + "." + lbl.name.replace(" ", "_")
                self.label_list.append(label_name)