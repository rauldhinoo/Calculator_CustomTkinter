# Visual Calculator (CustomTkinter)

A simple desktop calculator built with Python and CustomTkinter.

## Requirements
- Python 3.10 or newer
- CustomTkinter 6.0.0 or newer

## Install
```bash
python -m pip install -r requirements.txt
```

## Run
```bash
python visual_calculator.py
```

## Features
- Addition, subtraction, multiplication, division, modulo, and powers
- Parentheses and decimal numbers
- Percent conversion for the last entered number (for example, `25%` becomes `0.25`)
- Square root of the current expression
- Sign toggle and backspace
- Live result preview
- Keyboard support: numbers, operators, Enter, Backspace, and Escape
- Arithmetic is evaluated with a restricted AST parser (not Python `eval()`)
