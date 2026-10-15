
try:
    from .ast_nodes import (
        Program,
        Block,
        Declaration,
        Assignment,
        IfStatement,
        WhileStatement,
        BinaryExpression,
        UnaryExpression,
        Literal,
        Identifier,
        ParenthesizedExpression,
    )
    from .symbol_table import SymbolTable
    from .errors import SemanticError
except ImportError:
    from ast_nodes import (
        Program,
        Block,
        Declaration,
        Assignment,
        IfStatement,
        WhileStatement,
        BinaryExpression,
        UnaryExpression,
        Literal,
        Identifier,
        ParenthesizedExpression,
    )
    from symbol_table import SymbolTable
    from errors import SemanticError


NUMERIC_TYPES = {"int", "float"}


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def error(
        self,
        category,
        message,
        node,
        expected=None,
        found=None,
        rule=None,
        identifier=None,
    ):
        self.errors.append(
            SemanticError(
                category=category,
                message=message,
                line=node.line,
                column=node.column,
                expected=expected,
                found=found,
                rule=rule,
                identifier=identifier,
            )
        )

    def analyze(self, program):
        # Reset state so the same analyzer can analyze multiple programs.
        self.symbol_table = SymbolTable()
        self.errors = []

        for statement in program.statements:
            self.visit_statement(statement)

        return self.errors

    def visit_statement(self, node):
        if isinstance(node, Declaration):
            declared = self.symbol_table.declare(
                node.name,
                node.var_type,
                node.line,
                node.column,
            )

            if not declared:
                self.error(
                    "DUPLICATE_DECLARATION",
                    f"Variable '{node.name}' is already declared "
                    "in this scope.",
                    node,
                    identifier=node.name,
                    rule="A variable can be declared only once "
                         "within the same scope.",
                )

        elif isinstance(node, Assignment):
            symbol = self.symbol_table.lookup(node.name)

            # Check the right-hand side even if the target is undeclared.
            expression_type = self.expression_type(node.expression)

            if symbol is None:
                self.error(
                    "UNDECLARED_VARIABLE",
                    f"Variable '{node.name}' has not been declared.",
                    node,
                    identifier=node.name,
                    rule="A variable must be declared before assignment.",
                )

            elif (
                expression_type is not None
                and not self.assignable(
                    symbol.var_type,
                    expression_type,
                )
            ):
                self.error(
                    "TYPE_MISMATCH",
                    f"Cannot assign '{expression_type}' to "
                    f"'{symbol.var_type}' variable '{node.name}'.",
                    node,
                    expected=symbol.var_type,
                    found=expression_type,
                    identifier=node.name,
                    rule="The assigned value must have a compatible type.",
                )

        elif isinstance(node, Block):
            self.symbol_table.enter_scope()

            try:
                for statement in node.statements:
                    self.visit_statement(statement)
            finally:
                self.symbol_table.exit_scope()

        elif isinstance(node, IfStatement):
            condition_type = self.expression_type(node.condition)

            if (
                condition_type is not None
                and condition_type != "bool"
            ):
                self.error(
                    "INVALID_CONDITION",
                    "An if condition must have type 'bool'.",
                    node.condition,
                    expected="bool",
                    found=condition_type,
                    rule="Conditional expressions must be Boolean.",
                )

            self.visit_statement(node.then_branch)

            if node.else_branch is not None:
                self.visit_statement(node.else_branch)

        elif isinstance(node, WhileStatement):
            condition_type = self.expression_type(node.condition)

            if (
                condition_type is not None
                and condition_type != "bool"
            ):
                self.error(
                    "INVALID_CONDITION",
                    "A while condition must have type 'bool'.",
                    node.condition,
                    expected="bool",
                    found=condition_type,
                    rule="Loop conditions must be Boolean.",
                )

            self.visit_statement(node.body)

    def assignable(self, target_type, source_type):
        if target_type == source_type:
            return True

        # int can be widened to float, but not the reverse.
        if target_type == "float" and source_type == "int":
            return True

        return False

    def expression_type(self, node):
        if isinstance(node, Literal):
            return node.literal_type

        if isinstance(node, Identifier):
            symbol = self.symbol_table.lookup(node.name)

            if symbol is None:
                self.error(
                    "UNDECLARED_VARIABLE",
                    f"Variable '{node.name}' has not been declared.",
                    node,
                    identifier=node.name,
                    rule="An identifier must refer to a declared variable.",
                )
                return None

            return symbol.var_type

        if isinstance(node, ParenthesizedExpression):
            return self.expression_type(node.expression)

        if isinstance(node, UnaryExpression):
            operand_type = self.expression_type(node.operand)

            if operand_type is None:
                return None

            if (
                node.operator == "-"
                and operand_type in NUMERIC_TYPES
            ):
                return operand_type

            if node.operator == "!" and operand_type == "bool":
                return "bool"

            expected = (
                "int or float"
                if node.operator == "-"
                else "bool"
            )

            self.error(
                "INVALID_EXPRESSION",
                f"Unary operator '{node.operator}' cannot be applied "
                f"to type '{operand_type}'.",
                node,
                expected=expected,
                found=operand_type,
                rule="Unary operators require compatible operand types.",
            )
            return None

        if isinstance(node, BinaryExpression):
            left_type = self.expression_type(node.left)
            right_type = self.expression_type(node.right)

            # Avoid cascading operator errors when an operand
            # already contains an undeclared identifier or type error.
            if left_type is None or right_type is None:
                return None

            operator = node.operator

            if operator in {"+", "-", "*", "/"}:
                if (
                    left_type not in NUMERIC_TYPES
                    or right_type not in NUMERIC_TYPES
                ):
                    self.error(
                        "INVALID_EXPRESSION",
                        f"Arithmetic operator '{operator}' requires "
                        "numeric operands.",
                        node,
                        expected="int or float",
                        found=f"{left_type}, {right_type}",
                        rule="Arithmetic operators accept numeric types.",
                    )
                    return None

                if operator == "/":
                    return "float"

                if "float" in {left_type, right_type}:
                    return "float"

                return "int"

            if operator in {"<", ">", "<=", ">="}:
                if (
                    left_type in NUMERIC_TYPES
                    and right_type in NUMERIC_TYPES
                ):
                    return "bool"

                self.error(
                    "INVALID_EXPRESSION",
                    f"Comparison operator '{operator}' requires "
                    "numeric operands.",
                    node,
                    expected="int or float",
                    found=f"{left_type}, {right_type}",
                    rule="Ordered comparisons require numeric types.",
                )
                return None

            if operator in {"==", "!="}:
                compatible = (
                    left_type == right_type
                    or (
                        left_type in NUMERIC_TYPES
                        and right_type in NUMERIC_TYPES
                    )
                )

                if compatible:
                    return "bool"

                self.error(
                    "INVALID_EXPRESSION",
                    f"Cannot compare '{left_type}' and '{right_type}' "
                    f"using '{operator}'.",
                    node,
                    expected=left_type,
                    found=right_type,
                    rule="Equality operands must have compatible types.",
                )
                return None

            if operator in {"&&", "||"}:
                if left_type == "bool" and right_type == "bool":
                    return "bool"

                self.error(
                    "INVALID_EXPRESSION",
                    f"Logical operator '{operator}' requires "
                    "Boolean operands.",
                    node,
                    expected="bool",
                    found=f"{left_type}, {right_type}",
                    rule="Logical operators accept Boolean values.",
                )
                return None

        return None
