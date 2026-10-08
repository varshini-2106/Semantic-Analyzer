from ast_nodes import (
    Program,
    Block,
    Declaration,
    Assignment,
    BinaryExpression,
    Literal,
    Identifier,
    ParenthesizedExpression
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.current()
        self.pos += 1
        return token

    def expect(self, token_type):
        token = self.current()

        if token.type != token_type:
            raise SyntaxError(
                f"Expected {token_type}, got {token.type} "
                f"at line {token.line}, column {token.column}"
            )

        return self.advance()

    def parse(self):
        statements = []

        while self.current().type != "EOF":
            statements.append(self.statement())

        return Program(statements)

    def statement(self):
        if self.current().type in ("INT", "FLOAT", "BOOL"):
            return self.declaration()

        if self.current().type == "ID":
            return self.assignment()

        if self.current().type == "LBRACE":
            return self.block()

        token = self.current()

        raise SyntaxError(
            f"Unexpected token {token.value!r} at "
            f"line {token.line}, column {token.column}"
        )

    def declaration(self):
        type_token = self.advance()

        name_token = self.expect("ID")

        self.expect("SEMICOLON")

        return Declaration(
            var_type=type_token.value,
            name=name_token.value,
            line=type_token.line,
            column=type_token.column
        )

    def assignment(self):
        name_token = self.expect("ID")

        self.expect("ASSIGN")

        expression = self.expression()

        self.expect("SEMICOLON")

        return Assignment(
            name=name_token.value,
            expression=expression,
            line=name_token.line,
            column=name_token.column
        )

    def block(self):
        opening_brace = self.expect("LBRACE")

        statements = []

        while self.current().type not in ("RBRACE", "EOF"):
            statements.append(self.statement())

        self.expect("RBRACE")

        return Block(
            statements=statements,
            line=opening_brace.line,
            column=opening_brace.column
        )

    def expression(self):
        node = self.term()

        while self.current().type in ("PLUS", "MINUS"):
            operator_token = self.advance()

            right = self.term()

            node = BinaryExpression(
                left=node,
                operator=operator_token.value,
                right=right,
                line=operator_token.line,
                column=operator_token.column
            )

        return node

    def term(self):
        node = self.factor()

        while self.current().type in ("MUL", "DIV"):
            operator_token = self.advance()

            right = self.factor()

            node = BinaryExpression(
                left=node,
                operator=operator_token.value,
                right=right,
                line=operator_token.line,
                column=operator_token.column
            )

        return node

    def factor(self):
        token = self.current()

        if token.type == "INT_LITERAL":
            self.advance()

            return Literal(
                value=int(token.value),
                value_type="int",
                line=token.line,
                column=token.column
            )

        if token.type == "FLOAT_LITERAL":
            self.advance()

            return Literal(
                value=float(token.value),
                value_type="float",
                line=token.line,
                column=token.column
            )

        if token.type == "BOOL_LITERAL":
            self.advance()

            return Literal(
                value=(token.value == "true"),
                value_type="bool",
                line=token.line,
                column=token.column
            )

        if token.type == "ID":
            self.advance()

            return Identifier(
                name=token.value,
                line=token.line,
                column=token.column
            )

        if token.type == "LPAREN":
            opening_paren = self.advance()

            expr = self.expression()

            self.expect("RPAREN")

            return ParenthesizedExpression(
                expression=expr,
                line=opening_paren.line,
                column=opening_paren.column
            )

        raise SyntaxError(
            f"Invalid expression at line {token.line}, "
            f"column {token.column}"
        )