import pytest

from calculator import calculate


@pytest.mark.parametrize(
    "a, b, operation, expected",
    [
        (10, 5, "+", 15),
        (10, 5, "-", 5),
        (10, 5, "*", 50),
        (10, 5, "/", 2),
        (-4, 2, "+", -2),
        (0, 5, "*", 0),
        (0.1, 0.2, "+", 0.3),
    ],
)
def test_calculate(a, b, operation, expected):
    assert calculate(a, b, operation) == pytest.approx(expected)


def test_division_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculate(10, 0, "/")


def test_invalid_operation():
    with pytest.raises(ValueError, match="Invalid operation"):
        calculate(10, 5, "%")