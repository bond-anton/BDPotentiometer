import math as m

from .__helpers import check_integer, check_not_negative, check_positive, coerce, build_tuple, adjust_tuple


class DigitalRheostatDevice(object):
    """
    Represents a digital potentiometer device connected to SPI (serial interface).
    """

    def __init__(self, max_value: int = 128, default_value: int | None = 64, channels: int = 1,
                 r_ab: float = 10e3, r_w: float = 75) -> None:
        # terminal A is floating, terminals B and W are operational
        self.__default_value: int | None = None
        self.__min_value: int = 0
        self.__max_value: int = 1
        self.max_value = max_value
        self.default_value = default_value
        self.__channels_num: int = 1
        self.__channels: tuple[int] = (0,)
        self._values: list[int] = [0]
        self.channels_num = channels

        self.__r_ab: float = float(check_positive(r_ab))
        self.__r_w: float = float(check_positive(r_w))

    @property
    def min_value(self) -> int:
        return self.__min_value

    @property
    def max_value(self) -> int:
        return self.__max_value

    @max_value.setter
    def max_value(self, max_value: int) -> None:
        self.__max_value = check_positive(check_integer(max_value))
        self.default_value = self.default_value
        try:
            for i in range(self.channels_num):
                self.set(ch=i, value=self._values[i])
        except AttributeError:
            pass

    @property
    def default_value(self) -> int | None:
        return self.__default_value

    @default_value.setter
    def default_value(self, default_value: int | None) -> None:
        if default_value is None:
            self.__default_value = None
        else:
            self.__default_value = self._coerce_value(check_not_negative(check_integer(default_value)))

    @property
    def channels_num(self) -> int:
        return self.__channels_num

    def _init_channels(self) -> None:
        if self.default_value is None:
            self._values = [0 for _ in self.channels]
        else:
            self._values = [self.default_value for _ in self.channels]
        self._read_all()

    @channels_num.setter
    def channels_num(self, channels_num):
        self.__channels_num = check_positive(check_integer(channels_num))
        self.__channels: tuple[int] = tuple([i for i in range(self.__channels_num)])
        self._init_channels()

    @property
    def channels(self) -> tuple[int]:
        return self.__channels

    @property
    def r_ab(self) -> float:
        return self.__r_ab

    @r_ab.setter
    def r_ab(self, r_ab: float) -> None:
        self.__r_ab = float(check_not_negative(r_ab))

    @property
    def r_w(self) -> float:
        return self.__r_w

    @r_w.setter
    def r_w(self, r_w: float) -> None:
        self.__r_w = float(check_not_negative(r_w))

    def __check_channel(self, ch: int) -> None:
        if ch not in self.channels:
            raise ValueError('Channel must be in %s' % str(self.channels))

    def _coerce_value(self, value: int) -> int:
        return coerce(value, 0, self.max_value)

    def __coerce_r(self, r: float) -> float:
        return coerce(r, self.r_w, self.r_ab + self.r_w)

    def _set_value(self, ch: int, value: int) -> int:
        # actually w do not need to repeat the check for ch and value again
        self.__check_channel(ch)
        value = self._coerce_value(value)
        return value

    def _read_value(self, ch: int) -> int:
        return self._values[ch]

    def _read_all(self) -> None:
        for i in range(self.channels_num):
            self._values[i] = self._read_value(self.channels[i])

    def set(self, ch: int = 0, value: int = 0) -> int:
        self.__check_channel(ch)
        value = self._coerce_value(value)
        data = self._set_value(ch, value)
        self._values[ch] = data
        return data

    def read(self, ch: int = 0) -> int:
        self.__check_channel(ch)
        data = self._read_value(ch)
        self._values[ch] = data
        return data

    @property
    def value(self) -> tuple[int]:
        return tuple(self._values)

    @value.setter
    def value(self, v: list[int] | tuple[int]) -> None:
        if not isinstance(v, (list, tuple)):
            raise ValueError('A tuple or list of values expected')
        elif len(v) != self.channels_num:
            raise ValueError('A tuple or list of length {0} expected'.format(self.channels_num))
        for i in range(self.channels_num):
            ch = self.channels[i]
            value = self._coerce_value(check_integer(v[i]))
            data = self._set_value(ch, value)
            self._values[ch] = data

    def set_r(self, ch: int = 0, r: float = 0) -> int:
        r = self.__coerce_r(r)
        v = int(round(((r - self.r_w) / self.r_ab * self.max_value)))
        data = self.set(ch=ch, value=v)
        return data

    @property
    def r_wb(self) -> tuple[float]:
        result: list[float] = []
        for v in self._values:
            r = self.r_ab * v / self.max_value + self.r_w
            result.append(r)
        return tuple(result)

    @r_wb.setter
    def r_wb(self, r: list[float] | tuple[float]) -> None:
        if not isinstance(r, (list, tuple)):
            raise ValueError('A tuple or list of values expected')
        elif len(r) != self.channels_num:
            raise ValueError('A tuple or list of length {0} expected'.format(self.channels_num))
        for i in range(self.channels_num):
            self.set_r(ch=self.channels[i], r=r[i])


class DigitalPotentiometerDevice(DigitalRheostatDevice):
    """
    Represents a digital potentiometer device connected to SPI (serial interface).
    """

    def __init__(self, max_value: int = 128, default_value: int | None = 64, channels: int = 1,
                 r_ab: float = 10e3, r_w: float = 75,
                 r_lim: float | int | list[float] | tuple[float] = 0,
                 r_l: float | int | list[float] | tuple[float] = 1e6,
                 max_voltage: float = 5.0) -> None:
        # connect A to max_voltage and B to ground
        self.__r_lim: tuple[float] = (0.0,)
        self.__r_l: tuple[float] = (0.0,)
        super(DigitalPotentiometerDevice, self).__init__(max_value=max_value, default_value=default_value,
                                                         channels=channels, r_ab=r_ab, r_w=r_w)
        self.r_lim = r_lim
        self.r_l = r_l
        self.__max_voltage: float = check_not_negative(max_voltage)

    @property
    def r_lim(self) -> tuple[float]:
        return self.__r_lim

    @r_lim.setter
    def r_lim(self, r_lim: float | tuple[float] | list[float]) -> None:
        self.__r_lim = build_tuple(r_lim, self.channels_num, check_not_negative)

    @property
    def r_l(self) -> tuple[float]:
        return self.__r_l

    @r_l.setter
    def r_l(self, r_l: float | tuple[float] | list[float]) -> None:
        self.__r_l = build_tuple(r_l, self.channels_num, check_not_negative)

    def _init_channels(self) -> None:
        super(DigitalPotentiometerDevice, self)._init_channels()
        self.r_lim = adjust_tuple(self.r_lim, self.channels_num, 0.0)
        self.r_l = adjust_tuple(self.r_l, self.channels_num, 1.0e6)

    @property
    def max_voltage(self) -> float:
        return self.__max_voltage

    @max_voltage.setter
    def max_voltage(self, max_voltage: float) -> None:
        self.__max_voltage = check_not_negative(max_voltage)

    def __coerce_voltage(self, voltage: float) -> float:
        return coerce(voltage, 0.0, self.max_value)

    def __value_to_voltage(self, ch: int = 0) -> float:
        value = self._values[ch]
        r_lim = self.r_lim[ch]
        r_l = self.r_l[ch] + self.r_w
        div = r_lim / r_l * value
        div += self.r_ab / r_l * (1 - value / self.max_value) * value
        div += (r_lim / self.r_ab + 1) * self.max_value
        return value * self.max_voltage / div

    def __voltage_to_value(self, ch: int = 0, voltage: float = 0) -> int:
        if voltage == 0:
            return 0
        else:
            r_lim = self.r_ab + self.r_lim[ch]
            r_l = self.r_w + self.r_l[ch]
            a = voltage / self.max_value * self.r_ab / r_l
            b = self.max_voltage - voltage * r_lim / r_l
            ac = -voltage * voltage * r_lim / r_l
            descr = b * b - 4 * ac
            return int((-b + m.sqrt(descr)) / (2 * a))

    @property
    def voltage(self) -> tuple[float]:
        result: list[float] = []
        for ch in self.channels:
            result.append(self.__value_to_voltage(ch))
        return tuple(result)

    @voltage.setter
    def voltage(self, voltage: list[float] | tuple[float]) -> None:
        for i in range(self.channels_num):
            self.set_voltage(ch=self.channels[i], voltage=voltage[i])

    def set_voltage(self, ch: int = 0, voltage: float = 0.0) -> int:
        voltage = self.__coerce_voltage(voltage)
        v = self.__voltage_to_value(ch=ch, voltage=voltage)
        data = self.set(ch=ch, value=v)
        return data
