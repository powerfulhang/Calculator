# File Name: calculator_ui.py
# Author: hang.shi
# Time: 2026-05-01
# Version: 1.0
# Description: tkinter-based UI for the calculator, replicating the original Java Swing interface.

"""Calculator GUI built with tkinter.

Provides the full calculator window with:
  - Menu bar (Options / Help)
  - Dual display area (expression input + result)
  - Memory buttons (MC, MR, MS, M+)
  - Scientific mode button grid (7x5)
  - Programmer mode button grid (6x6)
  - Mode switching between Scientific and Programmer (Bin/Oct/Hex)
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, List

import calculator_engine as eng

__author__ = "powerfulhang"
__version__ = "1.0"

# =============================================================================
# Constants
# =============================================================================

FONT_FAMILY = 'Consolas'
DISPLAY_BG = '#D3D3D3'       # light gray (matches Java Color.LIGHT_GRAY)
OP_BG = '#808080'             # gray for operator / function buttons
NUM_BG = '#FFFFFF'            # white for digit buttons
MEM_BG = '#808080'            # gray for memory buttons
FG_COLOR = '#000000'          # black text

# Window sizes per mode
SCI_WINDOW_SIZE = '440x680'
PROG_WINDOW_SIZE = '540x680'


# =============================================================================
# Button definitions
# =============================================================================

MEMORY_BUTTONS = ['MC', 'MR', 'MS', 'M+']

# Scientific mode: 7 rows x 5 columns
SCI_BUTTONS = [
    ['sin',  'cos',  'tan',  'log',  'Exp'],
    ['√',    '1/x',  'n!',   '±',    'M'],
    ['^',    'CE',   'AC',   '←',    '÷'],
    ['Dec',  '7',    '8',    '9',    '×'],
    ['Bin',  '4',    '5',    '6',    '-'],
    ['π',    '1',    '2',    '3',    '+'],
    ['(',    ')',    '0',    '.',    '='],
]

# Programmer mode: 6 rows x 6 columns
PROG_BUTTONS = [
    ['2Dec', '2Bin', 'AND', 'OR',  'XOR', 'NOT'],
    ['2Oct', '2Hex', 'CE',  'AC',  '←',   '÷'],
    ['A',    'B',    '7',   '8',   '9',   '×'],
    ['C',    'D',    '4',   '5',   '6',   '-'],
    ['E',    'F',    '1',   '2',   '3',   '+'],
    ['Lsh',  'Rsh',  'M',   '0',   '.',   '='],
]

# Digits (shown on white background)
_DIGITS = set('0123456789')
# Programmer-mode hex digits
_HEX_DIGITS = set('ABCDEF')

# Buttons whose text is appended verbatim to the input expression
_APPEND_OPS_SCI = {'+', '-', '×', '÷', '^', '√', 'M'}
_APPEND_OPS_PROG = {'+', '-', '×', '÷', 'M', 'AND', 'OR', 'XOR', 'Lsh', 'Rsh'}

# Programmer mode operator mapping to internal characters
_PROG_OP_MAP = {'AND': '&', 'OR': '|', 'XOR': '^', 'Lsh': '<', 'Rsh': '>'}

# Disabled buttons per programmer submode (button labels)
_PROG_DISABLED: Dict[str, set] = {
    'dec': {'2Dec', 'A', 'B', 'C', 'D', 'E', 'F', '.'},
    'hex': {'2Hex', '.'},
    'oct': {'2Oct', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', '.'},
    'bin': {'2Bin', '2', '3', '4', '5', '6', '7', '8', '9',
            'A', 'B', 'C', 'D', 'E', 'F', '.'},
}

HELP_SECTIONS: Dict[str, str] = {
    '快速开始': """计算器帮助

本窗口用于查询计算器的模式、按键和操作规则。左侧选择主题，右侧查看说明。

基本流程
1. 选择计算模式：科学模式，或程序员模式下的二进制、八进制、十进制、十六进制。
2. 输入数字和运算符。
3. 按 = 计算结果。
4. 继续输入运算符可把当前结果作为下一轮运算数。

显示区
- 上方：当前输入表达式。
- 下方：当前结果或错误信息。

清除键
- CE：清除当前输入，结果回到 0。
- AC：清除当前输入、结果和科学模式的连续运算缓存。
- ←：删除当前输入的最后一个字符。""",

    '科学模式': """科学模式

支持的基础运算
- +：加法
- -：减法，也支持负数输入，例如 -5、5*-2、5--2
- ×：乘法
- ÷：除法
- M：取模
- ^：乘方，右结合，例如 2^3^2 = 512
- √：开方。√9 等价于 2√9，3√8 表示三次根
- ( 和 )：括号

支持的函数
- sin、cos、tan：三角函数，输入按弧度解释
- log：常用对数，以 10 为底
- Exp：自然指数 e^x
- 1/x：倒数
- n!：阶乘，仅支持非负整数
- ±：对当前数值取反
- π：插入圆周率

二进制转换
- Bin：把当前十进制数转换为二进制
- Dec：把当前二进制数转换为十进制
- Dec 会校验输入，只接受 0、1、小数点和可选负号。""",

    '程序员模式': """程序员模式

模式入口
- 选项(S) -> 切换(H) -> 程序员 -> 十六进制 / 八进制 / 二进制
- 使用 2Dec 转换后会进入十进制程序员状态

进制与可输入字符
- Bin：只允许 0、1
- Oct：允许 0 到 7
- Dec：允许 0 到 9
- Hex：允许 0 到 9、A 到 F

转换规则
- 2Bin：转换为二进制，并把后续运算切换到二进制模式
- 2Oct：转换为八进制，并把后续运算切换到八进制模式
- 2Dec：转换为十进制，并把后续运算切换到十进制模式
- 2Hex：转换为十六进制，并把后续运算切换到十六进制模式

示例
Hex 模式输入 AB，按 2Bin 得到 10101011。
此时再输入 +1=，会按二进制计算，结果为 10101100。""",

    '程序员运算符': """程序员运算符

算术运算
- +：加法
- -：减法
- ×：乘法
- ÷：整数除法
- M：取模

位运算
- AND：按位与
- OR：按位或
- XOR：按位异或
- NOT：32 位按位取反
- Lsh：左移
- Rsh：右移

优先级
1. ×、÷、M
2. +、-
3. Lsh、Rsh
4. AND
5. XOR
6. OR

说明
- 程序员模式按整数计算，不支持小数点。
- 移位运算按 32 位结果处理。""",

    '内存与剪贴板': """内存与剪贴板

内存键
- MC：清空内存
- MS：把当前可见值存入内存
- MR：把内存值追加到当前输入
- M+：把当前可见值累加到内存

复制和粘贴
- 复制(C) Ctrl+C：复制当前结果区内容
- 粘贴(V) Ctrl+V：粘贴数值内容到当前输入
- 非数值剪贴板内容会被忽略

注意
- 内存值以文本形式插入当前输入。
- 在程序员模式中，插入的内存值需要符合当前进制。""",

    '键盘快捷键': """键盘快捷键

通用
- 0-9：输入数字
- .：输入小数点，程序员模式中禁用
- +、-、*、/：四则运算
- %：取模 M
- ^：科学模式为乘方，程序员模式为 XOR
- Enter：等号
- Backspace：退格
- Delete：CE
- Escape：AC
- Ctrl+C：复制结果
- Ctrl+V：粘贴数值

程序员模式
- A-F：输入十六进制数字
- &：AND
- |：OR
- ~：NOT
- <：Lsh
- >：Rsh""",

    '错误信息': """常见错误

Cannot divide by zero
- 除数为 0。

Cannot modulo by zero
- 取模运算的右操作数为 0。

Incomplete expression
- 表达式不完整，例如末尾是运算符。

Malformed expression
- 表达式结构不合法，例如数字和括号之间缺少运算符。

Invalid binary number
- 二进制转换输入包含非法字符。

Factorial is only defined for non-negative integers
- 阶乘只支持非负整数。""",
}


# =============================================================================
# Main Application
# =============================================================================

class CalculatorApp:
    """Main calculator application window."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title('计算器')
        self.root.resizable(False, False)

        # ---- State ----
        self.pattern: str = 'sci'         # 'sci', 'dec', 'bin', 'oct', 'hex'
        self.input_expr: str = ''         # current expression being built
        self.memory: str = ''             # memory string (MS/MR/MC/M+)
        self.clipboard: str = ''          # copy/paste clipboard
        self._sci_last_result: str = '0'  # last result in scientific mode (for chaining)
        self.help_window: tk.Toplevel | None = None
        self.help_listbox: tk.Listbox | None = None
        self.help_text: tk.Text | None = None

        # ---- Build UI ----
        self._build_menu_bar()
        self._build_display()
        self._build_memory_bar()
        self._button_frame = tk.Frame(self.root)
        self._button_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        self._buttons: List[tk.Button] = []
        self._build_science_buttons()

        # ---- Keyboard shortcuts ----
        self.root.bind('<Control-c>', lambda _e: self._on_copy())
        self.root.bind('<Control-v>', lambda _e: self._on_paste())
        self._bind_keyboard()

        # ---- Finish ----
        self.root.geometry(SCI_WINDOW_SIZE)
        self.root.configure(bg='SystemButtonFace')

    # =========================================================================
    # Menu bar
    # =========================================================================

    def _build_menu_bar(self) -> None:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # -- 选项(S) --
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label='复制(C) Ctrl+C', command=self._on_copy)
        edit_menu.add_command(label='粘贴(V) Ctrl+V', command=self._on_paste)
        edit_menu.add_separator()

        # 切换(H) submenu
        switch_menu = tk.Menu(edit_menu, tearoff=0)
        switch_menu.add_command(label='科学', command=self._switch_to_science)

        prog_sub = tk.Menu(switch_menu, tearoff=0)
        prog_sub.add_command(label='十六进制', command=self._switch_to_hex)
        prog_sub.add_command(label='八进制', command=self._switch_to_oct)
        prog_sub.add_command(label='二进制', command=self._switch_to_bin)
        switch_menu.add_cascade(label='程序员', menu=prog_sub)

        edit_menu.add_cascade(label='切换(H)', menu=switch_menu)
        edit_menu.add_separator()
        edit_menu.add_command(label='退出(E)', command=self.root.destroy)

        # -- 帮助(H) --
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='帮助文档', command=self._on_help_document)
        help_menu.add_separator()
        help_menu.add_command(label='关于', command=self._on_about)

        menubar.add_cascade(label='选项(S)', menu=edit_menu)
        menubar.add_cascade(label='帮助(H)', menu=help_menu)

    # =========================================================================
    # Display area
    # =========================================================================

    def _build_display(self) -> None:
        """Create the two read-only display entries (input expression + result)."""
        display_frame = tk.Frame(self.root)
        display_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        # Input expression display
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            display_frame,
            textvariable=self.input_var,
            font=(FONT_FAMILY, 20, 'bold'),
            bg=DISPLAY_BG,
            fg=FG_COLOR,
            justify=tk.RIGHT,
            relief=tk.FLAT,
            state='readonly',
            readonlybackground=DISPLAY_BG,
        )
        self.input_entry.pack(fill=tk.X, ipady=10)

        # Result display
        self.result_var = tk.StringVar(value='0')
        self.result_entry = tk.Entry(
            display_frame,
            textvariable=self.result_var,
            font=(FONT_FAMILY, 26, 'bold'),
            bg=DISPLAY_BG,
            fg=FG_COLOR,
            justify=tk.RIGHT,
            relief=tk.FLAT,
            state='readonly',
            readonlybackground=DISPLAY_BG,
        )
        self.result_entry.pack(fill=tk.X, ipady=12)

    # =========================================================================
    # Memory buttons
    # =========================================================================

    def _build_memory_bar(self) -> None:
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        for i, label in enumerate(MEMORY_BUTTONS):
            btn = tk.Button(
                frame,
                text=label,
                font=(FONT_FAMILY, 14, 'bold'),
                bg=MEM_BG,
                fg=FG_COLOR,
                command=lambda l=label: self._on_memory(l),
            )
            btn.grid(row=0, column=i, sticky='nsew', padx=(0 if i == 0 else 2, 0))
            frame.grid_columnconfigure(i, weight=1)

    # =========================================================================
    # Button grids — scientific
    # =========================================================================

    def _build_science_buttons(self) -> None:
        """Create the 7x5 scientific button grid."""
        for widget in self._button_frame.winfo_children():
            widget.destroy()
        self._buttons.clear()

        self._button_frame.grid_columnconfigure(tuple(range(5)), weight=1)
        self._button_frame.grid_rowconfigure(tuple(range(7)), weight=1)

        for row, row_labels in enumerate(SCI_BUTTONS):
            for col, label in enumerate(row_labels):
                btn = tk.Button(
                    self._button_frame,
                    text=label,
                    font=(FONT_FAMILY, 14, 'bold'),
                    bg=self._button_color(label),
                    fg=FG_COLOR,
                    command=lambda l=label: self._on_button(l),
                )
                btn.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
                self._buttons.append(btn)

    # =========================================================================
    # Button grids — programmer
    # =========================================================================

    def _build_prog_buttons(self) -> None:
        """Create the 6x6 programmer button grid, disabling invalid keys."""
        for widget in self._button_frame.winfo_children():
            widget.destroy()
        self._buttons.clear()

        self._button_frame.grid_columnconfigure(tuple(range(6)), weight=1)
        self._button_frame.grid_rowconfigure(tuple(range(6)), weight=1)

        disabled = _PROG_DISABLED.get(self.pattern, set())

        for row, row_labels in enumerate(PROG_BUTTONS):
            for col, label in enumerate(row_labels):
                btn = tk.Button(
                    self._button_frame,
                    text=label,
                    font=(FONT_FAMILY, 14, 'bold'),
                    bg=self._button_color(label),
                    fg=FG_COLOR,
                    command=lambda l=label: self._on_button(l),
                )
                btn.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
                if label in disabled:
                    btn.config(state=tk.DISABLED)
                self._buttons.append(btn)

    @staticmethod
    def _button_color(label: str) -> str:
        """Return background color for a button based on its label."""
        if label in _DIGITS or label in _HEX_DIGITS:
            return NUM_BG
        return OP_BG

    # =========================================================================
    # Mode switching
    # =========================================================================

    def _switch_to_science(self) -> None:
        self._clear_all()
        self.pattern = 'sci'
        self.root.geometry(SCI_WINDOW_SIZE)
        self._build_science_buttons()

    def _switch_to_hex(self) -> None:
        self._clear_all()
        self.pattern = 'hex'
        self.root.geometry(PROG_WINDOW_SIZE)
        self._build_prog_buttons()

    def _switch_to_oct(self) -> None:
        self._clear_all()
        self.pattern = 'oct'
        self.root.geometry(PROG_WINDOW_SIZE)
        self._build_prog_buttons()

    def _switch_to_bin(self) -> None:
        self._clear_all()
        self.pattern = 'bin'
        self.root.geometry(PROG_WINDOW_SIZE)
        self._build_prog_buttons()

    def _set_programmer_base(self, base: int) -> None:
        """Switch programmer mode to the base that matches the visible result."""
        self.pattern = {2: 'bin', 8: 'oct', 10: 'dec', 16: 'hex'}[base]
        self.root.geometry(PROG_WINDOW_SIZE)
        self._build_prog_buttons()

    def _clear_all(self) -> None:
        self.input_expr = ''
        self.input_var.set('')
        self.result_var.set('0')
        self._sci_last_result = '0'

    # =========================================================================
    # Button dispatch
    # =========================================================================

    def _on_button(self, label: str) -> None:
        """Central button handler — dispatches based on button label and mode."""
        if self.pattern == 'sci':
            self._handle_sci_button(label)
        else:
            self._handle_prog_button(label)

    # -------------------------------------------------------------------------
    # Scientific-mode button handlers
    # -------------------------------------------------------------------------

    def _handle_sci_button(self, label: str) -> None:
        # --- Digits ---
        if label in _DIGITS:
            self._on_start_fresh()
            self.input_expr += label
            self.input_var.set(self.input_expr)
            return

        # --- Decimal point ---
        if label == '.':
            self._on_start_fresh()
            if self._current_sci_operand_has_decimal():
                return
            if (
                not self.input_expr
                or self.input_expr[-1] in _APPEND_OPS_SCI
                or self.input_expr[-1] == '('
            ):
                self.input_expr += '0'
            self.input_expr += '.'
            self.input_var.set(self.input_expr)
            return

        # --- Left-parenthesis (resets like a digit in original Java) ---
        if label == '(':
            self._on_start_fresh()
            self.input_expr += '('
            self.input_var.set(self.input_expr)
            return

        # --- Binary operators (chain from last result when display is empty) ---
        if label == '√':
            self._on_start_fresh()
            self.input_expr += label
            self.input_var.set(self.input_expr)
            return

        # --- Binary operators (chain from last result when display is empty) ---
        if label in _APPEND_OPS_SCI and label not in ('(', 'π', '√'):
            if not self.input_expr:
                if label == '-':
                    self.input_expr = '-'
                    self.input_var.set(self.input_expr)
                return
            if self.input_expr[-1] in _APPEND_OPS_SCI:
                if label == '-' and self.input_expr[-1] != '-':
                    self.input_expr += label
                else:
                    self.input_expr = self.input_expr[:-1] + label
            else:
                self.input_expr += label
            self.input_var.set(self.input_expr)
            return

        # --- π (replaces result when display empty, appends otherwise) ---
        if label == 'π':
            if not self.input_var.get():
                self.input_expr = eng.format_result(math.pi)
            else:
                self.input_expr += eng.format_result(math.pi)
            self.input_var.set(self.input_expr)
            return

        # --- Right-parenthesis ---
        if label == ')':
            if not self.input_expr:
                return
            self.input_expr += ')'
            self.input_var.set(self.input_expr)
            return

        # --- Equals ---
        if label == '=':
            self._evaluate_sci()
            return

        # --- Clear Entry ---
        if label == 'CE':
            self.input_expr = ''
            self.input_var.set('')
            self.result_var.set('0')
            return

        # --- All Clear ---
        if label == 'AC':
            self._clear_all()
            return

        # --- Backspace ---
        if label == '←':
            if self.input_expr:
                self.input_expr = self.input_expr[:-1]
                self.input_var.set(self.input_expr)
                if not self.input_expr:
                    self.result_var.set('0')
            return

        # --- Single-operand functions ---
        single_funcs: Dict[str, Callable[[float], float]] = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log10,
            'Exp': math.exp,
        }
        if label in single_funcs:
            self._apply_single_op(single_funcs[label])
            return

        if label == '1/x':
            self._apply_single_op(lambda x: 1.0 / x)
            return

        if label == '±':
            self._apply_single_op(lambda x: -x)
            return

        if label == 'n!':
            self._apply_single_op(eng.factorial)
            return

        # --- Dec (bin→dec in scientific mode) ---
        if label == 'Dec':
            try:
                operand = self._get_operand()
                val = eng.binary_to_decimal(operand)
                self._set_result(val)
            except (ValueError, ZeroDivisionError) as exc:
                self.result_var.set(str(exc))
                self.input_expr = ''
            return

        # --- Bin (dec→bin in scientific mode) ---
        if label == 'Bin':
            try:
                operand = float(self._get_operand())
                result = eng.decimal_to_binary(operand)
                self._set_result_str(result)
            except (ValueError, ZeroDivisionError) as exc:
                self.result_var.set(str(exc))
                self.input_expr = ''
            return

    def _current_sci_operand_has_decimal(self) -> bool:
        """Return whether the current scientific-mode number already has a dot."""
        start = len(self.input_expr)
        while start > 0:
            previous = self.input_expr[start - 1]
            if previous in _APPEND_OPS_SCI or previous in '()':
                break
            start -= 1
        return '.' in self.input_expr[start:]

    def _get_operand(self) -> str:
        """Return current input, or the last result if the display is empty."""
        if self.input_var.get():
            return self.input_var.get()
        if self.input_expr:
            return self.input_expr
        return self._sci_last_result

    def _on_start_fresh(self) -> None:
        """If the input display is empty (just saw a result), reset for fresh input."""
        if not self.input_var.get():
            self.input_expr = ''
            self.result_var.set('0')

    def _apply_single_op(self, func: Callable[[float], float]) -> None:
        """Apply a single-operand function to the current value."""
        try:
            operand_str = self._get_operand()
            if len(operand_str) > 1 and operand_str[:2] == '0-':
                operand_str = operand_str[1:]
            value = float(operand_str)
            result = func(value)
            self._set_result(result)
        except (ValueError, ZeroDivisionError) as exc:
            self.result_var.set(str(exc))
            self.input_expr = ''
            self._sci_last_result = '0'

    def _set_result(self, value: float) -> None:
        """Set result display and preserve value for operator chaining."""
        formatted = eng.format_result(value)
        self.input_var.set('')
        self.result_var.set(formatted)
        self.input_expr = formatted
        self._sci_last_result = formatted

    def _set_result_str(self, value: str) -> None:
        """Set result from a string (e.g. binary conversion) for operator chaining."""
        self.input_var.set('')
        self.result_var.set(value)
        self.input_expr = value
        self._sci_last_result = value

    def _evaluate_sci(self) -> None:
        """Evaluate the current scientific expression."""
        if not self.input_expr:
            return
        try:
            raw = self.input_expr
            raw = raw.replace('×', '*').replace('÷', '/')
            normalised = eng.normalise_input(raw)
            postfix = eng.infix_to_postfix(normalised)
            result = eng.evaluate_postfix(postfix)
            self._set_result(result)
        except (ValueError, ZeroDivisionError) as exc:
            self.result_var.set(str(exc))
            self.input_expr = ''
            self._sci_last_result = '0'

    # -------------------------------------------------------------------------
    # Programmer-mode button handlers
    # -------------------------------------------------------------------------

    def _base(self) -> int:
        return {'bin': 2, 'oct': 8, 'dec': 10, 'hex': 16}.get(self.pattern, 16)

    def _handle_prog_button(self, label: str) -> None:
        base = self._base()
        valid_digits = eng.valid_digits(base)

        # --- Digits and hex letters ---
        if label in valid_digits:
            if not self.input_var.get():
                self.input_expr = ''
                self.result_var.set('0')
            self.input_expr += label
            self.input_var.set(self.input_expr)
            return

        # --- Binary operators (chain from result when display is empty) ---
        if label in _APPEND_OPS_PROG:
            if not self.input_expr:
                return  # ignore leading operator
            mapped = _PROG_OP_MAP.get(label, label)
            mapped = mapped.replace('×', '*').replace('÷', '/')
            self.input_expr += mapped
            self.input_var.set(self.input_expr)
            return

        # --- Equals ---
        if label == '=':
            self._evaluate_prog()
            return

        # --- CE ---
        if label == 'CE':
            self.input_expr = ''
            self.input_var.set('')
            self.result_var.set('0')
            return

        # --- AC ---
        if label == 'AC':
            self._clear_all()
            return

        # --- Backspace ---
        if label == '←':
            if self.input_expr:
                self.input_expr = self.input_expr[:-1]
                self.input_var.set(self.input_expr)
                if not self.input_expr:
                    self.result_var.set('0')
            return

        # --- NOT ---
        if label == 'NOT':
            if not self.input_expr:
                return
            try:
                result_str = eng.bitwise_not(self.input_expr, base)
                self.input_var.set('')
                self.result_var.set(result_str)
                self.input_expr = result_str
            except (ValueError, ZeroDivisionError) as exc:
                self.result_var.set(str(exc))
                self.input_expr = ''
            return

        # --- Dot (disabled in programmer mode like original) ---
        if label == '.':
            return

        # --- Base conversion buttons ---
        base_map = {'2Dec': 10, '2Bin': 2, '2Oct': 8, '2Hex': 16}
        if label in base_map:
            target = base_map[label]
            try:
                if not self.input_expr:
                    return
                result_str = eng.convert_base(self.input_expr, base, target)
                self.input_var.set('')
                self.result_var.set(result_str)
                self.input_expr = result_str
                self._set_programmer_base(target)
            except (ValueError, ZeroDivisionError) as exc:
                self.result_var.set(str(exc))
                self.input_expr = ''
            return

    def _evaluate_prog(self) -> None:
        """Evaluate the current programmer-mode expression."""
        if not self.input_expr:
            return
        try:
            raw = self.input_expr
            raw = raw.replace('×', '*').replace('÷', '/')
            result_str, _ = eng.evaluate_programmer(raw, self._base())
            self.input_var.set('')
            self.result_var.set(result_str)
            self.input_expr = result_str
        except (ValueError, ZeroDivisionError) as exc:
            self.result_var.set(str(exc))
            self.input_expr = ''

    # =========================================================================
    # Memory functions
    # =========================================================================

    def _on_memory(self, label: str) -> None:
        if label == 'MC':
            self.memory = ''
        elif label == 'MS':
            self.memory = self._memory_value()
        elif label == 'MR':
            self._on_start_fresh()
            self.input_expr += self.memory
            self.input_var.set(self.input_expr)
        elif label == 'M+':
            try:
                current = float(self._memory_value() or '0')
                stored = float(self.memory or '0')
            except ValueError:
                self.memory = self._memory_value()
            else:
                self.memory = eng.format_result(stored + current)

    def _memory_value(self) -> str:
        """Return the value visible to the user for memory operations."""
        return self.input_var.get() or self.result_var.get()

    # =========================================================================
    # Menu actions
    # =========================================================================

    def _on_copy(self) -> None:
        self.clipboard = self.result_var.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(self.clipboard)

    def _on_paste(self) -> None:
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            return
        if text:
            try:
                float(text)
                self._on_start_fresh()
                self.input_expr += text
                self.input_var.set(self.input_expr)
            except ValueError:
                pass  # ignore non-numeric clipboard content

    def _on_help_document(self) -> None:
        if self.help_window is not None and self.help_window.winfo_exists():
            self.help_window.deiconify()
            self.help_window.lift()
            self.help_window.focus_force()
            return

        window = tk.Toplevel(self.root)
        window.title('计算器帮助')
        window.geometry('760x560')
        window.minsize(680, 480)
        window.transient(self.root)
        window.protocol('WM_DELETE_WINDOW', self._close_help)
        self.help_window = window

        container = tk.Frame(window)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        nav_frame = tk.Frame(container)
        nav_frame.grid(row=0, column=0, sticky='ns', padx=(0, 10))
        tk.Label(
            nav_frame,
            text='目录',
            anchor=tk.W,
            font=(FONT_FAMILY, 11, 'bold'),
        ).pack(fill=tk.X, pady=(0, 5))

        listbox = tk.Listbox(
            nav_frame,
            width=18,
            exportselection=False,
            font=(FONT_FAMILY, 11),
        )
        listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        scrollbar = tk.Scrollbar(nav_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.configure(yscrollcommand=scrollbar.set)

        doc_frame = tk.Frame(container)
        doc_frame.grid(row=0, column=1, sticky='nsew')
        doc_frame.grid_columnconfigure(0, weight=1)
        doc_frame.grid_rowconfigure(0, weight=1)

        text = tk.Text(
            doc_frame,
            wrap=tk.WORD,
            font=('Microsoft YaHei UI', 11),
            padx=14,
            pady=12,
            relief=tk.FLAT,
            bg='#F7F7F7',
            fg=FG_COLOR,
        )
        text.grid(row=0, column=0, sticky='nsew')
        text_scrollbar = tk.Scrollbar(doc_frame, orient=tk.VERTICAL, command=text.yview)
        text_scrollbar.grid(row=0, column=1, sticky='ns')
        text.configure(yscrollcommand=text_scrollbar.set, state=tk.DISABLED)
        text.tag_configure('title', font=('Microsoft YaHei UI', 16, 'bold'), spacing3=10)
        text.tag_configure('body', spacing1=3, spacing3=5)

        self.help_listbox = listbox
        self.help_text = text
        for section in HELP_SECTIONS:
            listbox.insert(tk.END, section)
        listbox.bind('<<ListboxSelect>>', self._on_help_section_selected)
        listbox.selection_set(0)
        self._show_help_section('快速开始')

    def _on_help_section_selected(self, _event: tk.Event) -> None:
        if self.help_listbox is None:
            return
        selection = self.help_listbox.curselection()
        if not selection:
            return
        section = self.help_listbox.get(selection[0])
        self._show_help_section(section)

    def _show_help_section(self, section: str) -> None:
        if self.help_text is None:
            return
        content = HELP_SECTIONS[section]
        title, _, body = content.partition('\n')
        self.help_text.configure(state=tk.NORMAL)
        self.help_text.delete('1.0', tk.END)
        self.help_text.insert(tk.END, title + '\n', 'title')
        self.help_text.insert(tk.END, body.lstrip(), 'body')
        self.help_text.configure(state=tk.DISABLED)
        self.help_text.yview_moveto(0)

    def _close_help(self) -> None:
        if self.help_window is not None and self.help_window.winfo_exists():
            self.help_window.destroy()
        self.help_window = None
        self.help_listbox = None
        self.help_text = None

    def _on_about(self) -> None:
        messagebox.showinfo(
            '关于',
            f'计算器\n版本：{__version__}\n作者：{__author__}',
            parent=self.root,
        )

    # =========================================================================
    # Keyboard bindings
    # =========================================================================

    def _bind_keyboard(self) -> None:
        """Bind keyboard keys to calculator buttons."""
        # Digits
        for digit in '0123456789':
            self.root.bind(f'<Key-{digit}>', lambda _e, d=digit: self._on_button(d))
        # Hex letters (A-F), bound to both lowercase and uppercase
        for letter in 'ABCDEF':
            self.root.bind(f'<Key-{letter.lower()}>',
                           lambda _e, l=letter: self._on_button(l))
            self.root.bind(f'<Key-{letter.upper()}>',
                           lambda _e, l=letter: self._on_button(l))
        # Operators and special keys
        self.root.bind('<period>', lambda _e: self._on_button('.'))
        self.root.bind('<plus>', lambda _e: self._on_button('+'))
        self.root.bind('<minus>', lambda _e: self._on_button('-'))
        self.root.bind('<asterisk>', lambda _e: self._on_button('×'))
        self.root.bind('<slash>', lambda _e: self._on_button('÷'))
        self.root.bind('<asciicircum>', lambda _e: self._on_key_caret())
        self.root.bind('<percent>', lambda _e: self._on_button('M'))
        self.root.bind('<Return>', lambda _e: self._on_button('='))
        self.root.bind('<BackSpace>', lambda _e: self._on_button('←'))
        self.root.bind('<Escape>', lambda _e: self._on_button('AC'))
        self.root.bind('<Delete>', lambda _e: self._on_button('CE'))
        self.root.bind('<parenleft>', lambda _e: self._on_button('('))
        self.root.bind('<parenright>', lambda _e: self._on_button(')'))
        # Programmer-mode bitwise operators mapped from keyboard
        self.root.bind('<ampersand>', lambda _e: self._on_key_bitwise('AND'))
        self.root.bind('<bar>', lambda _e: self._on_key_bitwise('OR'))
        self.root.bind('<asciitilde>', lambda _e: self._on_key_bitwise('NOT'))
        self.root.bind('<less>', lambda _e: self._on_key_bitwise('Lsh'))
        self.root.bind('<greater>', lambda _e: self._on_key_bitwise('Rsh'))

    def _on_key_caret(self) -> None:
        """^ means power in sci mode, XOR in programmer mode."""
        if self.pattern == 'sci':
            self._on_button('^')
        else:
            self._on_button('XOR')

    def _on_key_bitwise(self, label: str) -> None:
        """Bitwise operators only work in programmer mode."""
        if self.pattern != 'sci':
            self._on_button(label)
        # In sci mode, these keys are ignored

    # =========================================================================
    # Launch
    # =========================================================================

    def run(self) -> None:
        self.root.mainloop()
