import re
from token import Token

KEYWORDS = {
    "int": "INT",
    "float": "FLOAT",
    "bool": "BOOL",
    "true": "BOOL_LITERAL",
    "false": "BOOL_LITERAL",
}

TOKEN_SPEC = [
    ("NUMBER",      r"\d+(?:\.\d+)?"),
    ("ID",          r"[A-Za-z_][A-Za-z0-9_]*"),
    ("EQ",          r"=="),
    ("NE",          r"!="),
    ("LE",          r"<="),
    ("GE",          r">="),
    ("PLUS",        r"\+"),
    ("MINUS",       r"-"),
    ("MUL",         r"\*"),
    ("DIV",         r"/"),
    ("ASSIGN",      r"="),
    ("LT",          r"<"),
    ("GT",          r">"),
    ("LPAREN",      r"\("),
    ("RPAREN",      r"\)"),
    ("LBRACE",      r"\{"),
    ("RBRACE",      r"\}"),
    ("SEMICOLON",   r";"),
    ("SKIP",        r"[ \t]+"),
    ("NEWLINE",     r"\n"),
    ("MISMATCH",    r"."),
]

MASTER_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))

def tokenize(source):
    tokens = []
    line = 1
    column = 1

    for match in MASTER_RE.finditer(source):
        kind = match.lastgroup
        value = match.group()

        if kind == "NEWLINE":
            line += 1
            column = 1
            continue

        if kind == "SKIP":
            column += len(value)
            continue

        if kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character {value!r} at line {line}, column {column}")

        if kind == "ID":
            kind = KEYWORDS.get(value, "ID")
        elif kind == "NUMBER":
            kind = "FLOAT_LITERAL" if "." in value else "INT_LITERAL"

        tokens.append(Token(kind, value, line, column))
        column += len(value)

    tokens.append(Token("EOF", "", line, column))
    return tokens
