""" Digital potentiometer and digital rheostat base classes """

import math as m
from typing import Union

from .potentiometer import Potentiometer
from .digital_winder import DigitalWinder
from .__helpers import (check_integer, check_not_negative, check_positive,
                        coerce, build_tuple, adjust_tuple)


class DigitalRheostatDevice:
    """
    Represents a digital rheostat device connected to SPI (serial interface).

      A     ┌──────────┐     B
       x────┤          ├─────o
            └─────▲────┘
    max_value <── │ ──> 0
                  o W
    Total resistance is `r_ab`, terminal A is floating, terminals W and B are operational.
    W is a programmable winder terminal with output resistance `r_w`.
    Winder position can be set between 0 and `max_value`. Parameter `default_value` sets initial
    winder position. Use None for pots with non-volatile memory.
    """

    def __init__(self,
                 potentiometer: Potentiometer,
                 winder: DigitalWinder,
                 channels: int = 1) -> None:
        # terminal A is floating, terminals B and W are operational
        self.__potentiometer: Potentiometer = potentiometer
        self.__lock_parameters: bool = False
        self.__default_value: Union[int, None] = None
        self.__max_value: int = 1
        self.__max_value_setter(max_value)
        self.__default_value_setter(default_value)
        self.__channels: tuple[int] = (0,)
        self._values: list[int] = [0]
        self.__channels_num_setter(channels)

    @property
    def potentiometer(self) -> Potentiometer:
        """ Potentiometer object access. """
        return self.__potentiometer

    @property
    def locked(self) -> bool:
        """
        Check if parameters of the device are locked.

        :return: True if locked and False otherwise
        """
        return self.__lock_parameters

    @property
    def min_value(self) -> int:
        """
        Returns minimal winder position, which is always zero.
        :return: Always return 0.
        """
        return 0

    @property
    def max_value(self) -> int:
        """
        Returns device max winder position value.

        :return: Max winder position value as int.
        """
        return self.__max_value

    def __max_value_setter(self, max_value: int) -> None:
        """
        Method to alter device max value

        :param max_value:
        """
        self.__max_value = check_positive(check_integer(max_value))
        self.__default_value_setter(self.default_value)
        try:
            for i in range(self.channels_num):
                self.set(channel=i, value=self._values[i])
        except AttributeError:
            pass

    @max_value.setter
    def max_value(self, max_value: int) -> None:
        if not self.locked:
            self.__max_value_setter(max_value)

    @property
    def default_value(self) -> Union[int, None]:
        """
        Returns default winder position value or None for devices with non-volatile memory.

        :return: Default winder position value or None.
        """
        return self.__default_value

    def __default_value_setter(self, default_value: Union[int, None]) -> None:
        """
        Method to alter default winder position value of the device.
        Default value should be either integer number or None for devices with non-volatile memory.

        :param default_value: Either integer number or None.
        """
        if default_value is None:
            self.__default_value = None
        else:
            self.__default_value = self._coerce_value(
                check_not_negative(check_integer(default_value))
            )

    @default_value.setter
    def default_value(self, default_value: Union[int, None]) -> None:
        if not self.locked:
            self.__default_value_setter(default_value)

    @property
    def channels_num(self) -> int:
        """
        Get the number of channels of the device.

        :return: number of available channels as int.
        """
        return len(self.__channels)

    def _init_channels(self) -> None:
        """
        Initializes channels values according to `default_value`
        """
        if self.default_value is None:
            self._values = [0 for _ in self.channels]
        else:
            self._values = [self.default_value for _ in self.channels]
        try:
            self._read_all()
        except AttributeError:
            pass

    def __channels_num_setter(self, channels_num: int) -> None:
        """
        Function to set or alter channels number.

        :param channels_num: Desired number of channels.
        """
        self.__channels = tuple(i for i in range(check_integer(channels_num)))
        self._init_channels()

    @channels_num.setter
    def channels_num(self, channels_num: int) -> None:
        if not self.locked:
            self.__channels_num_setter(channels_num)

    @property
    def channels(self) -> tuple[int]:
        """
        A tuple of available channels of the device.

        :return: Available channels of the device as a tuple of int numbers.
        """
        return self.__channels

    @property
    def r_ab(self) -> float:
        """
        Total resistance of the device between A and B terminals.

        :return: Total resistance as float.
        """
        return self.__potentiometer.r_ab

    @r_ab.setter
    def r_ab(self, r_ab: float) -> None:
        self.__potentiometer.r_ab = r_ab

    @property
    def r_w(self) -> float:
        """
        Winder terminal resistance.

        :return: winder resistance as float.
        """
        return self.__potentiometer.r_w

    @r_w.setter
    def r_w(self, r_w: float) -> None:
        self.__potentiometer.r_w = r_w

    def __check_channel(self, channel: int) -> None:
        """
        Check if channel available for the device.

        :param channel: Queried channel number as int
        """
        if channel not in self.channels:
            raise ValueError(f'Channel must be in {self.channels}')

    def _coerce_value(self, value: int) -> int:
        """
        Coerce given value between zero and `max_value`.

        :param value: Queried value as int number.
        :return: Coerced value as int.
        """
        return coerce(value, 0, self.max_value)

    def _set_value(self, channel: int, value: int) -> int:
        """
        Set given `value` for channel `channel`.

        :param channel: Channel number.
        :param value: Requested value as int.
        :return: Value actually set as int.
        """
        # actually w do not need to repeat the check for ch and value again
        self.__check_channel(channel)
        value = self._coerce_value(value)
        return value

    def _read_value(self, channel: int) -> int:
        """
        Read value of given channel.

        :param channel: Channel number (int).
        :return: Winder position value (int).
        """
        return self._values[channel]

    def _read_all(self) -> None:
        """
        Read values for all available channels into `_values` list.
        """
        for i in range(self.channels_num):
            self._values[i] = self._read_value(self.channels[i])

    def set(self, channel: int = 0, value: int = 0) -> int:
        """
        Method to set the value for a given channel.

        :param channel: Channel number.
        :param value: Value requested as int.
        :return: Value actually set as int.
        """
        self.__check_channel(channel)
        value = self._coerce_value(value)
        data = self._set_value(channel, value)
        self._values[channel] = data
        return data

    def read(self, channel: int = 0) -> int:
        """
        Read value of given channel.

        :param channel: Channel number.
        :return: Winder position value as int.
        """
        self.__check_channel(channel)
        data = self._read_value(channel)
        self._values[channel] = data
        return data

    @property
    def value(self) -> tuple[int]:
        """
        Tuple of current values for all channels.

        :return: Tuple of int values for all channels.
        """
        return tuple(self._values)

    @value.setter
    def value(self, value: Union[list[int], tuple[int]]) -> None:
        if not isinstance(value, (list, tuple)):
            raise ValueError('A tuple or list of values expected')
        if len(value) != self.channels_num:
            raise ValueError(f'A tuple or list of length {self.channels_num} expected')
        for i in range(self.channels_num):
            channel = self.channels[i]
            value_i = self._coerce_value(check_integer(value[i]))
            data = self._set_value(channel, value_i)
            self._values[channel] = data

    def set_r(self, channel: int = 0, resistance: float = 0) -> int:
        """
        Set the resistance for given channel between B and W terminals
        as close as possible to requested value.

        :param channel: Channel number (int)
        :param resistance: Requested resistance as float.
        :return: Winder position value as int.
        """
        value = int(round(self.__potentiometer.r_wb_to_position(resistance) * self.max_value))
        data = self.set(channel=channel, value=value)
        return data

    @property
    def r_wb(self) -> tuple[float]:
        """
        Resistance between B and W terminals for all channels as a tuple of floats.

        :return: Resistance for all channels as a tuple of floats.
        """
        result: list[float] = []
        for value in self._values:
            resistance = self.__potentiometer.r_wb(value / self.max_value)
            result.append(resistance)
        return tuple(result)

    @r_wb.setter
    def r_wb(self, resistance: Union[list[float], tuple[float]]) -> None:
        if not isinstance(resistance, (list, tuple)):
            raise ValueError('A tuple or list of values expected')
        if len(resistance) != self.channels_num:
            raise ValueError(f'A tuple or list of length {self.channels_num} expected')
        for i in range(self.channels_num):
            self.set_r(channel=self.channels[i], resistance=resistance[i])


class DigitalPotentiometerDevice(DigitalRheostatDevice):
    """
    Represents a digital potentiometer device connected to SPI (serial interface).

    A     ┌──────────┐     B
     o────┤          ├─────o
          └─────▲────┘
                │
                o W

    Total resistance of the potentiometer is `r_ab`. All terminals are available for connection.
    W is a programmable winder terminal with output resistance `r_w`.
    Winder position can be set between 0 and `max_value`. Parameter `default_value` sets initial
    winder position. Use None for pots with non-volatile memory.

    For easy operation as voltage source following topology is assumed.

    V     ┌────────┐ A     ┌──────────┐     B
      o───┤ R_lim  ├──o────┤          ├─────┐
          └────────┘       └─────▲────┘     │
                   max_value <── │ ──> 0    │
                                 o W       ─┴─ GND

    terminal A is connected to voltage supply via current limiting resistor R_lim,
    terminal B is connected to ground. Voltage at W terminal may be set or calculated.
    Terminal W is connected to load resistance R_l (not shown).

    """

    def __init__(self, max_value: int = 128, default_value: Union[int, None] = 64,
                 channels: int = 1,
                 r_ab: float = 10e3, r_w: float = 75,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, lock_parameters: bool = False) -> None:
        # connect A to max_voltage and B to ground
        self.__r_lim: tuple[float] = (0.0,)
        self.__r_l: tuple[float] = (0.0,)
        super().__init__(max_value=max_value,
                         default_value=default_value,
                         channels=channels, r_ab=r_ab, r_w=r_w,
                         lock_parameters=lock_parameters)
        self.r_lim = r_lim
        self.r_l = r_l
        self.__max_voltage: float = check_not_negative(max_voltage)

    @property
    def r_lim(self) -> tuple[float]:
        """
        Current limiting resistor R_lim.
        :return: A tuple of `r_lim` values for all available channels.
        """
        return self.__r_lim

    @r_lim.setter
    def r_lim(self, r_lim: Union[float, tuple[float], list[float]]) -> None:
        self.__r_lim = build_tuple(r_lim, self.channels_num, check_not_negative)

    @property
    def r_l(self) -> tuple[float]:
        """
        Load resistor R_l value.
        :rtype: A tuple of load resistor values `r_l` values for all available channels.
        """
        return self.__r_l

    @r_l.setter
    def r_l(self, r_l: Union[float, tuple[float], list[float]]) -> None:
        self.__r_l = build_tuple(r_l, self.channels_num, check_not_negative)

    def _init_channels(self) -> None:
        super()._init_channels()
        self.r_lim = adjust_tuple(self.r_lim, self.channels_num, 0.0)
        self.r_l = adjust_tuple(self.r_l, self.channels_num, 1.0e6)

    @property
    def max_voltage(self) -> float:
        """
        Voltage applied to potentiometer terminal A via current limiting resistor R_lim.

        :return: Voltage applied as float.
        """
        return self.__max_voltage

    @max_voltage.setter
    def max_voltage(self, max_voltage: float) -> None:
        self.__max_voltage = check_not_negative(max_voltage)

    def __coerce_voltage(self, voltage: float) -> float:
        return coerce(voltage, 0.0, self.max_voltage)

    def __value_to_voltage(self, channel: int = 0) -> float:
        value = self._values[channel]
        r_lim = self.r_lim[channel]
        r_l = self.r_l[channel] + self.r_w
        div = r_lim / r_l * value
        div += self.r_ab / r_l * (1 - value / self.max_value) * value
        div += (r_lim / self.r_ab + 1) * self.max_value
        return value * self.max_voltage / div

    def __voltage_to_value(self, channel: int = 0, voltage: float = 0) -> int:
        """
        Calculate winder position value for given channel for a given voltage value.

        :param channel: Channel number (int).
        :param voltage: Voltage at terminal W (float).
        :return: Winder position value (int).
        """
        if voltage == 0:
            return 0
        r_lim = self.r_ab + self.r_lim[channel]
        r_l = self.r_w + self.r_l[channel]
        quad_a = voltage / self.max_value * self.r_ab / r_l
        quad_b = self.max_voltage - voltage * r_lim / r_l
        quad_ac = -voltage * voltage * r_lim / r_l
        quad_d = quad_b ** 2 - 4 * quad_ac
        return int((-quad_b + m.sqrt(quad_d)) / (2 * quad_a))

    @property
    def voltage(self) -> tuple[float]:
        """
        Voltage at winder for all available channels as a tuple of floats.

        :return: A tuple of voltages as floats.
        """
        result: list[float] = []
        for channel in self.channels:
            result.append(self.__value_to_voltage(channel))
        return tuple(result)

    @voltage.setter
    def voltage(self, voltage: Union[list[float], tuple[float]]) -> None:
        for i in range(self.channels_num):
            self.set_voltage(channel=self.channels[i], voltage=voltage[i])

    def set_voltage(self, channel: int = 0, voltage: float = 0.0) -> int:
        """
        Set voltage at winder for a given channel number.

        :param channel: Channel number (int).
        :param voltage: Voltage requested (float).
        :return: Winder position value (int).
        """
        voltage = self.__coerce_voltage(voltage)
        value = self.__voltage_to_value(channel=channel, voltage=voltage)
        data = self.set(channel=channel, value=value)
        return data
