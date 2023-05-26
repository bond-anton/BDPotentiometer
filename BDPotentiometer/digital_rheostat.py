""" Digital rheostat base classes """

import copy
from typing import Union

from .potentiometer import Potentiometer
from .digital_winder import DigitalWinder
from .__helpers import (check_integer, check_not_negative, check_positive)


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
        self.__potentiometer: Potentiometer = potentiometer
        self.__channels: dict[int, DigitalWinder] = {}
        self.__labels: dict[int, str] = {0: '0'}
        for i in range(check_positive(check_integer(channels))):
            winder = copy.deepcopy(winder)
            winder.channel = i
            winder.read()
            self.__channels[i] = winder
            self.__labels[i] = str(i)

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
