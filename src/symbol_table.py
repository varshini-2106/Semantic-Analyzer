from dataclasses import dataclass


@dataclass
class Symbol:
    name: str
    var_type: str
    scope_level: int


class SymbolTable:

    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):

        if len(self.scopes) == 1:
            raise RuntimeError(
                "Cannot exit global scope"
            )

        self.scopes.pop()

    @property
    def current_scope_level(self):
        return len(self.scopes) - 1

    def declare(self, name, var_type):

        current = self.scopes[-1]

        if name in current:
            return False

        current[name] = Symbol(
            name=name,
            var_type=var_type,
            scope_level=self.current_scope_level
        )

        return True

    def lookup(self, name):

        for scope in reversed(self.scopes):

            if name in scope:
                return scope[name]

        return None