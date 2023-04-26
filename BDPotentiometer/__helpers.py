def check_integer(num: float | int) -> int:
    if isinstance(num, float):
        if not num.is_integer():
            raise ValueError('Argument should be positive integer number')
    elif not isinstance(num, int):
        raise ValueError('Argument should be positive integer number')
    return int(num)


def check_not_negative(num: float | int) -> float | int:
    if not isinstance(num, (float, int)):
        raise ValueError('Argument should be not negative number')
    if num < 0:
        raise ValueError('Argument should be not negative number')
    return num


def check_positive(num: float | int) -> float | int:
    if not isinstance(num, (float, int)):
        raise ValueError('Argument should be a positive number')
    if num <= 0:
        raise ValueError('Argument should be a positive number')
    return num


def coerce(value: float | int, min_value: float | int, max_value: float | int) -> float | int:
    if not (isinstance(value, (float, int))
            and isinstance(min_value, (float, int))
            and isinstance(max_value, (float, int))):
        raise ValueError('Numeric value expected')
    if min_value > max_value:
        min_value, max_value = max_value, min_value
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value


def build_tuple(value, num, func=None):
    def unity(v):
        return v
    if not isinstance(value, (float, int, tuple, list)):
        raise ValueError('Argument should be a number or list or tuple of numbers')
    if not isinstance(num, (float, int)):
        raise ValueError('Argument should be a positive number')
    num = check_positive(check_integer(num))
    if func is not None:
        if not callable(func):
            raise ValueError('function must be callable or None')
    else:
        func = unity

    if isinstance(value, (float, int)):
        return tuple([float(func(value)) for _ in range(num)])
    elif isinstance(value, (list, tuple)):
        if len(value) != num:
            raise ValueError('A tuple or list of length {0} expected'.format(num))
        return tuple([float(func(value_i)) for value_i in value])
    else:
        raise ValueError('A number or a tuple or list of numbers of of length {0} expected'.format(num))


def adjust_tuple(value: tuple[float] | list[float], num: int, default_value: float) -> tuple[float]:
    if not isinstance(value, (tuple, list)):
        raise ValueError('Argument should be a list or a tuple of numbers')
    if not isinstance(num, (float, int)):
        raise ValueError('Argument should be a positive number')
    if not isinstance(default_value, (float, int)):
        raise ValueError('Argument should be a positive number')
    num = check_positive(check_integer(num))
    default_value = float(default_value)
    if len(value) < num:
        return tuple(list(value) + [default_value] * (num - len(value)))
    elif len(value) > num:
        return tuple(value)[:num]
    else:
        return tuple(value)
