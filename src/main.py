
import argparse
import sys
from pathlib import Path

try:
    from .lexer import Lexer
    from .parser import Parser
    from .semantic_analyzer import SemanticAnalyzer
    from .errors import LexerError, ParserError
except ImportError:
    from lexer import Lexer
    from parser import Parser
    from semantic_analyzer import SemanticAnalyzer
    from errors import LexerError, ParserError


DEFAULT_SOURCE = """
// MiniLang demonstration
int age;
float salary;
bool eligible;

age = 21;
salary = 45000;
eligible = age >= 18;

if (eligible) {
    int score;
    score = 95;
} else {
    int score;
    score = 50;
}

while (eligible) {
    eligible = false;
}
"""


def analyze_source(source):
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(program)

    return errors


def main():
    cli = argparse.ArgumentParser(
        description="Semantic Analyzer for MiniLang"
    )

    cli.add_argument(
        "file",
        nargs="?",
        help="Path to a MiniLang source file",
    )

    cli.add_argument(
        "--stdin",
        action="store_true",
        help="Read source code from standard input",
    )

    cli.add_argument(
        "--tokens",
        action="store_true",
        help="Display lexer tokens instead of semantic results",
    )

    args = cli.parse_args()

    if args.stdin and args.file:
        cli.error("Provide either a file or --stdin, not both.")

    try:
        if args.stdin:
            source = sys.stdin.read()
        elif args.file:
            source = Path(args.file).read_text(encoding="utf-8")
        else:
            source = DEFAULT_SOURCE

        tokens = Lexer(source).tokenize()

        if args.tokens:
            for token in tokens:
                print(token)
            return

        program = Parser(tokens).parse()
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(program)

        if errors:
            print(
                f"Semantic analysis completed with "
                f"{len(errors)} error(s):\n"
            )

            for index, error in enumerate(errors, start=1):
                print(f"{index}. {error}\n")

            sys.exit(1)

        print("Semantic analysis successful.")
        print("No semantic errors found.")

    except LexerError as exc:
        print(
            f"[LEXICAL ERROR] Line {exc.line}, "
            f"Column {exc.column}: {exc}"
        )
        sys.exit(2)

    except ParserError as exc:
        print(
            f"[SYNTAX ERROR] Line {exc.line}, "
            f"Column {exc.column}: {exc}"
        )
        sys.exit(2)

    except OSError as exc:
        print(f"[FILE ERROR] {exc}")
        sys.exit(2)


if __name__ == "__main__":
    main()
