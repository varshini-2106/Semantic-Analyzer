
from dataclasses import dataclass


@dataclass
class Symbol:
    name: str
    var_type: str
    scope_level: int
    line: int
    column: int


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    @property
    def scope_level(self):
        return len(self.scopes) - 1

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name, var_type, line=1, column=1):
        current_scope = self.scopes[-1]

        if name in current_scope:
            return False

        current_scope[name] = Symbol(
            name=name,
            var_type=var_type,
            scope_level=self.scope_level,
            line=line,
            column=column,
        )

        return True

    def lookup_current(self, name):
        return self.scopes[-1].get(name)

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

        return None
