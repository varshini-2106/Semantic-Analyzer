
import unittest

from src.lexer import Lexer
from src.parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.errors import LexerError, ParserError


def analyze(source):
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(program)
    return errors, analyzer


class MiniLangTests(unittest.TestCase):

    # ORIGINAL SEMANTIC ANALYZER TESTS

    def test_valid_types(self):
        source = """
        int age = 20;
        float height = 5.8;
        bool active = true;
        string name = "MiniLang";
        char grade = 'A';
        """
        errors, _ = analyze(source)
        self.assertEqual(errors, [])

    def test_int_to_float(self):
        errors, _ = analyze("float number = 5;")
        self.assertEqual(errors, [])

    def test_invalid_assignment(self):
        errors, _ = analyze("int age; age = true;")
        self.assertTrue(errors)

    def test_undeclared_variable(self):
        errors, _ = analyze("age = 10;")
        self.assertTrue(errors)

    def test_duplicate_declaration(self):
        errors, _ = analyze("int x; int x;")
        self.assertTrue(errors)

    def test_boolean_condition(self):
        errors, _ = analyze("if (5) { int x; }")
        self.assertTrue(errors)

    def test_nested_scope(self):
        errors, _ = analyze("{ int inside; } inside = 3;")
        self.assertTrue(errors)

    def test_string_concatenation(self):
        errors, _ = analyze(
            'string greeting = "Hello " + "world";'
        )
        self.assertEqual(errors, [])

    def test_char_string_mismatch(self):
        errors, _ = analyze('char grade = "ABC";')
        self.assertTrue(errors)

    def test_invalid_operator(self):
        errors, _ = analyze("bool result = true + 5;")
        self.assertTrue(errors)

    def test_invalid_character_literal(self):
        with self.assertRaises(LexerError):
            Lexer("char grade = 'AB';").tokenize()

    def test_syntax_error(self):
        with self.assertRaises(ParserError):
            Parser(Lexer("int x = ;").tokenize()).parse()

    # STRING DECLARATION AND ASSIGNMENT TESTS

    def test_string_declaration(self):
        errors, _ = analyze('string name = "Varshini";')
        self.assertEqual(errors, [])

    def test_string_assignment(self):
        errors, _ = analyze(
            'string name = "Hello"; name = "MiniLang";'
        )
        self.assertEqual(errors, [])

    def test_string_variable_assignment(self):
        errors, _ = analyze(
            'string first = "Hello"; '
            'string second = "World"; '
            'first = second;'
        )
        self.assertEqual(errors, [])

    def test_string_concatenation_assignment(self):
        errors, _ = analyze(
            'string greeting = "Hello " + "World";'
        )
        self.assertEqual(errors, [])

    def test_string_equality(self):
        errors, _ = analyze(
            'string a = "hello"; '
            'string b = "hello"; '
            'bool same = a == b;'
        )
        self.assertEqual(errors, [])

    def test_string_assigned_char(self):
        errors, _ = analyze("string name = 'A';")
        self.assertTrue(errors)

    def test_invalid_string_plus_integer(self):
        errors, _ = analyze(
            'string result = "Age: " + 10;'
        )
        self.assertTrue(errors)

    def test_string_with_escape(self):
        errors, _ = analyze(r'string message = "Hello\nWorld";')
        self.assertEqual(errors, [])

    # CHAR DECLARATION AND ASSIGNMENT TESTS

    def test_char_declaration(self):
        errors, _ = analyze("char grade = 'A';")
        self.assertEqual(errors, [])

    def test_char_assignment(self):
        errors, _ = analyze(
            "char grade = 'A'; grade = 'B';"
        )
        self.assertEqual(errors, [])

    def test_char_variable_assignment(self):
        errors, _ = analyze(
            "char first = 'A'; "
            "char second = 'B'; "
            "first = second;"
        )
        self.assertEqual(errors, [])

    def test_char_assigned_string(self):
        errors, _ = analyze('char grade = "A";')
        self.assertTrue(errors)

    def test_char_equality(self):
        errors, _ = analyze(
            "char grade = 'A'; "
            "bool result = grade == 'A';"
        )
        self.assertEqual(errors, [])

    def test_invalid_char_plus_char(self):
        errors, _ = analyze(
            "char result = 'A' + 'B';"
        )
        self.assertTrue(errors)

    def test_empty_char_literal(self):
        with self.assertRaises(LexerError):
            Lexer("char grade = '';").tokenize()

    def test_multiple_character_literal(self):
        with self.assertRaises(LexerError):
            Lexer("char grade = 'ABC';").tokenize()

    def test_char_with_escape(self):
        errors, _ = analyze(r"char newline = '\n';")
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
