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
        with open(sys.argv[1], "r", encoding="utf-8") as file:
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
        print(f"Syntax Error: {error}")
        return

    if errors:
        for error in errors:
            print(error)
    else:
        print("Semantic analysis successful. No semantic errors found.")

if __name__ == "__main__":
    main()
