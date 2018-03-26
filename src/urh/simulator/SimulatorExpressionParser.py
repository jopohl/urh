import ast
import html
import operator as op

from PyQt5.QtCore import QObject

from urh.simulator.SimulatorCounterAction import SimulatorCounterAction
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.simulator.SimulatorConfiguration import SimulatorConfiguration
from urh.simulator.SimulatorTriggerCommandAction import SimulatorTriggerCommandAction
from urh.util.Logger import logger


class SimulatorExpressionParser(QObject):
    formula_help = "<html><head/><body><p><b>Formula</b></p><p><i>Operators:</i> <code>+</code> (Addition), <code>-</code> (Subtraction), <code>*</code> (Multiplication), <code>/</code> (Division)</p><p><i>Bitwise operations:</i> <code>|</code> (Or), <code>^</code> (Exclusive Or), <code>&amp;</code> (And), <code>&lt;&lt;</code> (Left Shift), <code>&gt;&gt;</code> (Right Shift), <code>~</code> (Inversion)</p><p><i>Numeric literals:</i> <code>14</code> (dec), <code>0xe</code> (hex), <code>0b1110</code> (bin), <code>0o16</code> (oct)</p><i>Examples:</i><ul><li><code>item1.sequence_number + 1</code></li><li><code>~ (item1.preamble ^ 0b1110)</code></li></ul></body></html>"

    rule_condition_help = "<html><head/><body><p><b>Rule condition</b></p><p><i>Boolean operations:</i> <code>and</code>, <code>or</code>, <code>not</code></p><p><i>Comparison operations:</i> <code>==</code> (equal), <code>!=</code> (not equal), <code>&lt;</code> (lower), <code>&lt;=</code> (lower equal), <code>&gt;</code> (greater), <code>&gt;=</code> (greater equal)</p><p><i>Numeric literals:</i> <code>14</code> (dec), <code>0xe</code> (hex), <code>0b1110</code> (bin), <code>0o16</code> (oct)</p><p><i>String literals:</i> <code>&quot;abc&quot;</code> or <code>'abc'</code></p><p><i>Examples:</i></p><ul><li><code>item1.data == &quot;abc&quot;</code></li><li><code>not (item3.source_address == 0x123 or item1.length &gt;= 5)</code></li></ul></body></html>"

    op_formula = {
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

    op_cond = {
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

    operators = {}
    operators.update(op_formula)
    operators.update(op_cond)

    def __init__(self, config: SimulatorConfiguration):
        super().__init__()

        self.simulator_config = config

    def validate_expression(self, expr, is_formula=True):
        valid = True
        node = None

        try:
            node = ast.parse(expr, mode='eval').body
            self.validate_formula_node(node) if is_formula else self.validate_condition_node(node)
        except SyntaxError as err:
            valid = False
            message = "<pre>" + html.escape(expr) + "<br/>" + " " * err.offset + "^</pre>" + str(err)
        else:
            message = self.formula_help if is_formula else self.rule_condition_help

        return (valid, message, node)

    def evaluate_node(self, node):
        if isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](self.evaluate_node(node.left),
                                                 self.evaluate_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self.evaluate_node(node.operand))
        elif isinstance(node, ast.Compare):
            to_string = isinstance(node.comparators[0], ast.Str)

            return self.operators[type(node.ops[0])](self.evaluate_attribute_node(node.left, to_string),
                                                     self.evaluate_node(node.comparators[0]))
        elif isinstance(node, ast.BoolOp):
            func = all if isinstance(node.op, ast.And) else any
            return func(self.evaluate_node(value) for value in node.values)
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Attribute):
            return self.evaluate_attribute_node(node)
        elif isinstance(node, ast.Num):
            return node.n
        else:
            logger.error("Error during parsing")

    def evaluate_attribute_node(self, node, to_string=False):
        identifier = node.value.id + "." + node.attr
        if isinstance(self.simulator_config.item_dict[identifier], SimulatorProtocolLabel):
            label = self.simulator_config.item_dict[identifier]
            message = label.parent()

            start, end = message.get_label_range(label, 2 if to_string else 0, False)
            return message.plain_ascii_str[start:end] if to_string else int(message.plain_bits_str[start:end], 2)
        elif isinstance(self.simulator_config.item_dict[identifier], SimulatorCounterAction):
            return self.simulator_config.item_dict[identifier].value
        elif isinstance(self.simulator_config.item_dict[identifier], SimulatorTriggerCommandAction):
            return self.simulator_config.item_dict[identifier].return_code

    def validate_formula_node(self, node):
        if isinstance(node, ast.Num):
            return
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in self.op_formula:
                self.raise_syntax_error("unknown operator", node.lineno, node.col_offset)

            self.validate_formula_node(node.left)
            self.validate_formula_node(node.right)
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in self.op_formula:
                self.raise_syntax_error("unknown operator", node.lineno, node.col_offset)

            self.validate_formula_node(node.operand)
        elif isinstance(node, ast.Attribute):
            return self.validate_attribute_node(node)
        else:
            self.raise_syntax_error("", node.lineno, node.col_offset)

    def validate_condition_node(self, node):
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in self.op_cond:
                self.raise_syntax_error("unknown operator", node.lineno, node.col_offset)

            self.validate_condition_node(node.operand)
        elif isinstance(node, ast.Compare):
            if not (len(node.ops) == 1 and len(node.comparators) == 1):
                self.raise_syntax_error("", node.lineno, node.col_offset)

            if type(node.ops[0]) not in self.op_cond:
                self.raise_syntax_error("unknown operator", node.lineno, node.col_offset)

            self.validate_compare_nodes(node.left, node.comparators[0])
        elif isinstance(node, ast.BoolOp):
            for node in node.values:
                self.validate_condition_node(node)
        else:
            self.raise_syntax_error("", node.lineno, node.col_offset)

    def validate_compare_nodes(self, left, right):
        if not isinstance(left, ast.Attribute):
            self.raise_syntax_error("the left-hand side of a comparison must be a label identifier",
                                    left.lineno, left.col_offset)

        self.validate_attribute_node(left)

        if not isinstance(right, (ast.Num, ast.Str, ast.Attribute)):
            self.raise_syntax_error(
                "the right-hand side of a comparison must be a number, a string or a label identifier",
                right.lineno, right.col_offset)

        if isinstance(right, ast.Attribute):
            self.validate_attribute_node(right)

    def validate_attribute_node(self, node):
        if not isinstance(node.value, ast.Name):
            self.raise_syntax_error("", node.lineno, node.col_offset)

        identifier = node.value.id + "." + node.attr

        if not self.is_valid_identifier(identifier):
            self.raise_syntax_error("'" + identifier + "' is not a valid label identifier",
                                    node.lineno, node.col_offset)

    def is_valid_identifier(self, identifier):
        try:
            item = self.simulator_config.item_dict[identifier]
            return isinstance(item, SimulatorProtocolLabel) or\
                   isinstance(item, SimulatorCounterAction) or \
                   (isinstance(item, SimulatorTriggerCommandAction) and identifier.endswith("rc"))
        except KeyError:
            return False

    def get_identifiers(self):
        return [identifier for identifier in self.simulator_config.item_dict if self.is_valid_identifier(identifier)]

    def raise_syntax_error(self, message, lineno, col_offset):
        if message == "":
            message = "_invalid syntax"

        raise SyntaxError(message, ("", lineno, col_offset, ""))
