import sys

from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


def analyze_source(source):

    tokens = tokenize(source)

    tree = Parser(tokens).parse()

    analyzer = SemanticAnalyzer()

    errors = analyzer.analyze(tree)

    return errors


def main():

    if len(sys.argv) > 1:

        with open(
            sys.argv[1],
            "r",
            encoding="utf-8"
        ) as file:

            source = file.read()

    else:

        source = """int x;
float y;
x = 10;
y = x + 5.5;
"""

    try:

        errors = analyze_source(source)

    except SyntaxError as error:

        print("\n=== SYNTAX ERROR ===")
        print(error)
        return

    print("\n========================================")
    print("       SEMANTIC ANALYZER")
    print("========================================")

    if errors:

        print(
            f"\nSemantic analysis completed with "
            f"{len(errors)} error(s).\n"
        )

        for index, error in enumerate(
            errors,
            start=1
        ):

            print(
                f"---------- Error {index} ----------"
            )

            print(error)

            print()

    else:

        print(
            "\nSemantic analysis successful."
        )

        print(
            "No semantic errors found."
        )


if __name__ == "__main__":
    main()