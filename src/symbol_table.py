from dataclasses import dataclass


@dataclass
class Symbol:
    name: str
    var_type: str
    line: int
    column: int
    scope_level: int


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
        self.symbols = []

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name, var_type, line, column):
        current_scope = self.scopes[-1]

        if name in current_scope:
            return False

        symbol = Symbol(
            name, var_type, line, column, len(self.scopes) - 1
        )
        current_scope[name] = symbol
        self.symbols.append(symbol)
        return True

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def visible_symbols(self):
        visible = {}

        for scope in self.scopes:
            visible.update(scope)

        return list(visible.values())

    def format_table(self):
        rows = [
            "NAME | TYPE | DECLARED AT | SCOPE",
            "-" * 45
        ]

        for symbol in self.symbols:
            rows.append(
                f"{symbol.name} | {symbol.var_type} | "
                f"{symbol.line}:{symbol.column} | "
                f"{symbol.scope_level}"
            )

        return "\n".join(rows)