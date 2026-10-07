import ast
import tkinter as tk

from calculator import calculate


# Theme
BACKGROUND = "#111318"
DISPLAY = "#191C23"
NUMBER = "#252A34"
UTILITY = "#343B48"
ACCENT = "#A9F15A"
TEXT = "#F5F7FA"
MUTED = "#9099AA"

OPERATORS = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
}


def evaluate(expression):
    """Evaluate basic arithmetic without using eval()."""
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value

        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -visit(node.operand)
            if isinstance(node.op, ast.UAdd):
                return visit(node.operand)

        if isinstance(node, ast.BinOp):
            operation = OPERATORS.get(type(node.op))
            if operation:
                return calculate(
                    visit(node.left),
                    visit(node.right),
                    operation,
                )

        raise ValueError("Invalid expression")

    return visit(tree)


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Calculator")
        self.geometry("360x520")
        self.resizable(False, False)
        self.configure(bg=BACKGROUND)

        self.expression = ""
        self.finished = False

        self.value = tk.StringVar(value="0")
        self.history = tk.StringVar(value="STANDARD")

        self.build_interface()
        self.bind("<Key>", self.handle_keyboard)

    def build_interface(self):
        header = tk.Frame(self, bg=BACKGROUND)
        header.pack(fill="x", padx=22, pady=(18, 12))

        tk.Label(
            header,
            text="Calculator",
            font=("Segoe UI", 15, "bold"),
            bg=BACKGROUND,
            fg=TEXT,
        ).pack(side="left")

        tk.Label(
            header,
            text="●",
            font=("Segoe UI", 12),
            bg=BACKGROUND,
            fg=ACCENT,
        ).pack(side="right")

        screen = tk.Frame(self, bg=DISPLAY)
        screen.pack(fill="x", padx=16, pady=(0, 16))

        tk.Label(
            screen,
            textvariable=self.history,
            font=("Segoe UI", 10),
            bg=DISPLAY,
            fg=MUTED,
            anchor="e",
        ).pack(fill="x", padx=18, pady=(16, 4))

        self.display = tk.Label(
            screen,
            textvariable=self.value,
            font=("Segoe UI", 34, "bold"),
            bg=DISPLAY,
            fg=TEXT,
            anchor="e",
        )
        self.display.pack(fill="x", padx=18, pady=(0, 18))

        keypad = tk.Frame(self, bg=BACKGROUND)
        keypad.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 14),
        )

        rows = [
            ["AC", "(", ")", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["⌫", "0", ".", "="],
        ]

        for index in range(4):
            keypad.columnconfigure(index, weight=1, uniform="column")

        for index in range(5):
            keypad.rowconfigure(index, weight=1, uniform="row")

        for row_index, row in enumerate(rows):
            for column_index, symbol in enumerate(row):
                self.create_button(
                    keypad,
                    symbol,
                    row_index,
                    column_index,
                )

    def create_button(self, parent, symbol, row, column):
        if symbol == "=":
            background = ACCENT
            foreground = BACKGROUND
            hover = "#BDF780"
        elif symbol in ("÷", "×", "−", "+"):
            background = UTILITY
            foreground = ACCENT
            hover = "#454E5F"
        elif symbol in ("AC", "(", ")", "⌫"):
            background = UTILITY
            foreground = TEXT
            hover = "#454E5F"
        else:
            background = NUMBER
            foreground = TEXT
            hover = "#363D4B"

        button = tk.Button(
            parent,
            text=symbol,
            font=("Segoe UI", 18, "bold"),
            bg=background,
            fg=foreground,
            activebackground=hover,
            activeforeground=foreground,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            takefocus=False,
            command=lambda: self.press(symbol),
        )

        button.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=4,
            pady=4,
        )

        button.bind(
            "<Enter>",
            lambda event: button.configure(bg=hover),
        )
        button.bind(
            "<Leave>",
            lambda event: button.configure(bg=background),
        )

    def refresh(self):
        readable = (
            self.expression
            .replace("*", "×")
            .replace("/", "÷")
            .replace("-", "−")
        )

        self.value.set(readable or "0")

        # Reduce the text size for longer calculations.
        length = len(readable)
        size = 34 if length <= 11 else 23 if length <= 17 else 16
        self.display.configure(font=("Segoe UI", size, "bold"))

    def press(self, symbol):
        if symbol == "AC":
            self.expression = ""
            self.history.set("STANDARD")
            self.finished = False
            self.refresh()
            return

        if symbol == "⌫":
            self.expression = self.expression[:-1]
            self.finished = False
            self.history.set("STANDARD")
            self.refresh()
            return

        if symbol == "=":
            self.show_result()
            return

        character = {
            "×": "*",
            "÷": "/",
            "−": "-",
        }.get(symbol, symbol)

        if self.finished:
            if character not in "+-*/":
                self.expression = ""
            self.finished = False
            self.history.set("STANDARD")

        # Keep expressions within the fixed-size display.
        if len(self.expression) >= 24:
            return

        self.expression += character
        self.refresh()

    def show_result(self):
        if not self.expression:
            return

        original = self.value.get()

        try:
            answer = evaluate(self.expression)
            self.expression = format(answer, ".12g")
            self.history.set(f"{original} =")
            self.finished = True
            self.refresh()

        except (ValueError, ZeroDivisionError):
            self.show_error("Cannot calculate")

        except (SyntaxError, TypeError, OverflowError):
            self.show_error("Check expression")

    def show_error(self, message):
        self.history.set(message)
        self.value.set("Error")
        self.expression = ""
        self.finished = True

    def handle_keyboard(self, event):
        if event.keysym in ("Return", "KP_Enter"):
            self.press("=")
        elif event.keysym == "BackSpace":
            self.press("⌫")
        elif event.keysym == "Escape":
            self.press("AC")
        elif event.char and event.char in "0123456789.+-*/()":
            self.press(event.char)


if __name__ == "__main__":
    Calculator().mainloop()