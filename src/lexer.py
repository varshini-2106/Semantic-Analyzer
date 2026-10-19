
import re

from .token_model import Token
from .errors import LexerError


TOKEN_PATTERN = re.compile(
    r"(?P<SPACE>[ \t\r]+)"
    r"|(?P<NEWLINE>\n)"
    r"|(?P<COMMENT>//[^\n]*)"
    r'|(?P<STRING>"(?:\\.|[^"\\])*")'
    r"|(?P<CHAR>'(?:\\.|[^'\\])*')"
    r"|(?P<FLOAT>(?:\d+\.\d+|\.\d+))"
    r"|(?P<INT>\d+)"
    r"|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<OP>==|!=|<=|>=|&&|\|\||[+\-*/=!<>])"
    r"|(?P<PUNCT>[{}();,])"
)

KEYWORDS = {
    "int",
    "float",
    "bool",
    "string",
    "char",
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
                raise LexerError(
                    f"Unexpected character {self.source[index]!r}.",
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

                    if kind == "CHAR":
                        # A char must contain one character or
                        # one simple escape sequence, such as '\n'.
                        content = value[1:-1]

                        if len(content) != 1 and not (
                            len(content) == 2
                            and content[0] == "\\"
                        ):
                            raise LexerError(
                                "A character literal must contain "
                                "exactly one character.",
                                line,
                                column,
                            )

                    if kind == "STRING":
                        token_type = "STRING"

                    elif kind == "CHAR":
                        token_type = "CHAR"

                    elif kind == "ID" and value in KEYWORDS:
                        token_type = value.upper()

                    elif kind in {"OP", "PUNCT"}:
                        # The parser expects literal token types,
                        # such as '=', ';', '(', and '{'.
                        token_type = value

                    else:
                        token_type = kind

                    tokens.append(
                        Token(
                            token_type,
                            value,
                            line,
                            column,
                        )
                    )

                column += len(value)

            index = match.end()

        tokens.append(Token("EOF", "", line, column))
        return tokens
