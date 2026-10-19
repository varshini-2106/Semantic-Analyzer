
from dataclasses import dataclass
from typing import Optional


@dataclass
class SemanticError:
    category: str
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    expected: Optional[str] = None
    actual: Optional[str] = None
    identifier: Optional[str] = None
    rule: Optional[str] = None

    def __str__(self):
        location = ""

        if self.line is not None:
            location = f"Line {self.line}"
            if self.column is not None:
                location += f", Column {self.column}"
            location += ": "

        return f"[{self.category}] {location}{self.message}"


class LexerError(Exception):
    def __init__(self, message, line, column):
        super().__init__(message)
        self.line = line
        self.column = column


class ParserError(Exception):
    def __init__(self, message, line, column):
        super().__init__(message)
        self.line = line
        self.column = column
