"""Scientific calculator desktop interface. Run: python app.py"""

import tkinter as tk
from scientific import CalculatorState

BACKGROUND = "#111318"
SCREEN = "#191D25"
NUMBER = "#252B36"
FUNCTION = "#30394A"
ACCENT = "#A9F15A"
TEXT = "#F5F7FA"
MUTED = "#9AA5B7"


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scientific Calculator | 1.1")
        self.geometry("440x660")
        self.minsize(440, 660)
        self.configure(bg=BACKGROUND)
        self.state_model = CalculatorState()
        self.expression_text = tk.StringVar(value="0")
        self.result_text = tk.StringVar(value="0")
        self.message_text = tk.StringVar(value="Ready")
        self.build_interface()
        self.bind("<KeyPress>", self.handle_key)

    def build_interface(self):
        header = tk.Frame(self, bg=BACKGROUND)
        header.pack(fill="x", padx=20, pady=(18, 12))
        title = tk.Frame(header, bg=BACKGROUND)
        title.pack(side="left")
        tk.Label(title, text="Calculator", font=("Segoe UI", 18, "bold"),
                 bg=BACKGROUND, fg=TEXT).pack(anchor="w")
        tk.Label(title, text="SCIENTIFIC  /  1.1", font=("Segoe UI", 9),
                 bg=BACKGROUND, fg=MUTED).pack(anchor="w")
        self.mode_button = tk.Button(
            header, text="DEG", font=("Segoe UI", 11, "bold"),
            bg=FUNCTION, fg=ACCENT, activebackground=NUMBER,
            activeforeground=ACCENT, relief="flat", bd=0, padx=15, pady=9,
            takefocus=False, cursor="hand2", command=self.toggle_mode)
        self.mode_button.pack(side="right")

        screen = tk.Frame(self, bg=SCREEN)
        screen.pack(fill="x", padx=16)
        self.formula = tk.Entry(
            screen, textvariable=self.expression_text, state="readonly",
            readonlybackground=SCREEN, fg=MUTED, relief="flat", bd=0,
            font=("Consolas", 17), justify="right", highlightthickness=0)
        self.formula.pack(fill="x", padx=16, pady=(18, 8))
        self.result_label = tk.Label(
            screen, textvariable=self.result_text, anchor="e",
            font=("Segoe UI", 32, "bold"), bg=SCREEN, fg=TEXT)
        self.result_label.pack(fill="x", padx=16)
        tk.Label(screen, textvariable=self.message_text, anchor="w",
                 font=("Segoe UI", 9), bg=SCREEN, fg=MUTED,
                 wraplength=380, justify="left").pack(fill="x", padx=16, pady=(9, 14))

        tk.Label(self, text="Functions: sin(30)   •   Powers: 2^3   •   Enter =",
                 font=("Segoe UI", 9), bg=BACKGROUND, fg=MUTED).pack(pady=(10, 5))

        keypad = tk.Frame(self, bg=BACKGROUND)
        keypad.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        rows = [
            ["sin", "cos", "tan", "(", ")"],
            ["ln", "log", "√", "xʸ", "x²"],
            ["π", "e", "n!", "1/x", "AC"],
            ["7", "8", "9", "÷", "⌫"],
            ["4", "5", "6", "×", "±"],
            ["1", "2", "3", "−", "Ans"],
            ["0", ".", "abs", "+", "="],
        ]
        for column in range(5):
            keypad.columnconfigure(column, weight=1, uniform="key")
        for row in range(len(rows)):
            keypad.rowconfigure(row, weight=1, uniform="row")
        for row, symbols in enumerate(rows):
            for column, symbol in enumerate(symbols):
                self.add_button(keypad, symbol, row, column)
        tk.Label(self, text="Enter to calculate  ·  Backspace to delete  ·  Esc to clear",
                 font=("Segoe UI", 9), bg=BACKGROUND, fg=MUTED).pack(pady=(0, 12))

    def add_button(self, parent, symbol, row, column):
        is_number = symbol.isdigit() or symbol == "."
        color = ACCENT if symbol == "=" else NUMBER if is_number else FUNCTION
        foreground = BACKGROUND if symbol == "=" else TEXT
        if symbol in ("÷", "×", "−", "+", "xʸ", "x²"):
            foreground = ACCENT
        hover = "#BFF780" if symbol == "=" else "#414B5F"
        button = tk.Button(
            parent, text=symbol, font=("Segoe UI", 16, "bold"),
            bg=color, fg=foreground, activebackground=hover,
            activeforeground=foreground, relief="flat", bd=0,
            highlightthickness=0, takefocus=False, cursor="hand2",
            command=lambda: self.press(symbol))
        button.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
        button.bind("<Enter>", lambda event: button.configure(bg=hover))
        button.bind("<Leave>", lambda event: button.configure(bg=color))

    def refresh(self):
        self.expression_text.set(self.state_model.expression or "0")
        self.formula.xview_moveto(1.0)
        self.result_text.set(self.state_model.result)
        size = 32 if len(self.state_model.result) <= 14 else 23
        self.result_label.configure(font=("Segoe UI", size, "bold"))
        self.message_text.set(self.state_model.message)
        self.mode_button.configure(text="DEG" if self.state_model.degrees else "RAD")

    def press(self, symbol):
        model = self.state_model
        if symbol == "AC":
            model.clear()
        elif symbol == "⌫":
            model.backspace()
        elif symbol == "=":
            model.solve()
        elif symbol in ("x²", "1/x", "±"):
            template = {"x²": "({})^2", "1/x": "1/({})", "±": "-({})"}[symbol]
            model.wrap(template)
        else:
            tokens = {"π": "pi", "Ans": "ans", "√": "sqrt(", "n!": "fact(",
                      "×": "*", "÷": "/", "−": "-", "xʸ": "^"}
            token = tokens.get(symbol, symbol)
            if symbol in ("sin", "cos", "tan", "ln", "log", "abs"):
                token += "("
            model.insert(token)
        self.refresh()

    def toggle_mode(self):
        self.state_model.toggle_mode()
        self.refresh()

    def handle_key(self, event):
        # Keep system shortcuts, including Ctrl+C, available.
        if event.state & 0x4:
            return None
        if event.keysym in ("Return", "KP_Enter"):
            self.press("=")
        elif event.keysym == "Escape":
            self.press("AC")
        elif event.keysym == "BackSpace":
            self.press("⌫")
        elif event.char and event.char in "0123456789.+-*/^()abcdefghijklmnopqrstuvwxyzE=":
            self.press(event.char)
        else:
            return None
        return "break"


if __name__ == "__main__":
    Calculator().mainloop()
