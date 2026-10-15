
from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class Node:
    line: int = 1
    column: int = 1


@dataclass
class Program(Node):
    statements: List[Any] = field(default_factory=list)


@dataclass
class Block(Node):
    statements: List[Any] = field(default_factory=list)


@dataclass
class Declaration(Node):
    var_type: str = "int"
    name: str = ""


@dataclass
class Assignment(Node):
    name: str = ""
    expression: Any = None


@dataclass
class IfStatement(Node):
    condition: Any = None
    then_branch: Any = None
    else_branch: Any = None


@dataclass
class WhileStatement(Node):
    condition: Any = None
    body: Any = None


@dataclass
class BinaryExpression(Node):
    left: Any = None
    operator: str = ""
    right: Any = None


@dataclass
class UnaryExpression(Node):
    operator: str = ""
    operand: Any = None


@dataclass
class Literal(Node):
    value: Any = None
    literal_type: str = "int"


@dataclass
class Identifier(Node):
    name: str = ""


@dataclass
class ParenthesizedExpression(Node):
    expression: Any = None
