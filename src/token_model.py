from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    column: int

    def __repr__(self):
        return (
            f"Token({self.type!r}, {self.value!r}, "
            f"line={self.line}, column={self.column})"
        )