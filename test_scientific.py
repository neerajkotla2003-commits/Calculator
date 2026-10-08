"""Run with pytest (existing CI) or python -m unittest -v test_scientific."""

import math
import unittest

from scientific import CalculationError, CalculatorState, evaluate


class ScientificTests(unittest.TestCase):
    def test_arithmetic_and_precedence(self):
        cases = {
            "2 + 3 * 4": 14, "(2 + 3) * 4": 20,
            "2^3": 8, "2**3": 8, "2^3^2": 512,
            "-2^2": -4, "(-2)^2": 4, "2^-3": 0.125,
            "0.1 + 0.2": 0.3, "1e-3 * 1000": 1,
            "9 ÷ 3 + 2 × 4": 11, "2*pi": 2 * math.pi,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertAlmostEqual(evaluate(expression), expected)

    def test_scientific_functions(self):
        cases = {
            "sin(30)": 0.5, "cos(60)": 0.5, "tan(45)": 1,
            "sin(-30)": -0.5, "sqrt(81)": 9, "log(1000)": 3,
            "ln(e)": 1, "abs(-4)": 4, "fact(5)": 120,
            "fact(0)": 1, "sqrt(9) + log(100)": 5,
            "sin(30)^2 + cos(30)^2": 1,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertAlmostEqual(evaluate(expression), expected)

    def test_radians(self):
        self.assertAlmostEqual(evaluate("sin(pi/2)", degrees=False), 1)
        self.assertAlmostEqual(evaluate("cos(pi)", degrees=False), -1)
        self.assertAlmostEqual(evaluate("tan(pi/4)", degrees=False), 1)

    def test_last_answer(self):
        self.assertEqual(evaluate("ans*3", ans=4), 12)

    def test_invalid_domains(self):
        for expression in ("1/0", "sqrt(-1)", "log(0)", "ln(-1)",
                           "fact(-1)", "fact(2.5)", "fact(171)", "tan(90)",
                           "(-1)^0.5", "0^-1"):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    evaluate(expression)

    def test_invalid_radian_tangent(self):
        with self.assertRaises(CalculationError):
            evaluate("tan(pi/2)", degrees=False)

    def test_rejects_non_calculator_expressions(self):
        for expression in ("", "sin(", "2pi", "2//3", "2%3", "[1,2]",
                           "True", "'text'", "(1).__class__", "sqrt(1,2)",
                           "sin(x=30)", "__import__('os')", "[x for x in ()]"):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    evaluate(expression)

    def test_limits(self):
        for expression in ("9^9999", "1e309", "1e308*10", "1" * 301,
                           "+".join(["1"] * 80)):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    evaluate(expression)


class InputBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.model = CalculatorState()

    def test_number_after_result_starts_new_expression(self):
        self.model.insert("2+3")
        self.assertTrue(self.model.solve())
        self.model.insert("7")
        self.assertEqual(self.model.expression, "7")

    def test_continue_from_full_precision_answer(self):
        self.model.insert("1/3")
        self.model.solve()
        self.model.insert("*")
        self.model.insert("3")
        self.model.solve()
        self.assertEqual(self.model.answer, 1.0)

    def test_repeat_equals_does_not_change_ans_formula(self):
        self.model.insert("2")
        self.model.solve()
        self.model.insert("+")
        self.model.insert("3")
        self.model.solve()
        self.model.solve()
        self.assertEqual(self.model.answer, 5)

    def test_square_and_reciprocal_after_result(self):
        self.model.insert("3")
        self.model.solve()
        self.model.wrap("({})^2")
        self.model.solve()
        self.assertEqual(self.model.answer, 9)
        self.model.wrap("1/({})")
        self.model.solve()
        self.assertAlmostEqual(self.model.answer, 1/9)

    def test_errors_preserve_expression_for_correction(self):
        self.model.insert("sqrt(-1)")
        self.assertFalse(self.model.solve())
        self.assertEqual(self.model.expression, "sqrt(-1)")
        self.assertEqual(self.model.result, "Error")

    def test_mode_change_recalculates_formula(self):
        self.model.insert("sin(30)")
        self.model.solve()
        self.assertAlmostEqual(self.model.answer, 0.5)
        self.model.toggle_mode()
        self.model.solve()
        self.assertAlmostEqual(self.model.answer, math.sin(30))

    def test_backspace_and_clear(self):
        self.model.insert("123")
        self.model.backspace()
        self.assertEqual(self.model.expression, "12")
        self.model.solve()
        self.model.clear()
        self.assertEqual(self.model.expression, "")
        self.assertEqual(self.model.answer, 0)


if __name__ == "__main__":
    unittest.main()
