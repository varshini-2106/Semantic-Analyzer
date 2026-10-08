from ast_nodes import (
    Block, Declaration, Assignment, BinaryExpression,
    Literal, Identifier, ParenthesizedExpression
)
from errors import SemanticError
from symbol_table import SymbolTable

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def analyze(self, program):
        for statement in program.statements:
            self.visit(statement)
        return self.errors

    def visit(self, node):
        if isinstance(node, Block):
            self.symbol_table.enter_scope()
            for statement in node.statements:
                self.visit(statement)
            self.symbol_table.exit_scope()

        elif isinstance(node, Declaration):
            if not self.symbol_table.declare(node.name, node.var_type):
                self.errors.append(
                    SemanticError(
                        f"Variable '{node.name}' is already declared in the current scope."
                    )
                )

        elif isinstance(node, Assignment):
            symbol = self.symbol_table.lookup(node.name)

            if symbol is None:
                self.errors.append(
                    SemanticError(f"Variable '{node.name}' is not declared.")
                )
                return

            expression_type = self.expression_type(node.expression)

            if expression_type is not None and not self.assignment_compatible(
                symbol.var_type, expression_type
            ):
                self.errors.append(
                    SemanticError(
                        f"Cannot assign {expression_type} to {symbol.var_type} variable '{node.name}'."
                    )
                )

    def expression_type(self, node):
        if isinstance(node, Literal):
            return node.value_type

        if isinstance(node, Identifier):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                self.errors.append(
                    SemanticError(f"Variable '{node.name}' is not declared.")
                )
                return None
            return symbol.var_type

        if isinstance(node, ParenthesizedExpression):
            return self.expression_type(node.expression)

        if isinstance(node, BinaryExpression):
            left_type = self.expression_type(node.left)
            right_type = self.expression_type(node.right)

            if left_type is None or right_type is None:
                return None

            if left_type == "bool" or right_type == "bool":
                self.errors.append(
                    SemanticError(
                        f"Operator '{node.operator}' cannot be applied to boolean values."
                    )
                )
                return None

            if left_type == "float" or right_type == "float":
                return "float"

            return "int"

        return None

    @staticmethod
    def assignment_compatible(target_type, expression_type):
        # Exact matches are always valid.
        if target_type == expression_type:
            return True

        # Safe widening conversion: int -> float.
        if target_type == "float" and expression_type == "int":
            return True

        return False
