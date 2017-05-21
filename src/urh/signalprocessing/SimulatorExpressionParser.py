import ast
import operator as op

from urh.SimulatorProtocolManager import SimulatorProtocolManager

class SimulatorExpressionParser(object):
    operators_formula = {
                            ast.Add: op.add,
                            ast.Sub: op.sub,
                            ast.Mult: op.mul,
                            ast.Div: op.truediv,
                            ast.BitOr: op.or_,
                            ast.BitXor: op.xor,
                            ast.BitAnd: op.and_,
                            ast.LShift: op.lshift,
                            ast.RShift: op.rshift,
                            ast.Invert: op.invert
                        }

    operators_condition = {
                            ast.And: None,
                            ast.Or: None,
                            ast.Not: op.not_,
                            ast.Eq: op.eq,
                            ast.NotEq: op.ne,
                            ast.Lt: op.lt,
                            ast.LtE: op.le,
                            ast.Gt: op.gt,
                            ast.GtE: op.ge
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

    def validate_condition(self, expr):
        try:
            node = ast.parse(expr, mode='eval').body
        except SyntaxError:
            return False

        return self.validate_condition_node(node)

    def validate_formula(self, expr):
        try:
            node = ast.parse(expr, mode='eval').body
        except SyntaxError:
            return False

        return self.validate_formula_node(node)

    def validate_formula_node(self, node):
        if isinstance(node, ast.Num):
            return True
        elif isinstance(node, ast.BinOp):
            return (type(node.op) in self.operators_formula and self.validate_formula_node(node.left) and
                        self.validate_formula_node(node.right))
        elif isinstance(node, ast.Attribute):
            return self.check_attribute_node(node)
        else:
            return False

    def validate_condition_node(self, node):
        if isinstance(node, ast.UnaryOp):
            return (type(node.op) in self.operators_condition and
                    self.validate_condition_node(node.operand))
        elif isinstance(node, ast.Compare):
            return (len(node.ops) == 1 and len(node.comparators) == 1 and
                    type(node.ops[0]) in self.operators_condition and
                    self.check_compare_nodes(node.left, node.comparators[0]))
        elif isinstance(node, ast.BoolOp):
            return (type(node.op) in self.operators_condition and
                    all(self.validate_condition_node(node) for node in node.values))
        else:
            return False

    def check_compare_nodes(self, left, right):
        if (not (isinstance(left, ast.Attribute) and
                self.check_attribute_node(left))):
            return False

        if not isinstance(right, (ast.Num, ast.Str, ast.Attribute)):
            return False

        if (isinstance(right, ast.Attribute) and not
            self.check_attribute_node(right)):
            return False

        return True

    def check_attribute_node(self, node):
        return (isinstance(node.value, ast.Name) and
                    (node.value.id + "." + node.attr in self.label_list))

    def update_label_list(self):
        self.label_list.clear()

        for msg in self.sim_proto_manager.get_all_messages():
            for lbl in msg.children:
                label_name = "item" + msg.index().replace(".", "_") + "." + lbl.name.replace(" ", "_")
                self.label_list.append(label_name)