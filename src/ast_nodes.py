from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Program:
    statements: list

@dataclass
class Block:
    statements: list

@dataclass
class Declaration:
    var_type: str
    name: str

@dataclass
class Assignment:
    name: str
    expression: Any

@dataclass
class BinaryExpression:
    left: Any
    operator: str
    right: Any

@dataclass
class Literal:
    value: Any
    value_type: str

@dataclass
class Identifier:
    name: str

@dataclass
class ParenthesizedExpression:
    expression: Any
