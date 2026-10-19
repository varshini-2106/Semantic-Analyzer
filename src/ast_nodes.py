from dataclasses import dataclass, field


@dataclass
class Program:
    statements: list = field(default_factory=list)


@dataclass
class Block:
    statements: list = field(default_factory=list)


@dataclass
class Declaration:
    var_type: str
    name: str
    initializer: object = None
    line: int = 0
    column: int = 0


@dataclass
class Assignment:
    name: str
    expression: object
    line: int = 0
    column: int = 0


@dataclass
class IfStatement:
    condition: object
    then_branch: object
    else_branch: object = None
    line: int = 0
    column: int = 0


@dataclass
class WhileStatement:
    condition: object
    body: object
    line: int = 0
    column: int = 0


@dataclass
class BinaryExpression:
    left: object
    operator: str
    right: object
    line: int = 0
    column: int = 0


@dataclass
class UnaryExpression:
    operator: str
    operand: object
    line: int = 0
    column: int = 0


@dataclass
class Literal:
    value: object
    literal_type: str
    line: int = 0
    column: int = 0


@dataclass
class Identifier:
    name: str
    line: int = 0
    column: int = 0


@dataclass
class ParenthesizedExpression:
    expression: object