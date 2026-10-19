import ast

from .ast_nodes import (
    Program, Block, Declaration, Assignment,
    IfStatement, WhileStatement, BinaryExpression,
    UnaryExpression, Literal, Identifier,
    ParenthesizedExpression
)
from .errors import ParserError


TYPE_NAMES = {"int", "float", "bool", "string", "char"}

PRECEDENCE = {
    "||": 1,
    "&&": 2,
    "==": 3, "!=": 3,
    "<": 4, "<=": 4, ">": 4, ">=": 4,
    "+": 5, "-": 5,
    "*": 6, "/": 6,
}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current()
        if token.type != "EOF":
            self.position += 1
        return token

    def match(self, *types):
        if self.current().type in types:
            return self.advance()
        return None

    def expect(self, token_type):
        token = self.current()

        if token.type != token_type:
            raise ParserError(
                f"Expected {token_type}, got {token.type or 'EOF'}.",
                token.line, token.column
            )

        return self.advance()

    def parse(self):
        statements = []

        while self.current().type != "EOF":
            statements.append(self.parse_statement())

        return Program(statements)

    def parse_statement(self):
        token = self.current()

        if token.value in TYPE_NAMES:
            return self.parse_declaration()

        if token.type == "ID":
            return self.parse_assignment()

        if token.type == "{":
            return self.parse_block()

        if token.type == "IF":
            return self.parse_if()

        if token.type == "WHILE":
            return self.parse_while()

        raise ParserError(
            f"Unexpected token {token.value!r}.",
            token.line, token.column
        )

    def parse_declaration(self):
        type_token = self.advance()
        name_token = self.expect("ID")

        initializer = None
        if self.match("="):
            initializer = self.parse_expression()

        self.expect(";")

        return Declaration(
            type_token.value, name_token.value, initializer,
            type_token.line, type_token.column
        )

    def parse_assignment(self):
        name_token = self.expect("ID")
        self.expect("=")
        expression = self.parse_expression()
        self.expect(";")

        return Assignment(
            name_token.value, expression,
            name_token.line, name_token.column
        )

    def parse_block(self):
        self.expect("{")
        statements = []

        while self.current().type not in {"}", "EOF"}:
            statements.append(self.parse_statement())

        self.expect("}")
        return Block(statements)

    def parse_if(self):
        token = self.expect("IF")
        self.expect("(")
        condition = self.parse_expression()
        self.expect(")")
        then_branch = self.parse_statement()

        else_branch = None
        if self.match("ELSE"):
            else_branch = self.parse_statement()

        return IfStatement(
            condition, then_branch, else_branch,
            token.line, token.column
        )

    def parse_while(self):
        token = self.expect("WHILE")
        self.expect("(")
        condition = self.parse_expression()
        self.expect(")")
        body = self.parse_statement()

        return WhileStatement(
            condition, body, token.line, token.column
        )

    def parse_expression(self, min_precedence=1):
        left = self.parse_unary()

        while True:
            operator = self.current().value
            precedence = PRECEDENCE.get(operator, 0)

            if precedence < min_precedence:
                break

            op_token = self.advance()
            right = self.parse_expression(precedence + 1)

            left = BinaryExpression(
                left, op_token.value, right,
                op_token.line, op_token.column
            )

        return left

    def parse_unary(self):
        token = self.current()

        if token.value in {"!", "-"}:
            self.advance()
            return UnaryExpression(
                token.value, self.parse_unary(),
                token.line, token.column
            )

        return self.parse_primary()

    def parse_primary(self):
        token = self.current()

        if self.match("INT"):
            return Literal(
                int(token.value), "int", token.line, token.column
            )

        if self.match("FLOAT"):
            return Literal(
                float(token.value), "float", token.line, token.column
            )

        if self.match("STRING"):
            try:
                value = ast.literal_eval(token.value)
            except (ValueError, SyntaxError):
                raise ParserError(
                    "Invalid string escape sequence.",
                    token.line, token.column
                )
            return Literal(
                value, "string", token.line, token.column
            )

        if self.match("CHAR"):
            try:
                value = ast.literal_eval(token.value)
            except (ValueError, SyntaxError):
                raise ParserError(
                    "Invalid character literal.",
                    token.line, token.column
                )

            if not isinstance(value, str) or len(value) != 1:
                raise ParserError(
                    "A character literal must contain one character.",
                    token.line, token.column
                )

            return Literal(
                value, "char", token.line, token.column
            )

        if self.match("TRUE"):
            return Literal(
                True, "bool", token.line, token.column
            )

        if self.match("FALSE"):
            return Literal(
                False, "bool", token.line, token.column
            )

        if self.match("ID"):
            return Identifier(
                token.value, token.line, token.column
            )

        if self.match("("):
            expression = self.parse_expression()
            self.expect(")")
            return ParenthesizedExpression(expression)

        raise ParserError(
            f"Expected an expression, got {token.value!r}.",
            token.line, token.column
        )