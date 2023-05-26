""" Digital potentiometer base class """

import math as m
import copy
from typing import Union

from .__helpers import check_not_negative, check_positive, check_integer, coerce, build_tuple
from .potentiometer import Potentiometer
from .digital_winder import DigitalWinder


class DigitalPotentiometerDevice:
    """
    Represents a digital potentiometer device connected to SPI (serial interface).

    A     ┌──────────┐     B
     o────┤   POT    ├─────o
          └─────▲────┘
                │
                o W

    Total resistance of the potentiometer is `r_ab`. All terminals are available for connection.
    W is a programmable winder terminal with output resistance `r_w`.
    Winder position can be set between 0 and `max_value`. Parameter `default_value` sets initial
    winder position. Use None for pots with non-volatile memory.

    For easy operation as voltage source following topology is assumed.

    V_in     ┌────────┐ A     ┌──────────┐     B
         o───┤ R_lim  ├──o────┤   POT    ├──────────┐
             └────────┘       └─────▲────┘          │
                      max_value <── │ ──> 0         │
                                    o W (V_out)    ─┴─ GND
                                    │
                                  ┌───┐
                                  │ R │
                                  │lo-│
                                  │ad │
                                  └───┘
                                    │
                                   ─┴─ GND


    terminal A is connected to voltage supply via current limiting resistor R_lim,
    terminal B is connected to ground. Voltage at W terminal may be set or calculated.
    Terminal W is connected to load resistance R_load.
    By default, `R_load` equals to 1 MOhm, and `R_lim` equals to zero Ohms.

    Device can also be configured in Rheostat mode. In this case terminal A is left floating
    and only terminals B and W are available for connection.

      A     ┌──────────┐     B
       x────┤   POT    ├─────o
            └─────▲────┘
    max_value <── │ ──> 0
                  o W

    Option with `R_lim` and `R_load` connection is also available

      A     ┌──────────┐     B   ┌────────┐   (V_in)
       x────┤   POT    ├─────o───┤ R_lim  ├──o
            └─────▲────┘         └────────┘
    max_value <── │ ──> 0
                  o W (V_out)
                  │
                ┌───┐
                │ R │
                │lo-│
                │ad │
                └───┘
                  │
                 ─┴─ GND
    """

    def __init__(self,
                 potentiometer: Potentiometer,
                 winder: DigitalWinder,
                 channels: int = 1) -> None:
        self.__potentiometer: Potentiometer = potentiometer
        self.__channels: dict[int, DigitalWinder] = {}
        self.__labels: dict[int, str] = {0: '0'}
        for i in range(check_positive(check_integer(channels))):
            winder = copy.deepcopy(winder)
            winder.channel = i
            winder.read()
            self.__channels[i] = winder
            self.__labels[i] = str(i)
        self.__r_lim: tuple[float] = tuple(0.0 for _ in range(self.channels_num))
        self.__r_load: tuple[float] = tuple(0.0 for _ in range(self.channels_num))
        self.__voltage_in: float = 0.0

    def set_channel_label(self, channel: int = 0, label: Union[str, None] = None) -> None:
        """
        Assigns string label to a channel.
        Note that label must be unique, otherwise will rise ValueError.

        :param channel: Channel number.
        :param label: Label for the channel (str).
        """
        channel = check_not_negative(check_integer(channel))
        assert channel in self.__labels
        if label is None:
            label = str(channel)
        try:
            idx = list(self.__labels.values()).index(label)
            if idx != channel:
                raise ValueError(f'Label {label} already assigned to another channel {idx}.')
        except ValueError:
            pass
        self.__labels[channel] = str(label)

    def get_channel_number_by_label(self, label: str) -> Union[int, None]:
        """
        Look for channel number by label provided.

        :param label: Channel label (str).
        :return: Channel number if label found or None.
        """
        try:
            return list(self.__labels.values()).index(label)
        except ValueError:
            return None

    def get_channel_number_by_label_or_id(self, channel: Union[int, str]) -> Union[int, None]:
        """
        Look for channel number by label or number provided.

        :param channel: Channel number or label (int | str).
        :return: Channel number if channel found or None.
        """
        if isinstance(channel, str):
            return self.get_channel_number_by_label(channel)
        channel = check_not_negative(check_integer(channel))
        if channel in self.__channels:
            return channel
        return None

    @property
    def potentiometer(self) -> Potentiometer:
        """ Potentiometer object access. """
        return self.__potentiometer

    @property
    def channels(self) -> dict[int, DigitalWinder]:
        """
        Available channels of the device.

        :return: dict of DigitalWinder objects
        """
        return self.__channels

    @property
    def channels_num(self) -> int:
        """
        Get the number of channels of the device.

        :return: number of available channels as int.
        """
        return len(self.__channels)

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

    def set(self, channel: Union[int, str] = 0, value: int = 0) -> int:
        """
        Method to set the value for a given channel.

        :param channel: Channel number or label (int | str).
        :param value: Winder position value requested (int).
        :return: Winder position value actually set (int).
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f'Channel {channel} not found.')
        self.channels[channel].value = value
        return self.channels[channel].value

    def read(self, channel: Union[int, str] = 0) -> int:
        """
        Read value of given channel.

        :param channel: Channel number or label (int | str).
        :return: Winder position value (int).
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f'Channel {channel} not found.')
        return self.channels[channel].value

    @property
    def value(self) -> tuple[int]:
        """
        Tuple of current values for all channels.

        :return: Tuple of int values for all channels.
        """
        return tuple(winder.value for _, winder in self.channels.items())

    @value.setter
    def value(self, value: Union[list[int], tuple[int]]) -> None:
        if not isinstance(value, (list, tuple)):
            raise ValueError('A tuple or list of values is expected.')
        if len(value) != self.channels_num:
            raise ValueError(f'A tuple or list of length {self.channels_num} is expected.')
        for i in range(self.channels_num):
            self.channels[i].value = value[i]

    def set_r(self, channel: Union[int, str] = 0, resistance: float = 0) -> int:
        """
        Set the resistance for given channel between B and W terminals
        as close as possible to requested value.

        :param channel: Channel number (int)
        :param resistance: Requested resistance as float.
        :return: Winder position value as int.
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f'Channel {channel} not found.')
        value = round(self.potentiometer.r_wb_to_position(resistance)
                      * self.channels[channel_number].max_value)
        return self.set(channel=channel, value=int(value))

    @property
    def r_wb(self) -> tuple[float]:
        """
        Resistance between B and W terminals for all channels as a tuple of floats.

        :return: B-W resistance for all channels as a tuple of floats.
        """
        return tuple(self.potentiometer.r_wb(winder.value / winder.max_value)
                     for _, winder in self.channels.items())

    @r_wb.setter
    def r_wb(self, resistance: Union[list[float], tuple[float]]) -> None:
        if not isinstance(resistance, (list, tuple)):
            raise ValueError('A tuple or list of values is expected.')
        if len(resistance) != self.channels_num:
            raise ValueError(f'A tuple or list of length {self.channels_num} is expected.')
        for i in range(self.channels_num):
            self.set_r(channel=i, resistance=resistance[i])

    @property
    def r_wa(self) -> tuple[float]:
        """
        Resistance between A and W terminals for all channels as a tuple of floats.

        :return: A-W resistance for all channels as a tuple of floats.
        """
        return tuple(self.potentiometer.r_wa(winder.value / winder.max_value)
                     for _, winder in self.channels.items())

    @r_wa.setter
    def r_wa(self, resistance: Union[list[float], tuple[float]]) -> None:
        if not isinstance(resistance, (list, tuple)):
            raise ValueError('A tuple or list of values is expected.')
        if len(resistance) != self.channels_num:
            raise ValueError(f'A tuple or list of length {self.channels_num} is expected.')
        for i in range(self.channels_num):
            self.set_r(channel=i, resistance=self.potentiometer.r_ab - resistance[i])

    # Pot ONLY methods and props

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
        if self.potentiometer.rheostat:
            raise NotImplementedError('Not implemented for Rheostat yet')
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
        if self.potentiometer.rheostat:
            raise NotImplementedError('Not implemented for Rheostat yet')
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
        if self.potentiometer.rheostat:
            raise NotImplementedError('Not implemented for Rheostat yet')
        result: list[float] = []
        for channel in self.channels:
            result.append(self.__value_to_voltage(channel))
        return tuple(result)

    @voltage.setter
    def voltage(self, voltage: Union[list[float], tuple[float]]) -> None:
        if self.potentiometer.rheostat:
            raise NotImplementedError('Not implemented for Rheostat yet')
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
        if self.potentiometer.rheostat:
            raise NotImplementedError('Not implemented for Rheostat yet')
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f'Channel {channel} not found.')
        voltage = coerce(voltage, 0.0, self.voltage_in)
        value = self.__voltage_to_value(channel=channel, voltage=voltage)
        data = self.set(channel=channel, value=value)
        return data
