# File Name: calculator_engine.py
# Author: hang.shi
# Time: 2026-05-01
# Version: 1.0
# Description: Expression evaluation engine for scientific and programmer calculator modes.

"""Calculator expression evaluation engine.

Provides:
  - Scientific-mode infix-to-postfix (shunting-yard) parsing and RPN evaluation
  - Single-operand functions (sin, cos, tan, log, exp, factorial, reciprocal, negate)
  - Decimal <-> binary conversion
  - Programmer-mode expression evaluation with bitwise / logical / shift operators
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Tuple

__author__ = "hang.shi"

# =============================================================================
# Scientific Calculator — Operator definitions
# (precedence, is_left_associative)
# =============================================================================

_SCI_OPERATORS: Dict[str, Tuple[int, bool]] = {
    '+': (3, True),
    '-': (3, True),
    'M': (4, True),   # modulo
    '*': (4, True),
    '/': (4, True),
    '^': (5, False),  # exponentiation — right-associative
    'v': (5, False),  # root (degree v radicand); internal token, user types √
}

# Characters that are treated as binary operators in scientific mode
_SCI_OP_CHARS: set = {'+', '-', 'M', '*', '/', '^', 'v'}

# =============================================================================
# Scientific — infix → postfix (shunting-yard)
# =============================================================================


def infix_to_postfix(expr: str) -> str:
    """Convert a normalised infix expression to space-delimited postfix (RPN).

    The caller must already have normalised the input (see `normalise_input`).
    The sentinel '#' marks end-of-input; it will be appended if missing.

    Returns:
        Space-delimited RPN token string, e.g. ``"2 3 + 4 *"``.
    """
    if not expr.endswith('#'):
        expr += '#'

    output: List[str] = []
    stack: List[str] = []       # operator stack
    temp: List[str] = []        # current operand accumulator

    def flush() -> None:
        if temp:
            output.append(''.join(temp))
            temp.clear()

    for ch in expr:
        if ch.isdigit() or ch == '.':
            temp.append(ch)
            continue

        if ch == '#':
            flush()
            break

        if ch in _SCI_OP_CHARS:
            flush()
            prec, left_assoc = _SCI_OPERATORS[ch]
            while stack and stack[-1] != '(':
                top_prec, _ = _SCI_OPERATORS.get(stack[-1], (0, True))
                if top_prec > prec or (top_prec == prec and left_assoc):
                    output.append(stack.pop())
                else:
                    break
            stack.append(ch)
            continue

        if ch == '(':
            flush()
            stack.append(ch)
            continue

        if ch == ')':
            flush()
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()          # discard '('
            continue

    while stack:
        output.append(stack.pop())

    return ' '.join(output)


def evaluate_postfix(postfix: str) -> float:
    """Evaluate a space-delimited postfix (RPN) expression.

    Raises:
        ZeroDivisionError: divide-by-zero or modulo-by-zero.
        ValueError: malformed expression or unknown operator.
    """
    tokens = postfix.split()
    stack: List[float] = []

    for token in tokens:
        if not token:
            continue
        first = token[0]
        if first.isdigit() or first == '.':
            stack.append(float(token))
            continue
        if first == '-' and len(token) > 1:
            # Negative number literal produced by the postfix converter
            stack.append(float(token))
            continue

        # Binary operator
        if len(stack) < 2:
            raise ValueError('Incomplete expression')
        b = stack.pop()
        a = stack.pop()
        stack.append(_apply_sci_operator(a, b, token))

    return stack[-1] if stack else 0.0


def _apply_sci_operator(a: float, b: float, op: str) -> float:
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        if b == 0:
            raise ZeroDivisionError('Cannot divide by zero')
        return a / b
    if op == '^':
        return math.pow(a, b)
    if op == 'v':
        if a == 0:
            raise ValueError('0th root is undefined')
        return math.pow(b, 1.0 / a)
    if op == 'M':
        if b == 0:
            raise ZeroDivisionError('Cannot modulo by zero')
        return math.fmod(a, b)
    raise ValueError(f'Unknown operator: {op}')


# =============================================================================
# Input normalisation (same behaviours as the original Java calculator)
# =============================================================================


def normalise_input(raw: str) -> str:
    """Apply the same input normalisations as the original Java calculator.

    * Collapses repeated binary operators into one.
    * Inserts a default ``2`` before ``√`` and ``^`` when there is no
      explicit left operand.
    * Replaces ``(-`` with ``(0-`` so parenthesised negatives parse.
    * Prepends ``0`` when the expression starts with ``-``.
    """
    s = raw

    # Collapse repeats
    for pair in [('++', '+'), ('--', '-'), ('**', '*'), ('//', '/'),
                 ('MM', 'M'), ('^^', '^'), ('..', '.'),
                 ('<<', '<'), ('>>', '>'),
                 ('&&', '&'), ('||', '|')]:
        while pair[0] in s:
            s = s.replace(*pair)

    # Insert default 2-root / 2-power
    # '0√' → replace the zero (0th root = square root)
    s = s.replace('0√', '2√')
    # Insert '2' before √ and ^ when preceded by an operator or paren
    for prefix in ['(', '+', '-', '*', '/', 'M']:
        s = s.replace(f'{prefix}√', f'{prefix}2√')
        s = s.replace(f'{prefix}^', f'{prefix}2^')
    # Leading √ / ^ at position 0
    if s.startswith('√'):
        s = '2√' + s[1:]
    if s.startswith('^'):
        s = '2^' + s[1:]

    # Convert display root symbol to internal token
    s = s.replace('√', 'v')

    # Negative inside parentheses
    s = s.replace('(-', '(0-')

    # Leading minus
    if s.startswith('-'):
        s = '0' + s

    return s


# =============================================================================
# Result formatting
# =============================================================================


def format_result(value: float) -> str:
    """Format numeric result: integer when whole, otherwise decimal.

    Strips trailing zeros from the fractional part.
    """
    if math.isnan(value):
        return 'NaN'
    if math.isinf(value):
        return 'Infinity' if value > 0 else '-Infinity'
    if value == int(value):
        return str(int(value))
    # Up to 14 significant fractional digits, strip trailing zeros
    return f'{value:.14f}'.rstrip('0').rstrip('.')


# =============================================================================
# Single-operand scientific functions
# =============================================================================


def factorial(n: float) -> float:
    """Compute factorial of a non-negative integer.

    Raises ValueError for negative or non-integer input.
    """
    if n < 0:
        raise ValueError('Factorial is only defined for non-negative integers')
    if n != int(n):
        raise ValueError('Factorial is only defined for integers')
    return float(math.factorial(int(n)))


# =============================================================================
# Decimal <-> Binary conversion
# =============================================================================


def decimal_to_binary(num: float, fractional_bits: int = 10) -> str:
    """Convert a decimal float to binary string (e.g. ``"101.01"``)."""
    neg = num < 0
    integer_part = int(abs(num))
    fractional_part = abs(num) - integer_part

    if integer_part == 0:
        int_bin = '0'
    else:
        parts: List[str] = []
        n = integer_part
        while n > 0:
            parts.append(str(n % 2))
            n //= 2
        int_bin = ''.join(reversed(parts))

    frac_bin = ''
    f = fractional_part
    for _ in range(fractional_bits):
        f *= 2
        if f >= 1:
            frac_bin += '1'
            f -= 1
        else:
            frac_bin += '0'
    frac_bin = frac_bin.rstrip('0')

    result = f'{int_bin}.{frac_bin}' if frac_bin else int_bin
    return f'-{result}' if neg else result


def binary_to_decimal(bin_str: str) -> float:
    """Convert a binary string (optionally with fractional part) to float."""
    neg = bin_str.startswith('-')
    if neg:
        bin_str = bin_str[1:]

    if '.' in bin_str:
        int_part, frac_part = bin_str.split('.', 1)
    else:
        int_part, frac_part = bin_str, ''

    result = 0.0
    for i, ch in enumerate(reversed(int_part)):
        if ch == '1':
            result += math.pow(2, i)

    for i, ch in enumerate(frac_part, start=1):
        if ch == '1':
            result += 1.0 / math.pow(2, i)

    return -result if neg else result


# ==============================================================================
# Programmer-mode engine
# ==============================================================================

# Precedence (higher = binds tighter). All programmer binary operators are
# left-associative.
_PROG_PRECEDENCE: Dict[str, int] = {
    '|': 1,
    '^': 2,   # XOR (uses same char as exponentiation in sci mode, but different context)
    '&': 3,
    '<': 4,   # Lsh
    '>': 4,   # Rsh
    '+': 5,
    '-': 5,
    '*': 6,
    '/': 6,
    'M': 6,
}

_PROG_OP_SET: set = {'+', '-', '*', '/', 'M', '&', '|', '^', '<', '>'}


def valid_digits(base: int) -> set:
    if base == 2:
        return {'0', '1'}
    if base == 8:
        return set('01234567')
    if base == 10:
        return set('0123456789')
    if base == 16:
        return set('0123456789ABCDEF')
    raise ValueError(f'Unsupported base: {base}')


def _tokenize_prog(expr: str, base: int) -> List[Tuple[str, str]]:
    """Tokenize a programmer-mode expression into (type, value) pairs."""
    tokens: List[Tuple[str, str]] = []
    current: List[str] = []
    valid = valid_digits(base)

    for ch in expr.upper():
        if ch in valid:
            current.append(ch)
        elif ch in _PROG_OP_SET:
            if current:
                tokens.append(('num', ''.join(current)))
                current.clear()
            tokens.append(('op', ch))
        else:
            raise ValueError(f"Invalid character '{ch}' for base {base}")

    if current:
        tokens.append(('num', ''.join(current)))
    return tokens


def _prog_to_rpn(tokens: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Shunting-yard for programmer-mode tokens."""
    output: List[Tuple[str, str]] = []
    stack: List[Tuple[str, str]] = []

    for kind, value in tokens:
        if kind == 'num':
            output.append((kind, value))
        else:
            prec = _PROG_PRECEDENCE.get(value, 0)
            while stack and stack[-1][0] == 'op':
                top_prec = _PROG_PRECEDENCE.get(stack[-1][1], 0)
                if top_prec >= prec:
                    output.append(stack.pop())
                else:
                    break
            stack.append((kind, value))

    while stack:
        output.append(stack.pop())
    return output


def _eval_prog_rpn(rpn: List[Tuple[str, str]], base: int) -> int:
    """Evaluate programmer-mode RPN, returning integer."""
    stack: List[int] = []

    for kind, value in rpn:
        if kind == 'num':
            stack.append(int(value, base))
        else:
            if len(stack) < 2:
                raise ValueError('Incomplete expression')
            b = stack.pop()
            a = stack.pop()
            stack.append(_apply_prog_op(a, b, value))

    return stack[0] if stack else 0


def _apply_prog_op(a: int, b: int, op: str) -> int:
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        if b == 0:
            raise ZeroDivisionError('Cannot divide by zero')
        return a // b
    if op == 'M':
        if b == 0:
            raise ZeroDivisionError('Cannot modulo by zero')
        return a % b
    if op == '&':
        return a & b
    if op == '|':
        return a | b
    if op == '^':
        return a ^ b
    if op == '<':
        return (a << b) & 0xFFFF_FFFF
    if op == '>':
        return (a & 0xFFFF_FFFF) >> b
    raise ValueError(f'Unknown operator: {op}')


def _format_prog(value: int, base: int) -> str:
    """Format integer result in the target base."""
    if base == 2:
        return bin(value & 0xFFFF_FFFF)[2:] if value >= 0 else bin(value)[3:]
    if base == 8:
        return oct(value & 0xFFFF_FFFF)[2:] if value >= 0 else oct(value)[3:]
    if base == 10:
        return str(value)
    if base == 16:
        return hex(value & 0xFFFF_FFFF)[2:].upper() if value >= 0 else hex(value)[3:].upper()
    return str(value)


def evaluate_programmer(expr: str, base: int) -> Tuple[str, int]:
    """Evaluate a programmer-mode expression in the given base.

    Supports chained operations with full operator precedence.
    Bases: 2 (bin), 8 (oct), 10 (dec), 16 (hex).

    Returns:
        (result_string, result_base).
    """
    if not expr:
        return '0', base

    if expr.startswith('-'):
        expr = '0' + expr

    tokens = _tokenize_prog(expr, base)
    rpn = _prog_to_rpn(tokens)
    result = _eval_prog_rpn(rpn, base)
    return _format_prog(result, base), base


def bitwise_not(value_str: str, base: int, width: int = 32) -> str:
    """Bitwise NOT of a value in the given base, truncated to *width* bits."""
    value = int(value_str, base)
    mask = (1 << width) - 1
    result = (~value) & mask
    return _format_prog(result, base)


def convert_base(value_str: str, from_base: int, to_base: int) -> str:
    """Convert a number string from one base to another."""
    value = int(value_str, from_base)
    return _format_prog(value, to_base)
