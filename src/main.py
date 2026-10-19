import argparse
import json
import sys
from dataclasses import fields, is_dataclass

from .lexer import Lexer
from .parser import Parser
from .semantic_analyzer import SemanticAnalyzer
from .errors import LexerError, ParserError


DEMO_PROGRAM = """
int age = 20;
float height = 5.8;
bool eligible = true;
string name = "MiniLang";
char grade = 'A';

if (eligible && age >= 18) {
    string message = "Hello, " + name;
    grade = 'B';
}
"""


def to_dict(value):
    if is_dataclass(value):
        return {
            "node": type(value).__name__,
            **{
                field.name: to_dict(getattr(value, field.name))
                for field in fields(value)
            }
        }

    if isinstance(value, list):
        return [to_dict(item) for item in value]

    return value


def main():
    argument_parser = argparse.ArgumentParser(
        description="MiniLang educational semantic analyzer"
    )
    argument_parser.add_argument(
        "file", nargs="?", help="Source file to analyze"
    )
    argument_parser.add_argument(
        "--tokens", action="store_true",
        help="Print tokens"
    )
    argument_parser.add_argument(
        "--ast", action="store_true",
        help="Print the abstract syntax tree"
    )
    argument_parser.add_argument(
        "--symbols", action="store_true",
        help="Print declared symbols"
    )

    args = argument_parser.parse_args()

    try:
        if args.file:
            with open(args.file, encoding="utf-8") as source_file:
                source = source_file.read()
        elif not sys.stdin.isatty():
            source = sys.stdin.read()
        else:
            source = DEMO_PROGRAM

        tokens = Lexer(source).tokenize()

        if args.tokens:
            for token in tokens:
                print(token)

        program = Parser(tokens).parse()

        if args.ast:
            print(json.dumps(to_dict(program), indent=2))

        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(program)

        if args.symbols:
            print(analyzer.symbol_table.format_table())

        if errors:
            print("\nSemantic errors:")
            for error in errors:
                print(error)
            return 1

        print("Analysis completed successfully.")
        return 0

    except LexerError as error:
        print(
            f"[Lexical Error] Line {error.line}, "
            f"Column {error.column}: {error}",
            file=sys.stderr
        )
        return 1

    except ParserError as error:
        print(
            f"[Syntax Error] Line {error.line}, "
            f"Column {error.column}: {error}",
            file=sys.stderr
        )
        return 1

    except OSError as error:
        print(f"[File Error] {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())