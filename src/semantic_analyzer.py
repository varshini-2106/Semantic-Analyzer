from .ast_nodes import (
    Program, Block, Declaration, Assignment,
    IfStatement, WhileStatement, BinaryExpression,
    UnaryExpression, Literal, Identifier,
    ParenthesizedExpression
)
from .errors import SemanticError
from .symbol_table import SymbolTable


NUMERIC_TYPES = {"int", "float"}
ALL_TYPES = {"int", "float", "bool", "string", "char"}


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def error(self, node, message, category="Semantic"):
        self.errors.append(
            SemanticError(
                category, message,
                getattr(node, "line", None),
                getattr(node, "column", None)
            )
        )

    def analyze(self, program):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.visit(program)
        return self.errors

    def visit(self, node):
        if isinstance(node, Program):
            for statement in node.statements:
                self.visit(statement)

        elif isinstance(node, Block):
            self.symbol_table.enter_scope()
            try:
                for statement in node.statements:
                    self.visit(statement)
            finally:
                self.symbol_table.exit_scope()

        elif isinstance(node, Declaration):
            if node.var_type not in ALL_TYPES:
                self.error(node, f"Unknown type '{node.var_type}'.")
                return

            if not self.symbol_table.declare(
                node.name, node.var_type, node.line, node.column
            ):
                self.error(
                    node,
                    f"Variable '{node.name}' is already declared "
                    "in this scope."
                )
                return

            if node.initializer is not None:
                value_type = self.expression_type(node.initializer)
                if not self.assignable(node.var_type, value_type):
                    self.error(
                        node,
                        f"Cannot initialize '{node.name}' of type "
                        f"'{node.var_type}' with '{value_type}'."
                    )

        elif isinstance(node, Assignment):
            symbol = self.symbol_table.lookup(node.name)
            value_type = self.expression_type(node.expression)

            if symbol is None:
                self.error(
                    node, f"Variable '{node.name}' is not declared."
                )
            elif not self.assignable(symbol.var_type, value_type):
                self.error(
                    node,
                    f"Cannot assign '{value_type}' to variable "
                    f"'{node.name}' of type '{symbol.var_type}'."
                )

        elif isinstance(node, IfStatement):
            condition_type = self.expression_type(node.condition)

            if condition_type != "bool":
                self.error(node, "If condition must be Boolean.")

            self.visit(node.then_branch)

            if node.else_branch is not None:
                self.visit(node.else_branch)

        elif isinstance(node, WhileStatement):
            condition_type = self.expression_type(node.condition)

            if condition_type != "bool":
                self.error(node, "While condition must be Boolean.")

            self.visit(node.body)

    def assignable(self, target_type, source_type):
        if target_type == source_type:
            return True

        # Widening conversion only: int can be assigned to float.
        return target_type == "float" and source_type == "int"

    def expression_type(self, node):
        if isinstance(node, Literal):
            return node.literal_type

        if isinstance(node, Identifier):
            symbol = self.symbol_table.lookup(node.name)

            if symbol is None:
                self.error(
                    node, f"Variable '{node.name}' is not declared."
                )
                return "error"

            return symbol.var_type

        if isinstance(node, ParenthesizedExpression):
            return self.expression_type(node.expression)

        if isinstance(node, UnaryExpression):
            operand_type = self.expression_type(node.operand)

            if operand_type == "error":
                return "error"

            if node.operator == "-":
                if operand_type in NUMERIC_TYPES:
                    return operand_type

                self.error(
                    node, "Unary '-' requires a numeric operand."
                )
                return "error"

            if node.operator == "!":
                if operand_type == "bool":
                    return "bool"

                self.error(
                    node, "Unary '!' requires a Boolean operand."
                )
                return "error"

        if isinstance(node, BinaryExpression):
            left_type = self.expression_type(node.left)
            right_type = self.expression_type(node.right)

            if "error" in {left_type, right_type}:
                return "error"

            op = node.operator

            if op in {"+", "-", "*", "/"}:
                if op == "+" and left_type == right_type == "string":
                    return "string"

                if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                    # Division returns float in this language.
                    if op == "/":
                        return "float"

                    if "float" in {left_type, right_type}:
                        return "float"

                    return "int"

                self.error(
                    node,
                    f"Operator '{op}' requires numeric operands"
                    " (except string + string)."
                )
                return "error"

            if op in {"<", "<=", ">", ">="}:
                if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                    return "bool"

                self.error(
                    node, f"Operator '{op}' requires numeric operands."
                )
                return "error"

            if op in {"==", "!="}:
                if (
                    left_type == right_type
                    or (
                        left_type in NUMERIC_TYPES
                        and right_type in NUMERIC_TYPES
                    )
                ):
                    return "bool"

                self.error(
                    node,
                    f"Cannot compare '{left_type}' and '{right_type}'."
                )
                return "error"

            if op in {"&&", "||"}:
                if left_type == right_type == "bool":
                    return "bool"

                self.error(
                    node,
                    f"Operator '{op}' requires Boolean operands."
                )
                return "error"

        self.error(node, "Unsupported expression.")
        return "error"