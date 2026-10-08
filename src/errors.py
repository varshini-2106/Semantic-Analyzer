class SemanticError:
    def __init__(self, message, line=None):
        self.message = message
        self.line = line

    def __str__(self):
        if self.line is not None:
            return f"Semantic Error (line {self.line}): {self.message}"
        return f"Semantic Error: {self.message}"
