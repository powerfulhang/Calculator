# File Name: test_engine.py
# Author: hang.shi
# Time: 2026-05-03
# Version: 1.0
# Description: Unit tests for the calculator expression evaluation engine.

from __future__ import annotations

import math
import pytest

import calculator_engine as eng


# =============================================================================
# infix_to_postfix
# =============================================================================


class TestInfixToPostfix:
    def test_simple_addition(self):
        assert eng.infix_to_postfix('2+3#') == '2 3 +'

    def test_operator_precedence(self):
        assert eng.infix_to_postfix('2+3*4#') == '2 3 4 * +'

    def test_parentheses(self):
        assert eng.infix_to_postfix('(2+3)*4#') == '2 3 + 4 *'

    def test_exponentiation_right_assoc(self):
        assert eng.infix_to_postfix('2^3^2#') == '2 3 2 ^ ^'

    def test_root_operator(self):
        assert eng.infix_to_postfix('2v9#') == '2 9 v'

    def test_modulo(self):
        assert eng.infix_to_postfix('10M3#') == '10 3 M'

    def test_negative_number_at_start(self):
        result = eng.infix_to_postfix('-5+3#')
        assert result == '-5 3 +'

    def test_decimal_number(self):
        assert eng.infix_to_postfix('3.14+2#') == '3.14 2 +'

    def test_nested_parentheses(self):
        assert eng.infix_to_postfix('((2+3))*4#') == '2 3 + 4 *'

    def test_missing_sentinel_appended(self):
        assert eng.infix_to_postfix('1+2') == '1 2 +'

    def test_error_mismatched_parentheses(self):
        with pytest.raises(ValueError, match='括号不匹配'):
            eng.infix_to_postfix('(2+3#')

    def test_error_incomplete_expression(self):
        with pytest.raises(ValueError):
            eng.infix_to_postfix('2+#')

    def test_error_invalid_character(self):
        with pytest.raises(ValueError, match='无效字符'):
            eng.infix_to_postfix('2&3#')


# =============================================================================
# evaluate_postfix
# =============================================================================


class TestEvaluatePostfix:
    def test_simple_addition(self):
        assert eng.evaluate_postfix('2 3 +') == 5.0

    def test_complex_expression(self):
        assert eng.evaluate_postfix('2 3 4 * +') == 14.0

    def test_exponentiation(self):
        assert eng.evaluate_postfix('2 3 ^') == 8.0

    def test_root(self):
        assert eng.evaluate_postfix('2 9 v') == 3.0

    def test_modulo(self):
        assert eng.evaluate_postfix('10 3 M') == 1.0

    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            eng.evaluate_postfix('5 0 /')

    def test_modulo_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            eng.evaluate_postfix('5 0 M')

    def test_single_number(self):
        assert eng.evaluate_postfix('42') == 42.0

    def test_empty_returns_zero(self):
        assert eng.evaluate_postfix('') == 0.0

    def test_negative_literal(self):
        assert eng.evaluate_postfix('-5 3 +') == -2.0


# =============================================================================
# normalise_input
# =============================================================================


class TestNormaliseInput:
    def test_root_with_leading_digit(self):
        assert eng.normalise_input('3√8') == '3v8'

    def test_root_without_leading_digit(self):
        assert eng.normalise_input('√9') == '2v9'

    def test_root_after_operator(self):
        assert eng.normalise_input('2+√9') == '2+2v9'

    def test_root_after_open_paren(self):
        assert eng.normalise_input('(√9)') == '(2v9)'

    def test_no_root(self):
        assert eng.normalise_input('2+3') == '2+3'


# =============================================================================
# format_result
# =============================================================================


class TestFormatResult:
    def test_integer(self):
        assert eng.format_result(4.0) == '4'

    def test_decimal(self):
        assert eng.format_result(3.14) == '3.14'

    def test_trailing_zeros_stripped(self):
        assert eng.format_result(3.140000) == '3.14'

    def test_nan(self):
        assert eng.format_result(float('nan')) == 'NaN'

    def test_positive_infinity(self):
        assert eng.format_result(float('inf')) == 'Infinity'

    def test_negative_infinity(self):
        assert eng.format_result(float('-inf')) == '-Infinity'

    def test_zero(self):
        assert eng.format_result(0.0) == '0'


# =============================================================================
# factorial
# =============================================================================


class TestFactorial:
    def test_zero(self):
        assert eng.factorial(0) == 1.0

    def test_one(self):
        assert eng.factorial(1) == 1.0

    def test_five(self):
        assert eng.factorial(5) == 120.0

    def test_negative(self):
        with pytest.raises(ValueError, match='非负整数'):
            eng.factorial(-1)

    def test_non_integer(self):
        with pytest.raises(ValueError, match='整数'):
            eng.factorial(3.5)


# =============================================================================
# decimal_to_binary / binary_to_decimal
# =============================================================================


class TestBinaryConversion:
    def test_integer(self):
        assert eng.decimal_to_binary(10.0) == '1010'

    def test_fractional(self):
        result = eng.decimal_to_binary(0.5)
        assert result == '0.1'

    def test_mixed(self):
        assert eng.decimal_to_binary(5.5) == '101.1'

    def test_negative(self):
        assert eng.decimal_to_binary(-5.0) == '-101'

    def test_zero(self):
        assert eng.decimal_to_binary(0.0) == '0'

    def test_roundtrip(self):
        original = 13.75
        binary_str = eng.decimal_to_binary(original)
        result = eng.binary_to_decimal(binary_str)
        assert abs(result - original) < 1e-10

    def test_binary_to_decimal_integer(self):
        assert eng.binary_to_decimal('1010') == 10.0

    def test_binary_to_decimal_fractional(self):
        assert eng.binary_to_decimal('0.1') == 0.5

    def test_binary_to_decimal_negative(self):
        assert eng.binary_to_decimal('-101') == -5.0

    def test_binary_to_decimal_invalid(self):
        with pytest.raises(ValueError):
            eng.binary_to_decimal('102')


# =============================================================================
# evaluate_programmer
# =============================================================================


class TestEvaluateProgrammer:
    def test_addition_dec(self):
        result_str, base = eng.evaluate_programmer('3+5', 10)
        assert result_str == '8'
        assert base == 10

    def test_addition_hex(self):
        result_str, _ = eng.evaluate_programmer('A+1', 16)
        assert result_str == 'B'

    def test_addition_bin(self):
        result_str, _ = eng.evaluate_programmer('101+11', 2)
        assert result_str == '1000'

    def test_addition_oct(self):
        result_str, _ = eng.evaluate_programmer('7+1', 8)
        assert result_str == '10'

    def test_operator_precedence(self):
        result_str, _ = eng.evaluate_programmer('2+3*4', 10)
        assert result_str == '14'

    def test_bitwise_and(self):
        result_str, _ = eng.evaluate_programmer('FF&0F', 16)
        assert result_str == 'F'

    def test_bitwise_or(self):
        result_str, _ = eng.evaluate_programmer('F0|0F', 16)
        assert result_str == 'FF'

    def test_xor(self):
        result_str, _ = eng.evaluate_programmer('FF^0F', 16)
        assert result_str == 'F0'

    def test_left_shift(self):
        result_str, _ = eng.evaluate_programmer('1<3', 10)
        assert result_str == '8'

    def test_right_shift(self):
        result_str, _ = eng.evaluate_programmer('8>2', 10)
        assert result_str == '2'

    def test_empty_expression(self):
        result_str, base = eng.evaluate_programmer('', 10)
        assert result_str == '0'
        assert base == 10

    def test_negative_number(self):
        result_str, _ = eng.evaluate_programmer('-5+3', 10)
        assert result_str == '-2'

    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            eng.evaluate_programmer('5/0', 10)

    def test_modulo_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            eng.evaluate_programmer('5M0', 10)


# =============================================================================
# bitwise_not
# =============================================================================


class TestBitwiseNot:
    def test_dec(self):
        result = eng.bitwise_not('0', 10, 32)
        assert result == '4294967295'

    def test_bin(self):
        result = eng.bitwise_not('11110000', 2, 8)
        assert result == '1111'

    def test_hex(self):
        result = eng.bitwise_not('FF', 16, 8)
        assert result == '0'


# =============================================================================
# convert_base
# =============================================================================


class TestConvertBase:
    def test_dec_to_hex(self):
        assert eng.convert_base('255', 10, 16) == 'FF'

    def test_hex_to_dec(self):
        assert eng.convert_base('FF', 16, 10) == '255'

    def test_dec_to_bin(self):
        assert eng.convert_base('10', 10, 2) == '1010'

    def test_bin_to_oct(self):
        assert eng.convert_base('1010', 2, 8) == '12'

    def test_oct_to_hex(self):
        assert eng.convert_base('377', 8, 16) == 'FF'


# =============================================================================
# valid_digits
# =============================================================================


class TestValidDigits:
    def test_bin(self):
        assert eng.valid_digits(2) == {'0', '1'}

    def test_oct(self):
        assert eng.valid_digits(8) == set('01234567')

    def test_dec(self):
        assert eng.valid_digits(10) == set('0123456789')

    def test_hex(self):
        assert eng.valid_digits(16) == set('0123456789ABCDEF')

    def test_unsupported(self):
        with pytest.raises(ValueError):
            eng.valid_digits(3)
