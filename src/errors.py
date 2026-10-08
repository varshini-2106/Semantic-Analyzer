class SemanticError:
    def __init__(
        self,
        category,
        message,
        line=None,
        column=None,
        details=None,
        rule=None
    ):
        self.category = category
        self.message = message
        self.line = line
        self.column = column
        self.details = details or {}
        self.rule = rule

    def __str__(self):
        location = ""

        if self.line is not None:
            location = f"Line {self.line}"

            if self.column is not None:
                location += f", Column {self.column}"

        output = [
            f"[{self.category}]"
        ]

        if location:
            output.append(location)

        output.append("")
        output.append(self.message)

        if self.details:
            output.append("")

            for key, value in self.details.items():
                output.append(f"{key}: {value}")

        if self.rule:
            output.append("")
            output.append(f"Rule: {self.rule}")

        return "\n".join(output)