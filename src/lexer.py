
import re

try:
    from .token_model import Token
    from .errors import LexerError
except ImportError:
    from token_model import Token
    from errors import LexerError


TOKEN_PATTERN = re.compile(
    r"(?P<SPACE>[ \t\r]+)"
    r"|(?P<NEWLINE>\n)"
    r"|(?P<COMMENT>//[^\n]*)"
    r"|(?P<FLOAT>(?:\d+\.\d+|\d+\.(?!\.)|\.\d+))"
    r"|(?P<INT>\d+)"
    r"|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<OP>==|!=|<=|>=|&&|\|\||[+\-*/=!<>])"
    r"|(?P<PUNCT>[{}();])"
)

KEYWORDS = {
    "int",
    "float",
    "bool",
    "true",
    "false",
    "if",
    "else",
    "while",
}


class Lexer:
    def __init__(self, source):
        self.source = source

    def tokenize(self):
        tokens = []
        index = 0
        line = 1
        column = 1

        while index < len(self.source):
            match = TOKEN_PATTERN.match(self.source, index)

            if match is None:
                character = self.source[index]
                raise LexerError(
                    f"Unexpected character {character!r}.",
                    line,
                    column,
                )

            kind = match.lastgroup
            value = match.group()

            if kind == "NEWLINE":
                line += 1
                column = 1
            else:
                if kind not in {"SPACE", "COMMENT"}:
                    token_type = kind

                    if kind == "ID" and value in KEYWORDS:
                        token_type = value.upper()

                    tokens.append(
                        Token(token_type, value, line, column)
                    )

                column += len(value)

            index = match.end()

        tokens.append(Token("EOF", "", line, column))
        return tokens
