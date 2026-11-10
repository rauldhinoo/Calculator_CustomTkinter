from __future__ import annotations

import ast
import math
import operator
import re
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CalculatorError(Exception):
    pass

class SafeEvaluator:

    _binary_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }
    _unary_operators = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    @classmethod
    def evaluate(cls, expression: str) -> float:
        if not expression.strip():
            raise CalculatorError("Masukkan angka terlebih dahulu.")

        try:
            parsed = ast.parse(expression, mode="eval")
            result = cls._visit(parsed.body)
        except CalculatorError:
            raise
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
            raise CalculatorError("Ekspresi tidak valid.") from exc

        if isinstance(result, bool) or not isinstance(result, (int, float)):
            raise CalculatorError("Hasil tidak valid.")
        if not math.isfinite(float(result)):
            raise CalculatorError("Hasil terlalu besar atau tak terdefinisi.")
        return float(result)

    @classmethod
    def _visit(cls, node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)

        if isinstance(node, ast.BinOp) and type(node.op) in cls._binary_operators:
            left = cls._visit(node.left)
            right = cls._visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise CalculatorError("Pangkat terlalu besar.")
            result = cls._binary_operators[type(node.op)](left, right)
            if not math.isfinite(float(result)):
                raise CalculatorError("Hasil terlalu besar atau tidak terdefinisi.")
            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in cls._unary_operators:
            return cls._unary_operators[type(node.op)](cls._visit(node.operand))

        raise CalculatorError("Ekspresi mengandung operasi yang tidak didukung.")


class VisualCalculator(ctk.CTk):
    BG = "#101522"
    PANEL = "#192235"
    DISPLAY = "#111A2A"
    KEY = "#273349"
    KEY_HOVER = "#35445F"
    OPERATOR = "#2563EB"
    OPERATOR_HOVER = "#1D4ED8"
    ACTION = "#D97706"
    ACTION_HOVER = "#B45309"
    TEXT = "#F4F7FB"
    MUTED = "#9AA8BD"
    GREEN = "#34D399"

    def __init__(self) -> None:
        super().__init__()
        self.title("Visual Calculator")
        self.geometry("390x650")
        self.minsize(340, 570)
        self.configure(fg_color=self.BG)

        self.expression = ""
        self.just_evaluated = False
        self.expression_var = tk.StringVar(value="0")
        self.result_var = tk.StringVar(value="Ready")

        self._build_ui()
        self.bind_all("<Key>", self._on_key_press)
        self.focus_set()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header section
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="CALCULATOR",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            text_color=self.MUTED,
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=self.GREEN,
        ).grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(
            header,
            text="Simple • Fast • Clean",
            font=ctk.CTkFont(size=11),
            text_color=self.MUTED,
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        # Main calculator panel
        panel = ctk.CTkFrame(self, fg_color=self.PANEL, corner_radius=24)
        panel.grid(row=1, column=0, sticky="nsew", padx=16, pady=(6, 18))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        # Display
        display = ctk.CTkFrame(panel, fg_color=self.DISPLAY, corner_radius=18)
        display.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 12))
        display.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            display,
            textvariable=self.result_var,
            anchor="e",
            font=ctk.CTkFont(size=13),
            text_color=self.GREEN,
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(13, 2))

        ctk.CTkLabel(
            display,
            textvariable=self.expression_var,
            anchor="e",
            justify="right",
            font=ctk.CTkFont(family="Arial", size=31, weight="bold"),
            text_color=self.TEXT,
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(2, 16))

        # Keypad
        keypad = ctk.CTkFrame(panel, fg_color="transparent")
        keypad.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        for col in range(4):
            keypad.grid_columnconfigure(col, weight=1, uniform="keys")
        for row in range(6):
            keypad.grid_rowconfigure(row, weight=1, uniform="keys")

        keys = [
            ["AC", "⌫", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="],
            ["√", "(", ")", "^"],
        ]

        for r, row_keys in enumerate(keys):
            for c, label in enumerate(row_keys):
                self._make_key(keypad, label, r, c)

        ctk.CTkLabel(
            panel,
            text="Keyboard supported  ·  Enter = See Result ·  Esc = Clear",
            font=ctk.CTkFont(size=10),
            text_color=self.MUTED,
        ).grid(row=2, column=0, pady=(0, 12))

    def _make_key(self, parent: ctk.CTkFrame, label: str, row: int, col: int) -> None:
        if label == "=":
            fg, hover, text_color = self.OPERATOR, self.OPERATOR_HOVER, "white"
        elif label in {"AC", "⌫", "%", "√", "±"}:
            fg, hover, text_color = self.ACTION, self.ACTION_HOVER, "white"
        elif label in {"÷", "×", "−", "+", "^"}:
            fg, hover, text_color = "#34445F", "#465A7A", self.TEXT
        else:
            fg, hover, text_color = self.KEY, self.KEY_HOVER, self.TEXT

        button = ctk.CTkButton(
            parent,
            text=label,
            command=lambda value=label: self._on_button(value),
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            corner_radius=15,
            height=62,
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            border_spacing=0,
        )
        button.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

    @staticmethod
    def _format_number(value: float) -> str:
        if abs(value) < 1e-12:
            value = 0.0
        return f"{value:.12g}"

    @staticmethod
    def _to_python_expression(expression: str) -> str:
        return (
            expression.replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
            .replace("^", "**")
        )

    def _update_display(self) -> None:
        shown = self.expression if self.expression else "0"
        self.expression_var.set(shown)

        if not self.expression:
            self.result_var.set("Ready")
            return
        try:
            preview = SafeEvaluator.evaluate(self._to_python_expression(self.expression))
            self.result_var.set("= " + self._format_number(preview))
        except CalculatorError:
            self.result_var.set(" ")

    def _on_button(self, key: str) -> None:
        if key == "AC":
            self._clear()
        elif key == "⌫":
            self._backspace()
        elif key == "=":
            self._calculate()
        elif key == "%":
            self._percent()
        elif key == "√":
            self._square_root()
        elif key == "±":
            self._toggle_sign()
        else:
            self._append(key)

    def _append(self, value: str) -> None:
        if self.just_evaluated and (value.isdigit() or value == "." or value == "("):
            self.expression = ""
        self.just_evaluated = False

        if value in {"+", "−", "×", "÷", "^"}:
            if not self.expression:
                if value == "−":
                    self.expression = "−"
                else:
                    return
            elif self.expression[-1] in "+−×÷^":
                self.expression = self.expression[:-1] + value
            else:
                self.expression += value
        elif value == ".":
            # Prevent two decimal points in the current number.
            current_number = re.search(r"(?:^|[+−×÷^(])([0-9]*\.?[0-9]*)$", self.expression)
            if current_number and "." in current_number.group(1):
                return
            if not self.expression or self.expression[-1] in "+−×÷^(":
                self.expression += "0."
            else:
                self.expression += "."
        else:
            self.expression += value

        self._update_display()

    def _clear(self) -> None:
        self.expression = ""
        self.just_evaluated = False
        self._update_display()

    def _backspace(self) -> None:
        if self.just_evaluated:
            self.just_evaluated = False
        self.expression = self.expression[:-1]
        self._update_display()

    def _calculate(self) -> None:
        if not self.expression:
            return
        try:
            result = SafeEvaluator.evaluate(self._to_python_expression(self.expression))
            formatted = self._format_number(result)
            self.result_var.set(self.expression + " =")
            self.expression = formatted
            self.expression_var.set(formatted)
            self.just_evaluated = True
        except CalculatorError as exc:
            self.result_var.set("Error")
            messagebox.showerror("Calculation error", str(exc), parent=self)

    def _percent(self) -> None:
        # Convert the last number to a fraction: 25% becomes (25/100).
        match = re.search(r"(\d+(?:\.\d*)?|\.\d+)$", self.expression)
        if not match:
            return
        number = match.group(1)
        self.expression = self.expression[: match.start()] + f"({number}/100)"
        self.just_evaluated = False
        self._update_display()

    def _square_root(self) -> None:
        if not self.expression:
            return
        try:
            value = SafeEvaluator.evaluate(self._to_python_expression(self.expression))
            if value < 0:
                raise CalculatorError("Akar kuadrat bilangan negatif tidak tersedia.")
            result = self._format_number(math.sqrt(value))
            self.result_var.set("√(" + self.expression + ")")
            self.expression = result
            self.expression_var.set(result)
            self.just_evaluated = True
        except CalculatorError as exc:
            self.result_var.set("Error")
            messagebox.showerror("Calculation error", str(exc), parent=self)

    def _toggle_sign(self) -> None:
        match = re.search(r"(\d+(?:\.\d*)?|\.\d+)$", self.expression)
        if match:
            number = match.group(1)
            start = match.start()
            if start > 0 and self.expression[start - 1] == "−":
                # Keep a binary minus intact; remove only a unary minus.
                before = self.expression[: start - 1]
                if not before or before[-1] in "+−×÷^(":
                    self.expression = before + number
                else:
                    self.expression = self.expression[:start] + "(-" + number + ")"
            else:
                before = self.expression[:start]
                if not before or before[-1] in "+−×÷^(":
                    self.expression = before + "−" + number
                else:
                    self.expression = before + "(-" + number + ")"
            self._update_display()

    def _on_key_press(self, event: tk.Event) -> str | None:
        key = event.keysym
        char = event.char

        if key in {"Return", "KP_Enter"}:
            self._calculate()
            return "break"
        if key == "Escape":
            self._clear()
            return "break"
        if key == "BackSpace":
            self._backspace()
            return "break"

        mapping = {"*": "×", "/": "÷", "-": "−", "^": "^"}
        if char and char in "0123456789.()+%":
            self._on_button(char)
            return "break"
        if char in mapping or char == "+":
            self._on_button(mapping.get(char, char))
            return "break"
        if char == "=":
            self._calculate()
            return "break"
        return None

if __name__ == "__main__":
    app = VisualCalculator()
    app.mainloop()
