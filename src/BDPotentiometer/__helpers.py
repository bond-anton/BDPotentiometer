"""This module contains internal helper functions and not supposed to be used outside."""

from math import isnan
from numbers import Integral, Real
from typing import Union


def check_number(num: Union[float, int, Real]) -> Union[float, int]:
    """
    Checks if argument is a real number.
    check_number does not allow argument to be `+inf` or `-inf`, or `NaN`.
    Special float numbers `+0.0` and `-0.0` will be converted to just 0.0

    :param num: variable to check.
    :return: Unchanged `num` as float or int or raises ValueError if num is not a real number.
    """
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
    Checks if `num` is an integer and converts it to int, otherwise raises ValueError.

    :param num: Number (either int or float) to be checked.
    :return: int representation of `num` or rises ValueError.
    """
    num = check_number(num)
    if isinstance(num, float) and not num.is_integer():
        raise ValueError(f"Expected an integer number, got {num}")
    return int(num)


def check_not_negative(num: Union[float, int]) -> Union[float, int]:
    """
    Checks if `num` is a not negative number, otherwise rises ValueError.

    :param num: Either float or int number.
    :return: `num` if it is not negative or rises ValueError.
    """
    num = check_number(num)
    if num < 0:
        raise ValueError(f"Expected non-negative number, got {num}")
    return num


def check_positive(num: Union[float, int]) -> Union[float, int]:
    """
    Checks if `num` is a positive number, otherwise rises ValueError.

    :param num: Either float or int number.
    :return: `num` if it is positive or rises ValueError.
    """
    num = check_number(num)
    if num <= 0:
        raise ValueError(f"Expected a positive number, got {num}")
    return num


def clamp(
    value: Union[float, int], min_value: Union[float, int], max_value: Union[float, int]
) -> Union[float, int]:
    """
    Clamp `value` to given range between `min_value` and `max_value`.

    :param value: Either float or int number to be coerced.
    :param min_value: Lower coerce range boundary.
    :param max_value: Upper coerce range boundary.
    :return: Value coerced to given range.
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
