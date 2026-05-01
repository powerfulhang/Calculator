# File Name: main.py
# Author: hang.shi
# Time: 2026-05-01
# Version: 1.0
# Description: Entry point for the Python calculator application.

"""Launch the calculator GUI."""

from __future__ import annotations

from calculator_ui import CalculatorApp

__author__ = "hang.shi"

if __name__ == '__main__':
    app = CalculatorApp()
    app.run()
