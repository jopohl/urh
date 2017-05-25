import ast
import operator as op

from PyQt5.QtCore import pyqtSignal, QObject
from urh.SimulatorProtocolManager import SimulatorProtocolManager

class SimulatorExpressionParser(QObject):
    label_list_updated = pyqtSignal()

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
        super().__init__()

        self.sim_proto_manager = sim_proto_manager
        self.label_list = []
        self.create_connects()

    def create_connects(self):
        self.sim_proto_manager.items_added.connect(self.update_label_list)
        self.sim_proto_manager.items_moved.connect(self.update_label_list)
        self.sim_proto_manager.items_updated.connect(self.update_label_list)
        self.sim_proto_manager.items_deleted.connect(self.update_label_list)

    def validate_expression(self, expr, is_formula=True):
        valid = True
        message = ""

        try:
            node = ast.parse(expr, mode='eval').body
            self.validate_formula_node(node) if is_formula else self.validate_condition_node(node)
        except SyntaxError as err:
            valid = False
            message = expr + "\n" + " " * err.offset + "^" + "\n" + str(err)

        return (valid, message)

    def validate_formula_node(self, node):
        if isinstance(node, ast.Num):
            return
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in self.operators_formula:
                self.raise_syntax_error("unknown operator", node.lineno, node.col_offset)

            self.validate_formula_node(node.left)
            self.validate_formula_node(node.right)
        elif isinstance(node, ast.Attribute):
            return self.check_attribute_node(node)
        else:
            self.raise_syntax_error("", node.lineno, node.col_offset)

    def validate_condition_node(self, node):
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in self.operators_condition:
                self.raise_syntax_error("unknown operator", node.lineno, node.col_offset)

            self.validate_condition_node(node.operand)
        elif isinstance(node, ast.Compare):
            if not (len(node.ops) == 1 and len(node.comparators) == 1):
                self.raise_syntax_error("", node.lineno, node.col_offset)

            if type(node.ops[0]) not in self.operators_condition:
                self.raise_syntax_error("unknown operator", node.lineno, node.col_offset)

            self.check_compare_nodes(node.left, node.comparators[0])
        elif isinstance(node, ast.BoolOp):
            for node in node.values:
                self.validate_condition_node(node)
        else:
            self.raise_syntax_error("", node.lineno, node.col_offset)

    def check_compare_nodes(self, left, right):
        if not isinstance(left, ast.Attribute):
            self.raise_syntax_error("the left-hand side of a comparison must be a label identifier",
                left.lineno, left.col_offset)

        self.check_attribute_node(left)

        if not isinstance(right, (ast.Num, ast.Str, ast.Attribute)):
            self.raise_syntax_error("the right-hand side of a comparison must be a number, a string or a label identifier",
                right.lineno, right.col_offset)

        if isinstance(right, ast.Attribute):
            self.check_attribute_node(right)

    def check_attribute_node(self, node):
        if not isinstance(node.value, ast.Name):
            self.raise_syntax_error("", node.lineno, node.col_offset)

        label_identifier = node.value.id + "." + node.attr

        if label_identifier not in self.label_list:
            self.raise_syntax_error("'" + label_identifier + "' is not a valid label identifier",
                node.lineno, node.col_offset)

    def raise_syntax_error(self, message, lineno, col_offset):
        if message == "":
            message = "_invalid syntax"

        raise SyntaxError(message, ("<unknown>", lineno, col_offset, ""))

    def update_label_list(self):
        self.label_list.clear()

        for msg in self.sim_proto_manager.get_all_messages():
            for lbl in msg.children:
                label_name = "item" + msg.index().replace(".", "_") + "." + lbl.name.replace(" ", "_")
                self.label_list.append(label_name)

        self.label_list_updated.emit()