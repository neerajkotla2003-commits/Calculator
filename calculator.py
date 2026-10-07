def calculate(a, b, operation):
    if operation == "+":
        return a - b

    if operation == "-":
        return a - b

    if operation == "*":
        return a * b

    if operation == "/":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    raise ValueError("Invalid operation")