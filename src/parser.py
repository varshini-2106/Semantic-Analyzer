
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
    from .errors import ParserError
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
    from errors import ParserError


TYPE_TOKENS = {"INT", "FLOAT", "BOOL"}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.current

        if token.type != "EOF":
            self.pos += 1

        return token

    def match(self, *types):
        if self.current.type in types:
            return self.advance()

        return None

    def expect(self, token_type, message=None):
        if self.current.type != token_type:
            token = self.current
            raise ParserError(
                message
                or f"Expected {token_type}, found "
                   f"{token.value or token.type}.",
                token.line,
                token.column,
            )

        return self.advance()

    def expect_punctuation(self, value, message=None):
        if (
            self.current.type != "PUNCT"
            or self.current.value != value
        ):
            token = self.current
            raise ParserError(
                message or f"Expected '{value}'.",
                token.line,
                token.column,
            )

        return self.advance()

    def parse(self):
        statements = []

        while self.current.type != "EOF":
            statements.append(self.statement())

        return Program(statements=statements)

    def statement(self):
        if self.current.type in TYPE_TOKENS:
            return self.declaration()

        if self.current.type == "PUNCT" and self.current.value == "{":
            return self.block()

        if self.current.type == "ID":
            return self.assignment()

        if self.current.type == "IF":
            return self.if_statement()

        if self.current.type == "WHILE":
            return self.while_statement()

        token = self.current
        raise ParserError(
            f"Unexpected token {token.value or token.type} "
            "at start of statement.",
            token.line,
            token.column,
        )

    def declaration(self):
        type_token = self.advance()

        name = self.expect(
            "ID",
            "Expected an identifier after the type.",
        )

        self.expect_punctuation(
            ";",
            "Expected ';' after declaration.",
        )

        return Declaration(
            line=type_token.line,
            column=type_token.column,
            var_type=type_token.value,
            name=name.value,
        )

    def assignment(self):
        name = self.advance()

        if self.current.type != "OP" or self.current.value != "=":
            token = self.current
            raise ParserError(
                "Expected '=' in assignment.",
                token.line,
                token.column,
            )

        self.advance()
        expression = self.expression()

        self.expect_punctuation(
            ";",
            "Expected ';' after assignment.",
        )

        return Assignment(
            line=name.line,
            column=name.column,
            name=name.value,
            expression=expression,
        )

    def block(self):
        start = self.expect_punctuation(
            "{",
            "Expected '{' to start block.",
        )

        statements = []

        while not (
            self.current.type == "PUNCT"
            and self.current.value == "}"
        ):
            if self.current.type == "EOF":
                token = self.current
                raise ParserError(
                    "Unclosed block; expected '}'.",
                    token.line,
                    token.column,
                )

            statements.append(self.statement())

        self.advance()

        return Block(
            line=start.line,
            column=start.column,
            statements=statements,
        )

    def if_statement(self):
        start = self.advance()

        self.expect_punctuation(
            "(",
            "Expected '(' after 'if'.",
        )

        condition = self.expression()

        self.expect_punctuation(
            ")",
            "Expected ')' after if condition.",
        )

        if not (
            self.current.type == "PUNCT"
            and self.current.value == "{"
        ):
            token = self.current
            raise ParserError(
                "Expected a block after the if condition.",
                token.line,
                token.column,
            )

        then_branch = self.block()
        else_branch = None

        if self.match("ELSE"):
            if not (
                self.current.type == "PUNCT"
                and self.current.value == "{"
            ):
                token = self.current
                raise ParserError(
                    "Expected a block after 'else'.",
                    token.line,
                    token.column,
                )

            else_branch = self.block()

        return IfStatement(
            line=start.line,
            column=start.column,
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
        )

    def while_statement(self):
        start = self.advance()

        self.expect_punctuation(
            "(",
            "Expected '(' after 'while'.",
        )

        condition = self.expression()

        self.expect_punctuation(
            ")",
            "Expected ')' after while condition.",
        )

        if not (
            self.current.type == "PUNCT"
            and self.current.value == "{"
        ):
            token = self.current
            raise ParserError(
                "Expected a block after the while condition.",
                token.line,
                token.column,
            )

        body = self.block()

        return WhileStatement(
            line=start.line,
            column=start.column,
            condition=condition,
            body=body,
        )

    # Precedence from lowest to highest:
    # ||, &&, == !=, < > <= >=, + -, * /, unary, primary

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        node = self.logical_and()

        while self.current.type == "OP" and self.current.value == "||":
            operator = self.advance()
            right = self.logical_and()

            node = BinaryExpression(
                line=operator.line,
                column=operator.column,
                left=node,
                operator=operator.value,
                right=right,
            )

        return node

    def logical_and(self):
        node = self.equality()

        while self.current.type == "OP" and self.current.value == "&&":
            operator = self.advance()
            right = self.equality()

            node = BinaryExpression(
                line=operator.line,
                column=operator.column,
                left=node,
                operator=operator.value,
                right=right,
            )

        return node

    def equality(self):
        node = self.relational()

        while (
            self.current.type == "OP"
            and self.current.value in {"==", "!="}
        ):
            operator = self.advance()
            right = self.relational()

            node = BinaryExpression(
                line=operator.line,
                column=operator.column,
                left=node,
                operator=operator.value,
                right=right,
            )

        return node

    def relational(self):
        node = self.additive()

        while (
            self.current.type == "OP"
            and self.current.value in {"<", ">", "<=", ">="}
        ):
            operator = self.advance()
            right = self.additive()

            node = BinaryExpression(
                line=operator.line,
                column=operator.column,
                left=node,
                operator=operator.value,
                right=right,
            )

        return node

    def additive(self):
        node = self.multiplicative()

        while (
            self.current.type == "OP"
            and self.current.value in {"+", "-"}
        ):
            operator = self.advance()
            right = self.multiplicative()

            node = BinaryExpression(
                line=operator.line,
                column=operator.column,
                left=node,
                operator=operator.value,
                right=right,
            )

        return node

    def multiplicative(self):
        node = self.unary()

        while (
            self.current.type == "OP"
            and self.current.value in {"*", "/"}
        ):
            operator = self.advance()
            right = self.unary()

            node = BinaryExpression(
                line=operator.line,
                column=operator.column,
                left=node,
                operator=operator.value,
                right=right,
            )

        return node

    def unary(self):
        if (
            self.current.type == "OP"
            and self.current.value in {"-", "!"}
        ):
            operator = self.advance()
            operand = self.unary()

            return UnaryExpression(
                line=operator.line,
                column=operator.column,
                operator=operator.value,
                operand=operand,
            )

        return self.primary()

    def primary(self):
        token = self.current

        if self.match("INT"):
            return Literal(
                line=token.line,
                column=token.column,
                value=int(token.value),
                literal_type="int",
            )

        if self.match("FLOAT"):
            return Literal(
                line=token.line,
                column=token.column,
                value=float(token.value),
                literal_type="float",
            )

        if self.match("TRUE"):
            return Literal(
                line=token.line,
                column=token.column,
                value=True,
                literal_type="bool",
            )

        if self.match("FALSE"):
            return Literal(
                line=token.line,
                column=token.column,
                value=False,
                literal_type="bool",
            )

        if self.match("ID"):
            return Identifier(
                line=token.line,
                column=token.column,
                name=token.value,
            )

        if token.type == "PUNCT" and token.value == "(":
            self.advance()
            expression = self.expression()

            self.expect_punctuation(
                ")",
                "Expected ')' after expression.",
            )

            return ParenthesizedExpression(
                line=token.line,
                column=token.column,
                expression=expression,
            )

        raise ParserError(
            f"Expected an expression, found "
            f"{token.value or token.type}.",
            token.line,
            token.column,
        )
