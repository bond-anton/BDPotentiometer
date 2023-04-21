import math as m


class DigitalRheostatDevice(object):
    """
    Represents a digital potentiometer device connected to SPI (serial interface).
    """

    def __init__(self, max_value: int = 128, default_value: int | None = 64, channels: int = 1,
                 r_ab: float = 10e3, r_w: float = 75) -> None:
        # terminal A is floating, terminals B and W are operational
        self.channels: tuple[int] = tuple([i for i in range(channels)])
        self.default_value: int | None = default_value
        self.__values: list[int]
        if self.default_value is None:
            self.__values = [0 for _ in self.channels]
        else:
            self.__values = [self.default_value for _ in self.channels]
        self.min_value: int = 0
        self.max_value: int = max_value
        for i in range(len(self.channels)):
            self.__values[i] = self._read_value(self.channels[i])
        self.r_ab: float = r_ab
        self.r_w: float = r_w

    def __check_channel(self, ch: int) -> None:
        if ch not in self.channels:
            raise ValueError('Channel must be in %s' % self.channels)

    def __coerce_value(self, value: int) -> int:
        if value < 0:
            return 0
        elif value > self.max_value:
            return self.max_value
        return value

    def __coerce_r(self, r: float) -> float:
        if r < self.r_w:
            return self.r_w
        elif r > self.r_ab:
            return self.r_ab
        return r

    def _set_value(self, ch: int, value: int) -> int:
        # actually w do not need to repeat the check for ch and value again
        self.__check_channel(ch)
        value = self.__coerce_value(value)
        return value

    def _read_value(self, ch: int) -> int:
        return self.__values[ch]

    def set(self, ch: int = 0, value: int = 0) -> int:
        self.__check_channel(ch)
        value = self.__coerce_value(value)
        data = self._set_value(ch, value)
        self.__values[ch] = data
        return data

    def read(self, ch: int = 0) -> int:
        self.__check_channel(ch)
        data = self._read_value(ch)
        self.__values[ch] = data
        return data

    @property
    def value(self) -> tuple[int]:
        return tuple(self.__values)

    @value.setter
    def value(self, v: list[int] | tuple[int]) -> None:
        for i in range(len(self.channels)):
            ch = self.channels[i]
            value = self.__coerce_value(v[i])
            data = self._set_value(ch, value)
            self.__values[ch] = data

    def set_r(self, ch: int = 0, r: float = 0) -> int:
        r = self.__coerce_r(r)
        v = int((r - self.r_w) / self.r_ab * self.max_value)
        data = self.set(ch=ch, value=v)
        return data

    @property
    def r_wb(self) -> tuple[float]:
        result: list[float] = []
        for v in self.__values:
            r = self.r_ab * v / self.max_value + self.r_w
            result.append(r)
        return tuple(result)

    @r_wb.setter
    def r_wb(self, r: list[float] | tuple[float]) -> None:
        for i in range(len(self.channels)):
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
        super(DigitalPotentiometerDevice, self).__init__(max_value=max_value, default_value=default_value,
                                                         channels=channels, r_ab=r_ab, r_w=r_w)
        if isinstance(r_lim, (float, int)):
            self.r_lim: tuple[float] = tuple([float(r_lim) for _ in self.channels])
        elif isinstance(r_lim, (list, tuple)):
            self.r_lim = tuple(r_lim)
        if isinstance(r_l, (float, int)):
            self.r_l: tuple[float] = tuple([float(r_l) for _ in self.channels])
        elif isinstance(r_l, (list, tuple)):
            self.r_l = tuple(r_l)
        self.max_voltage: float = max_voltage

    def __coerce_voltage(self, voltage: float) -> float:
        if voltage > self.max_voltage:
            return self.max_voltage
        elif voltage < 0:
            return 0.0
        return voltage

    def __value_to_voltage(self, ch: int = 0) -> float:
        value = self.__values[ch]
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
        for i in range(len(self.channels)):
            self.set_voltage(ch=self.channels[i], voltage=voltage[i])

    def set_voltage(self, ch: int = 0, voltage: float = 0.0) -> int:
        voltage = self.__coerce_voltage(voltage)
        v = self.__voltage_to_value(ch=ch, voltage=voltage)
        data = self.set(ch=ch, value=v)
        return data
