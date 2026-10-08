from ast_nodes import (
    Program, Block, Declaration, Assignment,
    BinaryExpression, Literal, Identifier, ParenthesizedExpression
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
        raise SyntaxError(f"Unexpected token {token.value!r} at line {token.line}")

    def declaration(self):
        var_type = self.advance().value
        name = self.expect("ID").value
        self.expect("SEMICOLON")
        return Declaration(var_type, name)

    def assignment(self):
        name = self.expect("ID").value
        self.expect("ASSIGN")
        expression = self.expression()
        self.expect("SEMICOLON")
        return Assignment(name, expression)

    def block(self):
        self.expect("LBRACE")
        statements = []
        while self.current().type not in ("RBRACE", "EOF"):
            statements.append(self.statement())
        self.expect("RBRACE")
        return Block(statements)

    def expression(self):
        node = self.term()
        while self.current().type in ("PLUS", "MINUS"):
            op = self.advance().value
            node = BinaryExpression(node, op, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current().type in ("MUL", "DIV"):
            op = self.advance().value
            node = BinaryExpression(node, op, self.factor())
        return node

    def factor(self):
        token = self.current()

        if token.type == "INT_LITERAL":
            self.advance()
            return Literal(int(token.value), "int")

        if token.type == "FLOAT_LITERAL":
            self.advance()
            return Literal(float(token.value), "float")

        if token.type == "BOOL_LITERAL":
            self.advance()
            return Literal(token.value == "true", "bool")

        if token.type == "ID":
            self.advance()
            return Identifier(token.value)

        if token.type == "LPAREN":
            self.advance()
            expr = self.expression()
            self.expect("RPAREN")
            return ParenthesizedExpression(expr)

        raise SyntaxError(f"Invalid expression at line {token.line}, column {token.column}")
