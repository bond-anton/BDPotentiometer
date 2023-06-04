"""This module contains internal helper functions and not supposed to be used outside."""

from typing import Union, Callable


def check_number(num: Union[float, int]) -> Union[float, int]:
    """
    Checks if argument is an instance of float or int class.
    :param num: variable to check.
    :return: Unchanged `num` or raises ValueError.
    """
    if not isinstance(num, (float, int)):
        raise ValueError(f"Expected integer or float number, got {type(num)}")
    return num


def check_integer(num: Union[float, int]) -> int:
    """
    Checks if `num` is an integer and converts it to int, otherwise raises ValueError.

    :param num: Number (either int or float) to be checked.
    :return: int representation of `num` or rises ValueError.
    """
    if isinstance(num, float):
        if not num.is_integer():
            raise ValueError("Argument should be integer number")
    elif not isinstance(num, int):
        raise ValueError("Argument should be integer number")
    return int(num)


def check_not_negative(num: Union[float, int]) -> Union[float, int]:
    """
    Checks if `num` is a not negative number, otherwise rises ValueError.

    :param num: Either float or int number.
    :return: `num` if it is not negative or rises ValueError.
    """
    num = check_number(num)
    if num < 0:
        raise ValueError("Argument should be not negative number")
    return num


def check_positive(num: Union[float, int]) -> Union[float, int]:
    """
    Checks if `num` is a positive number, otherwise rises ValueError.

    :param num: Either float or int number.
    :return: `num` if it is positive or rises ValueError.
    """
    num = check_number(num)
    if num <= 0:
        raise ValueError("Argument should be a positive number")
    return num


def coerce(
    value: Union[float, int], min_value: Union[float, int], max_value: Union[float, int]
) -> Union[float, int]:
    """
    Coerce `value` to given range between `min_value` and `max_value`.

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
        return min_value
    if value > max_value:
        return max_value
    return value


def build_tuple(
    value: Union[float, int, tuple, list],
    num: Union[int, float],
    func: Union[Callable, None] = None,
) -> tuple[float, ...]:
    """
    Builds tuple of floats of given length by applying a callable `func` to value.
    If `value` is an iterable (either list or tuple) its length must be equal to `num`.
    The `func` will be applied to each element of the iterable.
    If `value` is a number the resulting tuple of length `num` will be built of same `func(value)`
    elements converted to float.
    If `func` is None the `value` will enter resulting tuple unchanged.

    :param value: Iterable (either list or tuple) or a number.
    :param num: A number of elements in a tuple.
    :param func: Callable to be applied to `value` or None for identity function.
    :return: A tuple of floats of length `num` produced by application of `func` to `value`.
    """

    def identity(val: float) -> float:
        return val

    if not isinstance(value, (float, int, tuple, list)):
        raise ValueError("Argument should be a number or list or tuple of numbers")
    num = check_integer(check_positive(num))
    if func is not None:
        if not callable(func):
            raise ValueError("function must be callable or None")
    else:
        func = identity

    if isinstance(value, (float, int)):
        return tuple(float(func(value)) for _ in range(num))
    if isinstance(value, (list, tuple)):
        if len(value) != num:
            raise ValueError(f"A tuple or list of length {num} expected")
        return tuple(float(func(value_i)) for value_i in value)


def adjust_tuple(
    value: Union[tuple[float], list[float]], num: int, default_value: float
) -> tuple[float, ...]:
    """
    Adjusts tuple or list of floats to a given length `num` and returns a tuple.
    if `num` is less than initial length of the tuple it will be truncated to first `num` elements,
    otherwise it will be appended using `default_value` parameter.

    :param value: Initial iterable (either tuple or list) of float values.
    :param num: Final length of the tuple.
    :param default_value: Default value to populate the tuple if it needs to be grown.
    :return: A tuple of floats of length `num`.
    """
    if not isinstance(value, (tuple, list)):
        raise ValueError("Argument should be a list or a tuple of numbers")
    num = check_integer(check_positive(num))
    default_value = float(check_number(default_value))
    if len(value) < num:
        return tuple(list(value) + [default_value] * (num - len(value)))
    if len(value) > num:
        return tuple(value)[:num]
    return tuple(value)
