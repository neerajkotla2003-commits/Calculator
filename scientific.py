"""Scientific arithmetic and input state, independent of the desktop window.

Uses Python's math module and a small AST allowlist, never eval().
The original calculator.py remains responsible for basic arithmetic.
"""

import ast
import math

from calculator import calculate


class CalculationError(ValueError):
    """An expression that the calculator cannot evaluate."""


def _finite(value):
    if type(value) not in (int, float):
        raise CalculationError("Only real numbers are supported")
    value = float(value)
    if not math.isfinite(value):
        raise CalculationError("Result is too large")
    return value


def _factorial(value):
    if not value.is_integer() or not 0 <= value <= 170:
        raise CalculationError("Factorial needs a whole number from 0 to 170")
    return math.factorial(int(value))


def evaluate(expression, degrees=True, ans=0.0):
    """Evaluate real arithmetic. sin/cos/tan use degrees by default.

    Supported: + - * / ^ **, parentheses, pi, e, ans,
    sin, cos, tan, sqrt, log (base 10), ln, fact and abs.
    Explicit multiplication is required: 2*pi, not 2pi.
    """
    expression = expression.strip()
    if not expression:
        raise CalculationError("Enter a calculation")
    if len(expression) > 300:
        raise CalculationError("Expression is too long")
    expression = (expression.replace("×", "*").replace("÷", "/")
                  .replace("−", "-").replace("π", "pi").replace("^", "**"))

    def angle(value):
        return math.radians(value) if degrees else value

    def tangent(value):
        radians = angle(value)
        if math.isclose(math.cos(radians), 0.0, abs_tol=1e-15):
            raise CalculationError("Tangent is undefined at this angle")
        return math.tan(radians)

    functions = {
        "sin": lambda value: math.sin(angle(value)),
        "cos": lambda value: math.cos(angle(value)),
        "tan": tangent,
        "sqrt": math.sqrt,
        "log": math.log10,
        "ln": math.log,
        "fact": _factorial,
        "abs": abs,
    }
    operators = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}

    def visit(node):
        if isinstance(node, ast.Constant):
            return _finite(node.value)
        if isinstance(node, ast.Name):
            constants = {"pi": math.pi, "e": math.e, "ans": ans}
            if node.id in constants:
                return _finite(constants[node.id])
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -visit(node.operand)
            if isinstance(node.op, ast.UAdd):
                return visit(node.operand)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow):
                return _finite(math.pow(left, right))
            symbol = operators.get(type(node.op))
            if symbol:
                return _finite(calculate(left, right, symbol))
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in functions and len(node.args) == 1
                and not node.keywords):
            return _finite(functions[node.func.id](visit(node.args[0])))
        raise CalculationError("Unsupported expression or function")

    try:
        tree = ast.parse(expression, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 150:
            raise CalculationError("Expression is too complex")
        return _finite(visit(tree.body))
    except CalculationError:
        raise
    except SyntaxError:
        raise CalculationError("Check the expression and parentheses") from None
    except (OverflowError, RecursionError):
        raise CalculationError("Result is too large or expression too complex") from None
    except ZeroDivisionError:
        raise CalculationError("Cannot divide by zero") from None
    except ValueError as error:
        if str(error) == "Cannot divide by zero":
            raise CalculationError(str(error)) from None
        raise CalculationError("Invalid input for this operation") from None


def format_result(value):
    """Show up to 12 significant digits; retain full float precision in ans."""
    return "0" if value == 0 else format(value, ".12g")


class CalculatorState:
    """Input behavior shared by the UI and automated tests."""

    def __init__(self):
        self.degrees = True
        self.clear()

    def clear(self):
        self.expression = ""
        self.answer = 0.0
        self.finished = False
        self.result = "0"
        self.message = "Ready"

    def insert(self, token):
        expression = self.expression
        if self.finished:
            expression = "ans" if token in ("+", "-", "*", "/", "^", "**") else ""
        if len(expression) + len(token) > 300:
            self.message = "Expression is too long"
            return
        self.expression = expression + token
        self.finished = False
        self.message = "Ready"

    def backspace(self):
        self.expression = self.expression[:-1]
        self.finished = False
        self.message = "Ready"

    def wrap(self, template):
        value = "ans" if self.finished else (self.expression or "0")
        expression = template.format(value)
        if len(expression) > 300:
            self.message = "Expression is too long"
            return
        self.expression = expression
        self.finished = False
        self.message = "Ready"

    def toggle_mode(self):
        self.degrees = not self.degrees
        self.message = "Press = to calculate in the new angle mode"

    def solve(self):
        if self.finished:
            # Re-evaluate the visible formula using the same original ans value.
            previous = self._previous_answer
        else:
            previous = self.answer
        try:
            result = evaluate(self.expression, self.degrees, previous)
        except CalculationError as error:
            self.result = "Error"
            self.message = str(error)
            self.finished = False
            return False
        self._previous_answer = previous
        self.answer = result
        self.result = format_result(result)
        self.message = "Calculated in " + ("degrees" if self.degrees else "radians")
        self.finished = True
        return True
