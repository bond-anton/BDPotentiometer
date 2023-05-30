""" Digital potentiometer base class """

import copy
from typing import Union

from .__helpers import check_not_negative, check_positive, check_integer
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

    def __init__(self, winder: DigitalWinder, channels: int = 1) -> None:
        self.__channels: dict[int, DigitalWinder] = {}
        self.__labels: dict[int, str] = {0: "0"}
        for i in range(check_integer(check_positive(channels))):
            winder = copy.deepcopy(winder)
            winder.channel = i
            winder.potentiometer.r_lim = 0
            winder.potentiometer.r_load = 0
            winder.potentiometer.voltage_in = 0
            winder.read()
            self.__channels[i] = winder
            self.__labels[i] = str(i)

    def set_channel_label(
        self, channel: int = 0, label: Union[str, None] = None
    ) -> None:
        """
        Assigns string label to a channel.
        Note that label must be unique, otherwise will rise ValueError.

        :param channel: Channel number.
        :param label: Label for the channel (str).
        """
        channel = check_integer(check_not_negative(channel))
        if channel not in self.__labels:
            raise ValueError(f"Channel {channel} does not exist.")
        if label is None:
            label = str(channel)
        for idx, lbl in self.__labels.items():
            if lbl == label and idx != channel:
                raise ValueError(
                    f"Label {label} already assigned to another channel {idx}."
                )
        self.__labels[channel] = str(label)

    def get_channel_number_by_label(self, label: str) -> Union[int, None]:
        """
        Look for channel number by label provided.

        :param label: Channel label (str).
        :return: Channel number if label found or None.
        """
        try:
            return list(self.__labels.values()).index(str(label))
        except ValueError:
            return None

    def get_channel_number_by_label_or_id(
        self, channel: Union[int, str]
    ) -> Union[int, None]:
        """
        Look for channel number by label or number provided.

        :param channel: Channel number or label (int | str).
        :return: Channel number if channel found or None.
        """
        if isinstance(channel, str):
            return self.get_channel_number_by_label(channel)
        channel = check_integer(check_not_negative(channel))
        if channel in self.__channels:
            return channel
        return None

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

    def set(self, channel: Union[int, str] = 0, value: int = 0) -> int:
        """
        Method to set the value for a given channel.

        :param channel: Channel number or label (int | str).
        :param value: Winder position value requested (int).
        :return: Winder position value actually set (int).
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f"Channel {channel} not found.")
        self.channels[channel_number].value = value
        return self.channels[channel_number].value

    def read(self, channel: Union[int, str] = 0) -> int:
        """
        Read value of given channel.

        :param channel: Channel number or label (int | str).
        :return: Winder position value (int).
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.channels[channel_number].value

    @property
    def value(self) -> tuple[int, ...]:
        """
        Tuple of current values for all channels.

        :return: Tuple of int values for all channels.
        """
        return tuple(winder.value for _, winder in self.channels.items())

    @value.setter
    def value(self, value: Union[list[int], tuple[int]]) -> None:
        if not isinstance(value, (list, tuple)):
            raise ValueError("A tuple or list of values is expected.")
        if len(value) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} is expected."
            )
        for i in range(self.channels_num):
            self.channels[i].value = value[i]

    def set_r_wb(self, channel: Union[int, str] = 0, resistance: float = 0) -> int:
        """
        Set the resistance for given channel between B and W terminals
        as close as possible to requested value.

        :param channel: Channel number or label (int | str)
        :param resistance: Requested resistance as float.
        :return: Winder position value as int.
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f"Channel {channel} not found.")
        self.channels[channel_number].r_wb = resistance
        return self.channels[channel_number].value

    def set_r_wa(self, channel: Union[int, str] = 0, resistance: float = 0) -> int:
        """
        Set the resistance for given channel between A and W terminals
        as close as possible to requested value.

        :param channel: Channel number or label (int | str)
        :param resistance: Requested resistance as float.
        :return: Winder position value as int.
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f"Channel {channel} not found.")
        self.channels[channel_number].r_wa = resistance
        return self.channels[channel_number].value

    @property
    def r_wb(self) -> tuple[float, ...]:
        """
        Resistance between B and W terminals for all channels as a tuple of floats.

        :return: B-W resistance for all channels as a tuple of floats.
        """
        return tuple(winder.r_wb for _, winder in self.channels.items())

    @r_wb.setter
    def r_wb(self, resistance: Union[list[float], tuple[float]]) -> None:
        if len(resistance) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} is expected."
            )
        for channel, winder in self.channels.items():
            winder.r_wb = resistance[channel]

    @property
    def r_wa(self) -> tuple[float, ...]:
        """
        Resistance between A and W terminals for all channels as a tuple of floats.

        :return: A-W resistance for all channels as a tuple of floats.
        """
        return tuple(winder.r_wa for _, winder in self.channels.items())

    @r_wa.setter
    def r_wa(self, resistance: Union[list[float], tuple[float]]) -> None:
        if len(resistance) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} is expected."
            )
        for channel, winder in self.channels.items():
            winder.r_wa = resistance[channel]

    @property
    def voltage_in(self) -> tuple[float, ...]:
        """
        Input voltage of the device.

        :return: voltage_in tuple of floats.
        """
        return tuple(winder.voltage_in for _, winder in self.channels.items())

    @voltage_in.setter
    def voltage_in(self, voltage: Union[list[float], tuple[float]]) -> None:
        if len(voltage) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} is expected."
            )
        for channel, winder in self.channels.items():
            winder.voltage_in = voltage[channel]

    @property
    def voltage_out(self) -> tuple[float, ...]:
        """
        Voltage at pot's winder for all available channels as a tuple of floats.

        :return: A tuple of voltages as floats.
        """
        return tuple(winder.voltage_out for _, winder in self.channels.items())

    @voltage_out.setter
    def voltage_out(self, voltage: Union[list[float], tuple[float]]) -> None:
        if len(voltage) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} is expected."
            )
        for channel, winder in self.channels.items():
            winder.voltage_out = voltage[channel]

    def set_voltage_in(self, channel: Union[int, str] = 0, voltage: float = 0.0) -> int:
        """
        Set input voltage for a given channel number.

        :param channel: Channel number (int).
        :param voltage: Voltage (float).
        :return: Winder position value (int).
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f"Channel {channel} not found.")
        self.channels[channel_number].voltage_in = voltage
        return self.channels[channel_number].value

    def set_voltage_out(
        self, channel: Union[int, str] = 0, voltage: float = 0.0
    ) -> int:
        """
        Set voltage at winder for a given channel number.

        :param channel: Channel number (int).
        :param voltage: Voltage requested (float).
        :return: Winder position value (int).
        """
        channel_number = self.get_channel_number_by_label_or_id(channel)
        if channel_number is None:
            raise ValueError(f"Channel {channel} not found.")
        self.channels[channel_number].voltage_out = voltage
        return self.channels[channel_number].value
