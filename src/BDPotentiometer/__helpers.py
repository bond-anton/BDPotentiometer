"""Internal validation helpers shared by the package.

These functions are not part of the public API. They check the type of an
argument first, raising `TypeError` for anything that is not a real number, and
its value second, raising `ValueError` for infinities, `NaN`, and values outside
the requested range.
"""

from math import isnan
from numbers import Integral, Real
from typing import Union


def check_number(num: Union[float, int, Real]) -> Union[float, int]:
    """
    Check that `num` is a finite real number.

    Infinity and `NaN` are rejected. `bool` is rejected as well even though it
    is an `int` subclass: `True` and `False` are flags, not measurements, and
    accepting them as numbers hides caller mistakes. Both `+0.0` and `-0.0` are
    returned as `0.0`; integers are returned as int, all other numbers as float.

    :param num: variable to check.
    :return: Unchanged `num` as int or float.
    :raises TypeError: If `num` is not a real number, or is a `bool`.
    :raises ValueError: If `num` is infinite or `NaN`.
    """
    if isinstance(num, bool):
        raise TypeError(
            f"Expected a finite integer or float number, not bool {num!r} "
            f"of type {type(num)}"
        )
    if not isinstance(num, Real):
        raise TypeError(f"Expected a finite integer or float number, got {type(num)}")
    if isinstance(num, Integral):
        return int(num)
    if num in [float("inf"), float("-inf")]:
        raise ValueError(f"Expected a finite integer or float number, got {num}")
    if isnan(num):
        raise ValueError("Expected a finite integer or float number, not NaN")
    if num == 0:
        return 0.0
    return float(num)


def check_integer(num: Union[float, int, Real]) -> int:
    """
    Check that `num` is an integer and convert it to int.

    :param num: Number (either int or float) to be checked.
    :return: int representation of `num`.
    :raises TypeError: If `num` is not a real number, or is a `bool`.
    :raises ValueError: If `num` is infinite, `NaN`, or has a fractional part.
    """
    num = check_number(num)
    if isinstance(num, float) and not num.is_integer():
        raise ValueError(f"Expected an integer number, got {num}")
    return int(num)


def check_bool(value: bool) -> bool:
    """
    Check that `value` is a boolean.

    :param value: variable to check.
    :return: Unchanged `value` as bool.
    :raises TypeError: If `value` is not a boolean.
    """
    if not isinstance(value, bool):
        raise TypeError(f"Expected a boolean, got {value!r} of type {type(value)}")
    return value


LABEL_MAX_LENGTH = 64


def check_label(value: str) -> str:
    """
    Check that `value` is a non-empty string usable as a channel label.

    Non-string input is rejected instead of coerced, so a label can never be
    confused with a channel number. Surrounding whitespace is stripped and the
    stripped text is returned, so `" a "` and `"a"` are the same label and an
    all-whitespace string is empty.

    :param value: Label to check.
    :return: Stripped label as str.
    :raises TypeError: If `value` is not a str.
    :raises ValueError: If `value` is empty after stripping, or longer than
        `LABEL_MAX_LENGTH` characters.
    """
    if not isinstance(value, str):
        raise TypeError(f"Expected a string label, got {value!r} of type {type(value)}")
    text = value.strip()
    if not text:
        raise ValueError("Expected a non-empty label")
    if len(text) > LABEL_MAX_LENGTH:
        raise ValueError(
            f"Expected a label of at most {LABEL_MAX_LENGTH} characters, "
            f"got {len(text)}"
        )
    return text


def check_not_negative(num: Union[float, int]) -> Union[float, int]:
    """
    Check that `num` is a not negative number.

    `bool` is rejected as a type error even though it is an `int` subclass; pass
    `0` or `1` explicitly when a numeric flag is intended.

    :param num: Either float or int number.
    :return: `num` unchanged.
    :raises TypeError: If `num` is not a real number, or is a `bool`.
    :raises ValueError: If `num` is negative, infinite, or `NaN`.
    """
    num = check_number(num)
    if num < 0:
        raise ValueError(f"Expected non-negative number, got {num}")
    return num


def check_positive(num: Union[float, int]) -> Union[float, int]:
    """
    Check that `num` is a positive number.

    `bool` is rejected as a type error even though it is an `int` subclass; pass
    `1` explicitly when a numeric flag is intended.

    :param num: Either float or int number.
    :return: `num` unchanged.
    :raises TypeError: If `num` is not a real number, or is a `bool`.
    :raises ValueError: If `num` is zero, negative, infinite, or `NaN`.
    """
    num = check_number(num)
    if num <= 0:
        raise ValueError(f"Expected a positive number, got {num}")
    return num


def clamp(
    value: Union[float, int], min_value: Union[float, int], max_value: Union[float, int]
) -> Union[float, int]:
    """
    Clamp `value` to the range between `min_value` and `max_value`.

    The bounds may be passed in any order: swapped bounds are normalized before
    the comparison. A float `value` always stays a float, even when it is
    clamped to an int bound. All three arguments reject `bool` even though it
    is an `int` subclass; pass `0` or `1` explicitly when a numeric flag is
    intended.

    :param value: Either float or int number to be coerced.
    :param min_value: Lower coerce range boundary.
    :param max_value: Upper coerce range boundary.
    :return: Value coerced to the given range.
    :raises TypeError: If an argument is not a real number, or is a `bool`.
    :raises ValueError: If an argument is infinite or `NaN`.
    """
    value = check_number(value)
    min_value = check_number(min_value)
    max_value = check_number(max_value)
    if min_value > max_value:
        min_value, max_value = max_value, min_value
    if value < min_value:
        if isinstance(value, float):
            return float(min_value)
        return min_value
    if value > max_value:
        if isinstance(value, float):
            return float(max_value)
        return max_value
    return value
