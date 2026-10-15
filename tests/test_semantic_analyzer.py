
import unittest

from src.main import analyze_source
from src.lexer import Lexer
from src.parser import Parser
from src.errors import LexerError, ParserError


def categories(source):
    return [error.category for error in analyze_source(source)]


class SemanticAnalyzerTests(unittest.TestCase):

    def test_valid_program(self):
        source = """
        int age;
        float salary;
        bool active;
        age = 21;
        salary = 45000;
        active = true;
        """
        self.assertEqual(categories(source), [])

    def test_int_to_float_assignment(self):
        self.assertEqual(
            categories("float amount; amount = 10;"),
            [],
        )

    def test_float_to_int_assignment(self):
        self.assertIn(
            "TYPE_MISMATCH",
            categories("int amount; amount = 10.5;"),
        )

    def test_duplicate_declaration(self):
        self.assertIn(
            "DUPLICATE_DECLARATION",
            categories("int x; int x;"),
        )

    def test_undeclared_assignment_target(self):
        self.assertIn(
            "UNDECLARED_VARIABLE",
            categories("x = 10;"),
        )

    def test_undeclared_expression_variable(self):
        self.assertIn(
            "UNDECLARED_VARIABLE",
            categories("int x; x = missing + 1;"),
        )

    def test_scope_error(self):
        source = "{ int local; local = 1; } local = 2;"
        self.assertIn(
            "UNDECLARED_VARIABLE",
            categories(source),
        )

    def test_nested_scope_can_access_outer_variable(self):
        source = """
        int outer;
        outer = 5;
        {
            int inner;
            inner = outer + 1;
        }
        """
        self.assertEqual(categories(source), [])

    def test_inner_variable_does_not_escape(self):
        source = """
        {
            int inner;
            inner = 5;
        }
        """
        self.assertIn(
            "UNDECLARED_VARIABLE",
            categories(source + "inner = 10;"),
        )

    def test_boolean_arithmetic_invalid(self):
        source = """
        bool active;
        int result;
        result = active + 1;
        """
        self.assertIn(
            "INVALID_EXPRESSION",
            categories(source),
        )

    def test_operator_precedence(self):
        self.assertEqual(
            categories("int x; x = 2 + 3 * 4;"),
            [],
        )

    def test_parenthesized_expression(self):
        self.assertEqual(
            categories("int x; x = (2 + 3) * 4;"),
            [],
        )

    def test_logical_expression(self):
        source = """
        int x;
        bool result;
        x = 4;
        result = x > 2 && !(x == 0);
        """
        self.assertEqual(categories(source), [])

    def test_invalid_logical_operands(self):
        self.assertIn(
            "INVALID_EXPRESSION",
            categories("bool result; result = 1 && true;"),
        )

    def test_valid_if_else(self):
        source = """
        bool active;
        active = true;
        if (active) {
            int result;
            result = 1;
        } else {
            int result;
            result = 0;
        }
        """
        self.assertEqual(categories(source), [])

    def test_invalid_if_condition(self):
        source = """
        if (10) {
            int x;
            x = 1;
        }
        """
        self.assertIn(
            "INVALID_CONDITION",
            categories(source),
        )

    def test_valid_while_loop(self):
        source = """
        bool running;
        running = true;
        while (running) {
            int count;
            count = 1;
            running = false;
        }
        """
        self.assertEqual(categories(source), [])

    def test_invalid_while_condition(self):
        source = """
        while (5) {
            int x;
            x = 1;
        }
        """
        self.assertIn(
            "INVALID_CONDITION",
            categories(source),
        )

    def test_control_block_scope(self):
        source = """
        if (true) {
            int hidden;
            hidden = 1;
        }
        hidden = 2;
        """
        self.assertIn(
            "UNDECLARED_VARIABLE",
            categories(source),
        )

    def test_nested_control_flow(self):
        source = """
        int age;
        bool active;
        age = 21;
        active = true;

        if (age > 18) {
            while (active) {
                int score;
                score = age + 10;
                active = false;
            }
        }
        """
        self.assertEqual(categories(source), [])

    def test_lexer_error(self):
        with self.assertRaises(LexerError):
            Lexer("int x; @").tokenize()

    def test_parser_error(self):
        with self.assertRaises(ParserError):
            Parser(Lexer("int x").tokenize()).parse()


if __name__ == "__main__":
    unittest.main()
