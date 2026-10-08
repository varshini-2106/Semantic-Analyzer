from ast_nodes import (
    Block,
    Declaration,
    Assignment,
    BinaryExpression,
    Literal,
    Identifier,
    ParenthesizedExpression
)

from errors import SemanticError
from symbol_table import SymbolTable


class SemanticAnalyzer:

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def analyze(self, program):
        self.errors = []

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

            success = self.symbol_table.declare(
                node.name,
                node.var_type
            )

            if not success:

                self.errors.append(
                    SemanticError(
                        category="DUPLICATE_DECLARATION",

                        message=(
                            f"Variable '{node.name}' is already "
                            f"declared in the current scope."
                        ),

                        line=node.line,
                        column=node.column,

                        details={
                            "Variable": node.name,
                            "Type": node.var_type,
                            "Scope": self.symbol_table.current_scope_level
                        },

                        rule=(
                            "An identifier cannot be declared more "
                            "than once within the same scope."
                        )
                    )
                )

        elif isinstance(node, Assignment):

            symbol = self.symbol_table.lookup(node.name)

            if symbol is None:

                self.errors.append(
                    SemanticError(
                        category="UNDECLARED_VARIABLE",

                        message=(
                            f"Variable '{node.name}' is not declared."
                        ),

                        line=node.line,
                        column=node.column,

                        details={
                            "Identifier": node.name,
                            "Status": (
                                "No declaration found in the "
                                "current or enclosing scopes."
                            )
                        },

                        rule=(
                            "Every identifier must be declared "
                            "before it is used."
                        )
                    )
                )

                # Still analyze the expression so that
                # additional errors inside it can be found.
                self.expression_type(node.expression)

                return

            expression_type = self.expression_type(
                node.expression
            )

            if expression_type is not None:

                if not self.assignment_compatible(
                    symbol.var_type,
                    expression_type
                ):

                    self.errors.append(
                        SemanticError(
                            category="TYPE_MISMATCH",

                            message=(
                                f"Cannot assign {expression_type} "
                                f"to {symbol.var_type} variable "
                                f"'{node.name}'."
                            ),

                            line=node.line,
                            column=node.column,

                            details={
                                "Variable": node.name,
                                "Expected type": symbol.var_type,
                                "Found type": expression_type
                            },

                            rule=(
                                "An assignment expression must be "
                                "compatible with the declared "
                                "variable type."
                            )
                        )
                    )

    def expression_type(self, node):

        if isinstance(node, Literal):
            return node.value_type

        if isinstance(node, Identifier):

            symbol = self.symbol_table.lookup(node.name)

            if symbol is None:

                self.errors.append(
                    SemanticError(
                        category="UNDECLARED_VARIABLE",

                        message=(
                            f"Variable '{node.name}' is not declared."
                        ),

                        line=node.line,
                        column=node.column,

                        details={
                            "Identifier": node.name,
                            "Status": (
                                "No declaration found in the "
                                "current or enclosing scopes."
                            )
                        },

                        rule=(
                            "Every identifier must be declared "
                            "before it is used."
                        )
                    )
                )

                return None

            return symbol.var_type

        if isinstance(node, ParenthesizedExpression):

            return self.expression_type(
                node.expression
            )

        if isinstance(node, BinaryExpression):

            left_type = self.expression_type(
                node.left
            )

            right_type = self.expression_type(
                node.right
            )

            if left_type is None or right_type is None:
                return None

            if left_type == "bool" or right_type == "bool":

                self.errors.append(
                    SemanticError(
                        category="INVALID_EXPRESSION",

                        message=(
                            f"Operator '{node.operator}' cannot "
                            f"be applied to boolean values."
                        ),

                        line=node.line,
                        column=node.column,

                        details={
                            "Operator": node.operator,
                            "Left type": left_type,
                            "Right type": right_type
                        },

                        rule=(
                            "Arithmetic operators require "
                            "numeric operands."
                        )
                    )
                )

                return None

            if left_type == "float" or right_type == "float":
                return "float"

            return "int"

        return None

    @staticmethod
    def assignment_compatible(
        target_type,
        expression_type
    ):

        # Exact matches are valid.
        if target_type == expression_type:
            return True

        # Safe widening conversion: int -> float.
        if (
            target_type == "float"
            and expression_type == "int"
        ):
            return True

        return False