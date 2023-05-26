""" Digital potentiometer base class """

import math as m
from typing import Union

from .__helpers import check_not_negative, coerce, build_tuple
from .potentiometer import Potentiometer
from .digital_winder import DigitalWinder
from .digital_rheostat import DigitalRheostatDevice


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
    Terminal W is connected to load resistance R_load (not shown).
    By default, `R_load` equals to 1 MOhm, and `R_lim` equals to zero Ohms.

    """

    def __init__(self,
                 potentiometer: Potentiometer,
                 winder: DigitalWinder,
                 channels: int = 1) -> None:
        super().__init__(potentiometer=potentiometer,
                         winder=winder,
                         channels=channels)
        self.__r_lim: tuple[float] = tuple(0.0 for _ in range(self.channels_num))
        self.__r_load: tuple[float] = tuple(0.0 for _ in range(self.channels_num))
        self.__voltage_in: float = 0.0

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
    def r_load(self) -> tuple[float]:
        """
        Load resistor R_load value.
        :rtype: A tuple of load resistor values `r_load` values for all available channels.
        """
        return self.__r_load

    @r_load.setter
    def r_load(self, r_load: Union[float, tuple[float], list[float]]) -> None:
        self.__r_load = build_tuple(r_load, self.channels_num, check_not_negative)

    @property
    def voltage_in(self) -> float:
        """
        Voltage applied to potentiometer terminal A via current limiting resistor R_lim.

        :return: Voltage applied as float.
        """
        return self.__voltage_in

    @voltage_in.setter
    def voltage_in(self, voltage: float) -> None:
        self.__voltage_in = voltage

    def __value_to_voltage(self, channel: int = 0) -> float:
        """
        Calculates output winder terminal voltage for given channel number.
        :param channel: Channel number (int).
        :return: Voltage at terminal W (float).
        """
        value = self.channels[channel].value
        r_lim = self.r_lim[channel]
        r_l = self.r_load[channel] + self.r_w
        div = r_lim / r_l * value
        div += self.r_ab / r_l * (1 - value / self.channels[channel].max_value) * value
        div += (r_lim / self.r_ab + 1) * self.channels[channel].max_value
        return value * self.voltage_in / div

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
        r_l = self.r_w + self.r_load[channel]
        quad_a = voltage / self.channels[channel].max_value * self.r_ab / r_l
        quad_b = self.voltage_in - voltage * r_lim / r_l
        quad_ac = -voltage * voltage * r_lim / r_l
        quad_d = quad_b ** 2 - 4 * quad_ac
        return int((-quad_b + m.sqrt(quad_d)) / (2 * quad_a))

    @property
    def voltage(self) -> tuple[float]:
        """
        Voltage at pot's winder for all available channels as a tuple of floats.

        :return: A tuple of voltages as floats.
        """
        result: list[float] = []
        for channel in self.channels:
            result.append(self.__value_to_voltage(channel))
        return tuple(result)

    @voltage.setter
    def voltage(self, voltage: Union[list[float], tuple[float]]) -> None:
        if not isinstance(voltage, (list, tuple)):
            raise ValueError('A tuple or list of values is expected.')
        if len(voltage) != self.channels_num:
            raise ValueError(f'A tuple or list of length {self.channels_num} is expected.')
        for i in range(self.channels_num):
            self.set_voltage(channel=i, voltage=voltage[i])

    def set_voltage(self, channel: Union[int, str] = 0, voltage: float = 0.0) -> int:
        """
        Set voltage at winder for a given channel number.

        :param channel: Channel number (int).
        :param voltage: Voltage requested (float).
        :return: Winder position value (int).
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f'Channel {channel} not found.')
        voltage = coerce(voltage, 0.0, self.voltage_in)
        value = self.__voltage_to_value(channel=channel, voltage=voltage)
        data = self.set(channel=channel, value=value)
        return data
