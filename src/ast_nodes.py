from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Program:
    statements: list


@dataclass
class Block:
    statements: list
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class Declaration:
    var_type: str
    name: str
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class Assignment:
    name: str
    expression: Any
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class BinaryExpression:
    left: Any
    operator: str
    right: Any
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class Literal:
    value: Any
    value_type: str
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class Identifier:
    name: str
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class ParenthesizedExpression:
    expression: Any
    line: Optional[int] = None
    column: Optional[int] = None