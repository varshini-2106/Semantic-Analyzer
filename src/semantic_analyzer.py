
"""Semantic analyzer for MiniLang."""

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
VALID_TYPES = {"int", "float", "bool", "string", "char"}


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
        """Record a semantic error."""
        details = message

        if expected is not None:
            details += f" Expected: {expected}."
        if found is not None:
            details += f" Found: {found}."
        if rule is not None:
            details += f" Rule: {rule}"

        error = SemanticError(
            category=category,
            message=details,
            line=getattr(node, "line", 0),
            column=getattr(node, "column", 0),
        )

        # Preserve optional metadata when supported by the error class.
        for name, value in (
            ("expected", expected),
            ("actual", found),
            ("found", found),
            ("rule", rule),
            ("identifier", identifier),
        ):
            if value is not None:
                try:
                    setattr(error, name, value)
                except (AttributeError, TypeError):
                    pass

        self.errors.append(error)

    def analyze(self, program):
        """Analyze a program and return its semantic errors."""
        self.symbol_table = SymbolTable()
        self.errors = []

        for statement in program.statements:
            self.visit_statement(statement)

        return self.errors

    def assignable(self, target_type, source_type):
        """Check assignment compatibility."""
        if target_type == source_type:
            return True

        # Allow widening from int to float.
        if target_type == "float" and source_type == "int":
            return True

        return False

    def check_condition(self, expression, statement_name):
        """Conditions in MiniLang must have Boolean type."""
        condition_type = self.expression_type(expression)

        if condition_type is not None and condition_type != "bool":
            self.error(
                "INVALID_CONDITION",
                f"A {statement_name} condition must be Boolean.",
                expression,
                expected="bool",
                found=condition_type,
                rule="Conditional expressions must evaluate to Boolean.",
            )

    def visit_statement(self, node):
        if isinstance(node, Declaration):
            if node.var_type not in VALID_TYPES:
                self.error(
                    "INVALID_TYPE",
                    f"Unknown type '{node.var_type}' for variable "
                    f"'{node.name}'.",
                    node,
                    expected=", ".join(sorted(VALID_TYPES)),
                    found=node.var_type,
                    identifier=node.name,
                )
                return

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
                    rule="A variable can be declared only once per scope.",
                )
                return

            if node.initializer is not None:
                initializer_type = self.expression_type(node.initializer)

                if (
                    initializer_type is not None
                    and not self.assignable(node.var_type, initializer_type)
                ):
                    self.error(
                        "TYPE_MISMATCH",
                        f"Cannot initialize '{node.var_type}' variable "
                        f"'{node.name}' with '{initializer_type}'.",
                        node,
                        expected=node.var_type,
                        found=initializer_type,
                        identifier=node.name,
                    )

        elif isinstance(node, Assignment):
            symbol = self.symbol_table.lookup(node.name)
            expression_type = self.expression_type(node.expression)

            if symbol is None:
                self.error(
                    "UNDECLARED_VARIABLE",
                    f"Variable '{node.name}' has not been declared.",
                    node,
                    identifier=node.name,
                    rule="A variable must be declared before assignment.",
                )
                return

            if (
                expression_type is not None
                and not self.assignable(symbol.var_type, expression_type)
            ):
                self.error(
                    "TYPE_MISMATCH",
                    f"Cannot assign '{expression_type}' to "
                    f"'{symbol.var_type}' variable '{node.name}'.",
                    node,
                    expected=symbol.var_type,
                    found=expression_type,
                    identifier=node.name,
                )

        elif isinstance(node, Block):
            self.symbol_table.enter_scope()
            try:
                for statement in node.statements:
                    self.visit_statement(statement)
            finally:
                self.symbol_table.exit_scope()

        elif isinstance(node, IfStatement):
            self.check_condition(node.condition, "if")
            self.visit_statement(node.then_branch)

            if node.else_branch is not None:
                self.visit_statement(node.else_branch)

        elif isinstance(node, WhileStatement):
            self.check_condition(node.condition, "while")
            self.visit_statement(node.body)

    def expression_type(self, node):
        """Infer expression types and validate operators."""

        if isinstance(node, ParenthesizedExpression):
            return self.expression_type(node.expression)

        if isinstance(node, Literal):
            literal_type = getattr(node, "literal_type", None)

            if literal_type is not None:
                return literal_type

            value = node.value

            if isinstance(value, bool):
                return "bool"
            if isinstance(value, int):
                return "int"
            if isinstance(value, float):
                return "float"
            if isinstance(value, str):
                return "string"

            return None

        if isinstance(node, Identifier):
            symbol = self.symbol_table.lookup(node.name)

            if symbol is None:
                self.error(
                    "UNDECLARED_VARIABLE",
                    f"Variable '{node.name}' has not been declared.",
                    node,
                    identifier=node.name,
                    rule="An identifier must be declared before use.",
                )
                return None

            return symbol.var_type

        if isinstance(node, UnaryExpression):
            operand_type = self.expression_type(node.operand)

            if operand_type is None:
                return None

            operator = node.operator

            if operator == "-":
                if operand_type not in NUMERIC_TYPES:
                    self.error(
                        "INVALID_EXPRESSION",
                        "Unary '-' requires a numeric operand.",
                        node,
                        expected="int or float",
                        found=operand_type,
                    )
                    return None

                return operand_type

            if operator == "!":
                if operand_type != "bool":
                    self.error(
                        "INVALID_EXPRESSION",
                        "Operator '!' requires a Boolean operand.",
                        node,
                        expected="bool",
                        found=operand_type,
                    )
                    return None

                return "bool"

            self.error(
                "INVALID_EXPRESSION",
                f"Unsupported unary operator '{operator}'.",
                node,
                found=operand_type,
            )
            return None

        if isinstance(node, BinaryExpression):
            left_type = self.expression_type(node.left)
            right_type = self.expression_type(node.right)

            if left_type is None or right_type is None:
                return None

            operator = node.operator

            # String concatenation.
            if (
                operator == "+"
                and left_type == "string"
                and right_type == "string"
            ):
                return "string"

            # Boolean logical operators.
            if operator in ("&&", "||"):
                if left_type != "bool" or right_type != "bool":
                    self.error(
                        "INVALID_EXPRESSION",
                        f"Operator '{operator}' requires Boolean operands.",
                        node,
                        expected="bool and bool",
                        found=f"{left_type} {operator} {right_type}",
                    )
                    return None

                return "bool"

            # Numeric arithmetic operators.
            if operator in ("+", "-", "*", "/"):
                if (
                    left_type not in NUMERIC_TYPES
                    or right_type not in NUMERIC_TYPES
                ):
                    self.error(
                        "INVALID_EXPRESSION",
                        f"Operator '{operator}' requires numeric operands.",
                        node,
                        expected="int or float operands",
                        found=f"{left_type} {operator} {right_type}",
                    )
                    return None

                if operator == "/" or (
                    left_type == "float" or right_type == "float"
                ):
                    return "float"

                return "int"

            # Numeric ordered comparisons.
            if operator in ("<", ">", "<=", ">="):
                if (
                    left_type not in NUMERIC_TYPES
                    or right_type not in NUMERIC_TYPES
                ):
                    self.error(
                        "INVALID_EXPRESSION",
                        f"Operator '{operator}' requires numeric operands.",
                        node,
                        expected="int or float operands",
                        found=f"{left_type} {operator} {right_type}",
                    )
                    return None

                return "bool"

            # Equality supports matching types and mixed numeric types.
            if operator in ("==", "!="):
                compatible = (
                    left_type == right_type
                    or (
                        left_type in NUMERIC_TYPES
                        and right_type in NUMERIC_TYPES
                    )
                )

                if not compatible:
                    self.error(
                        "INVALID_EXPRESSION",
                        "Equality operands have incompatible types.",
                        node,
                        expected=left_type,
                        found=right_type,
                    )
                    return None

                return "bool"

            self.error(
                "INVALID_EXPRESSION",
                f"Unsupported binary operator '{operator}'.",
                node,
                found=f"{left_type} {operator} {right_type}",
            )
            return None

        self.error(
            "INVALID_EXPRESSION",
            f"Unsupported expression node '{type(node).__name__}'.",
            node,
        )
        return None
