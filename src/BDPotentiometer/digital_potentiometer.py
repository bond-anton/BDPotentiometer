""" Digital potentiometer base class """

import copy
from typing import Union

from .digital_wiper import DigitalWiper
from .__helpers import check_not_negative, check_positive, check_integer
from .__logger import get_logger


class DigitalPotentiometerDevice:
    """
    Represents a digital potentiometer device connected to SPI (serial interface).

        A     ┌─────────────┐     B
         o────┤Potentiometer├─────o
              └──────▲──────┘
       max_value <── │ ──> 0
                     o W

    Total resistance of the potentiometer is `r_ab`. All terminals are available for connection.
    W is a programmable wiper terminal. Wiper position can be set between 0 and `max_value`.
    Parameter `default_value` sets initial wiper position.
    For pots with non-volatile memory set `default_value` to None.

    Each terminal of the potentiometer has adjustable resistance `r_a`, `r_b`, and `r_w`.
    Wiper is connected to load resistance `r_load`.
    Voltage at the terminals is available via properties `v_a`, `v_b`, `v_load`, and `v_w`.


             A   ┌─────────┐  ┌─────────┐  ┌─────────┐   B
      (V_A)  o───┤   R_A   ├──┤  R_AB   ├──┤   R_B   ├───o  (V_B)
                 └─────────┘  └────▲────┘  └─────────┘
                             1 <── │ ──> 0
                                ┌─────┐
                                │     │
                                │ R_W │
                                │     │
                                └─────┘
                                   │
                                   o W (V_W)
                                   │
                                 ┌───┐
                                 │ L │
                        R_load   │ o │
                                 │ a │
                                 │ d │
                                 └───┘
                                   │
                                   o L (V_L)

    """

    # pylint: disable=too-many-public-methods
    # pylint: disable=too-many-instance-attributes

    def __init__(self, wiper: DigitalWiper, channels: int = 1, **kwargs) -> None:
        self.__channels: dict[int, DigitalWiper] = {}
        self.__labels: dict[int, str] = {0: "0"}
        for i in range(check_integer(check_positive(channels))):
            wiper = copy.deepcopy(wiper)
            wiper.channel = i
            wiper.read()
            self.__channels[i] = wiper
            self.__labels[i] = str(i)
        self.logger = get_logger(
            kwargs.get("label", "DigiPot"), kwargs.get("log_level", None)
        )

    def _get_channel_number_by_label_or_id(
        self, channel: Union[int, str]
    ) -> Union[int, None]:
        """
        Look for channel number by label or number provided.

        :param channel: Channel number or label (int | str).
        :return: Channel number if channel found or None.
        """
        if isinstance(channel, str):
            try:
                return list(self.__labels.values()).index(channel)
            except ValueError:
                return None
        if isinstance(channel, (int, float)):
            channel = check_integer(check_not_negative(channel))
        if channel in self.__channels:
            return channel
        return None

    def set_channel_label(
        self, channel: Union[int, str] = 0, label: Union[str, None] = None
    ) -> None:
        """
        Assigns string label to a channel.
        Note that label must be unique, otherwise will rise ValueError.

        :param channel: Channel number or label.
        :param label: Label for the channel (str).
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} does not exist.")
        if label is None:
            label = str(channel_id)
        for idx, lbl in self.__labels.items():
            if lbl == label and idx != channel_id:
                raise ValueError(f"Label {label} already assigned to channel {idx}.")
        self.__labels[channel_id] = str(label)
        self.logger.debug("Channel %s label is set to %s", channel_id, label)

    @property
    def channels(self) -> dict[int, DigitalWiper]:
        """
        Available channels of the device.

        :return: dict of DigitalWiper objects
        """
        return self.__channels

    @property
    def channels_num(self) -> int:
        """
        Get the number of channels of the device.

        :return: number of available channels as int.
        """
        return len(self.__channels)

    def set_value(self, channel: Union[int, str] = 0, value: int = 0) -> int:
        """
        Method to set the value for a given channel.

        :param channel: Channel number or label (int | str).
        :param value: Wiper position value requested (int).
        :return: Wiper position value actually set (int).
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].value = value
        self.logger.debug("Channel %s value is set to %d", channel_id, value)
        return self.__channels[channel_id].value

    def get_value(self, channel: Union[int, str] = 0) -> int:
        """
        Read value of a given channel.

        :param channel: Channel number or label (int | str).
        :return: Wiper position value (int).
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].value

    @property
    def value(self) -> tuple[int, ...]:
        """
        Tuple of current values for all channels.

        :return: Tuple of int values for all channels.
        """
        return tuple(wiper.value for _, wiper in self.__channels.items())

    @value.setter
    def value(self, value: Union[list[int], tuple[int, ...]]) -> None:
        if not isinstance(value, (list, tuple)):
            raise TypeError(f"A tuple or list of values was expected, got {value}.")
        if len(value) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(value)} of length {len(value)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].value = value[idx]
            self.logger.debug("Channel %s value is set to %d", channel_id, value[idx])

    def set_invert(self, channel: Union[int, str] = 0, invert: bool = False) -> int:
        """
        Set the invert property for a given channel.

        :param channel: Channel number or label (int | str)
        :param invert: bool.
        :return: Wiper position value as int.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].invert = invert
        self.logger.debug("Channel %s invert is set to %s", channel_id, invert)
        return self.__channels[channel_id].value

    def get_invert(self, channel: Union[int, str] = 0) -> bool:
        """
        Get the invert property value for a given channel.

        :param channel: Channel number or label (int | str)
        :return: invert property value as bool.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].invert

    @property
    def invert(self) -> tuple[bool, ...]:
        """
        Tuple of the invert property of channels.

        :return: Invert property values for all channels as a tuple of booleans.
        """
        return tuple(wiper.invert for _, wiper in self.__channels.items())

    @invert.setter
    def invert(self, invert: Union[list[bool], tuple[bool, ...]]) -> None:
        if not isinstance(invert, (list, tuple)):
            raise TypeError(f"A tuple or list of values was expected, got {invert}.")
        if len(invert) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(invert)} of length {len(invert)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].invert = invert[idx]
            self.logger.debug("Channel %s invert is set to %s", channel_id, invert[idx])

    def set_r_wb(self, channel: Union[int, str] = 0, resistance: float = 0) -> int:
        """
        Set the resistance for given channel between B and W terminals
        as close as possible to requested value.

        :param channel: Channel number or label (int | str)
        :param resistance: Requested resistance as float.
        :return: Wiper position value as int.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].r_wb = resistance
        self.logger.debug("Channel %s r_wb is set to %s", channel_id, resistance)
        return self.__channels[channel_id].value

    def get_r_wb(self, channel: Union[int, str] = 0) -> float:
        """
        Get the resistance for given channel between B and W terminals.

        :param channel: Channel number or label (int | str)
        :return: B-W resistance value as float.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].r_wb

    @property
    def r_wb(self) -> tuple[float, ...]:
        """
        Resistance between B and W terminals for all channels as a tuple of floats.

        :return: B-W resistance for all channels as a tuple of floats.
        """
        return tuple(wiper.r_wb for _, wiper in self.channels.items())

    @r_wb.setter
    def r_wb(self, resistance_wb: Union[list[float], tuple[float, ...]]) -> None:
        if not isinstance(resistance_wb, (list, tuple)):
            raise TypeError(
                f"A tuple or list of values was expected, got {resistance_wb}."
            )
        if len(resistance_wb) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(resistance_wb)} of length {len(resistance_wb)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].r_wb = resistance_wb[idx]
            self.logger.debug(
                "Channel %s r_wb is set to %s", channel_id, resistance_wb[idx]
            )

    def set_r_wa(self, channel: Union[int, str] = 0, resistance: float = 0) -> int:
        """
        Set the resistance for given channel between A and W terminals
        as close as possible to requested value.

        :param channel: Channel number or label (int | str)
        :param resistance: Requested resistance as float.
        :return: Wiper position value as int.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].r_wa = resistance
        self.logger.debug("Channel %s r_wa is set to %s", channel_id, resistance)
        return self.__channels[channel_id].value

    def get_r_wa(self, channel: Union[int, str] = 0) -> float:
        """
        Get the resistance for given channel between A and W terminals.

        :param channel: Channel number or label (int | str)
        :return: A-W resistance value as float.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].r_wa

    @property
    def r_wa(self) -> tuple[float, ...]:
        """
        Resistance between A and W terminals for all channels as a tuple of floats.

        :return: A-W resistance for all channels as a tuple of floats.
        """
        return tuple(wiper.r_wa for _, wiper in self.channels.items())

    @r_wa.setter
    def r_wa(self, resistance_wa: Union[list[float], tuple[float, ...]]) -> None:
        if not isinstance(resistance_wa, (list, tuple)):
            raise TypeError(
                f"A tuple or list of values was expected, got {resistance_wa}."
            )
        if len(resistance_wa) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(resistance_wa)} of length {len(resistance_wa)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].r_wa = resistance_wa[idx]
            self.logger.debug(
                "Channel %s r_wa is set to %s", channel_id, resistance_wa[idx]
            )

    def set_r_a(self, channel: Union[int, str] = 0, resistance: float = 0) -> int:
        """
        Set the resistance of the A terminal (this can be current limiting resistor).

        :param channel: Channel number or label (int | str)
        :param resistance: Requested resistance as float.
        :return: Wiper position value as int.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].potentiometer.r_a = resistance
        self.logger.debug("Channel %s r_a is set to %s", channel_id, resistance)
        return self.__channels[channel_id].value

    def get_r_a(self, channel: Union[int, str] = 0) -> float:
        """
        Get the resistance of the A terminal for a given channel.

        :param channel: Channel number or label (int | str)
        :return: A-terminal resistance value as float.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].potentiometer.r_a

    @property
    def r_a(self) -> tuple[float, ...]:
        """Resistance of the A terminal for all channels as a tuple of floats."""
        return tuple(wiper.potentiometer.r_a for _, wiper in self.channels.items())

    @r_a.setter
    def r_a(self, resistance_a: Union[list[float], tuple[float, ...]]) -> None:
        if not isinstance(resistance_a, (list, tuple)):
            raise TypeError(
                f"A tuple or list of values was expected, got {resistance_a}."
            )
        if len(resistance_a) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(resistance_a)} of length {len(resistance_a)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].potentiometer.r_a = resistance_a[idx]
            self.logger.debug(
                "Channel %s r_a is set to %s", channel_id, resistance_a[idx]
            )

    def set_r_b(self, channel: Union[int, str] = 0, resistance: float = 0) -> int:
        """
        Set the resistance of the B terminal (this can be current limiting resistor).

        :param channel: Channel number or label (int | str)
        :param resistance: Requested resistance as float.
        :return: Wiper position value as int.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].potentiometer.r_b = resistance
        self.logger.debug("Channel %s r_b is set to %s", channel_id, resistance)
        return self.__channels[channel_id].value

    def get_r_b(self, channel: Union[int, str] = 0) -> float:
        """
        Get the resistance of the B terminal for a given channel.

        :param channel: Channel number or label (int | str)
        :return: B-terminal resistance value as float.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].potentiometer.r_b

    @property
    def r_b(self) -> tuple[float, ...]:
        """Resistance of the B terminal for all channels as a tuple of floats."""
        return tuple(wiper.potentiometer.r_b for _, wiper in self.channels.items())

    @r_b.setter
    def r_b(self, resistance_b: Union[list[float], tuple[float, ...]]) -> None:
        if not isinstance(resistance_b, (list, tuple)):
            raise TypeError(
                f"A tuple or list of values was expected, got {resistance_b}."
            )
        if len(resistance_b) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(resistance_b)} of length {len(resistance_b)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].potentiometer.r_b = resistance_b[idx]
            self.logger.debug(
                "Channel %s r_b is set to %s", channel_id, resistance_b[idx]
            )

    def set_r_load(self, channel: Union[int, str] = 0, resistance: float = 0) -> int:
        """
        Set the load resistance for a given channel.

        :param channel: Channel number or label (int | str)
        :param resistance: Requested resistance as float.
        :return: Wiper position value as int.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].potentiometer.r_load = resistance
        self.logger.debug("Channel %s r_load is set to %s", channel_id, resistance)
        return self.__channels[channel_id].value

    def get_r_load(self, channel: Union[int, str] = 0) -> float:
        """
        Get the load resistance for a given channel.

        :param channel: Channel number or label (int | str)
        :return: Load resistance value as float.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].potentiometer.r_load

    @property
    def r_load(self) -> tuple[float, ...]:
        """Load Resistance for all channels as a tuple of floats."""
        return tuple(wiper.potentiometer.r_load for _, wiper in self.channels.items())

    @r_load.setter
    def r_load(self, resistance_l: Union[list[float], tuple[float, ...]]) -> None:
        if not isinstance(resistance_l, (list, tuple)):
            raise TypeError(
                f"A tuple or list of values was expected, got {resistance_l}."
            )
        if len(resistance_l) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(resistance_l)} of length {len(resistance_l)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].potentiometer.r_load = resistance_l[idx]
            self.logger.debug(
                "Channel %s r_load is set to %s", channel_id, resistance_l[idx]
            )

    def set_v_a(self, channel: Union[int, str] = 0, voltage: float = 0) -> float:
        """
        Set the terminal A voltage for a given channel.

        :param channel: Channel number or label (int | str)
        :param voltage: Requested voltage.
        :return: Actual voltage.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].potentiometer.v_a = voltage
        self.logger.debug("Channel %s v_a is set to %s", channel_id, voltage)
        return self.__channels[channel_id].potentiometer.v_a

    def get_v_a(self, channel: Union[int, str] = 0) -> float:
        """
        Get the terminal A voltage for a given channel.

        :param channel: Channel number or label (int | str)
        :return: Voltage value as float.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].potentiometer.v_a

    @property
    def v_a(self) -> tuple[float, ...]:
        """Terminal A voltage for all channels as a tuple of floats."""
        return tuple(wiper.potentiometer.v_a for _, wiper in self.channels.items())

    @v_a.setter
    def v_a(self, voltage_a: Union[list[float], tuple[float, ...]]) -> None:
        if not isinstance(voltage_a, (list, tuple)):
            raise TypeError(f"A tuple or list of values was expected, got {voltage_a}.")
        if len(voltage_a) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(voltage_a)} of length {len(voltage_a)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].potentiometer.v_a = voltage_a[idx]
            self.logger.debug("Channel %s v_a is set to %s", channel_id, voltage_a[idx])

    def set_v_b(self, channel: Union[int, str] = 0, voltage: float = 0) -> float:
        """
        Set the terminal B voltage for a given channel.

        :param channel: Channel number or label (int | str)
        :param voltage: Requested voltage.
        :return: Actual voltage.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].potentiometer.v_b = voltage
        self.logger.debug("Channel %s v_b is set to %s", channel_id, voltage)
        return self.__channels[channel_id].potentiometer.v_b

    def get_v_b(self, channel: Union[int, str] = 0) -> float:
        """
        Get the terminal B voltage for a given channel.

        :param channel: Channel number or label (int | str)
        :return: Voltage value as float.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].potentiometer.v_b

    @property
    def v_b(self) -> tuple[float, ...]:
        """Terminal A voltage for all channels as a tuple of floats."""
        return tuple(wiper.potentiometer.v_b for _, wiper in self.channels.items())

    @v_b.setter
    def v_b(self, voltage_b: Union[list[float], tuple[float, ...]]) -> None:
        if not isinstance(voltage_b, (list, tuple)):
            raise TypeError(f"A tuple or list of values was expected, got {voltage_b}.")
        if len(voltage_b) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(voltage_b)} of length {len(voltage_b)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].potentiometer.v_b = voltage_b[idx]
            self.logger.debug("Channel %s v_b is set to %s", channel_id, voltage_b[idx])

    def set_v_load(self, channel: Union[int, str] = 0, voltage: float = 0) -> float:
        """
        Set the voltage at the load for a given channel.

        :param channel: Channel number or label (int | str)
        :param voltage: Requested voltage.
        :return: Actual voltage.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].potentiometer.v_load = voltage
        self.logger.debug("Channel %s v_load is set to %s", channel_id, voltage)
        return self.__channels[channel_id].potentiometer.v_load

    def get_v_load(self, channel: Union[int, str] = 0) -> float:
        """
        Get the voltage at the load for a given channel.

        :param channel: Channel number or label (int | str)
        :return: Voltage value as float.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].potentiometer.v_load

    @property
    def v_load(self) -> tuple[float, ...]:
        """The voltage at the load for all channels as a tuple of floats."""
        return tuple(wiper.potentiometer.v_load for _, wiper in self.channels.items())

    @v_load.setter
    def v_load(self, voltage_l: Union[list[float], tuple[float, ...]]) -> None:
        if not isinstance(voltage_l, (list, tuple)):
            raise TypeError(f"A tuple or list of values was expected, got {voltage_l}.")
        if len(voltage_l) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(voltage_l)} of length {len(voltage_l)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].potentiometer.v_load = voltage_l[idx]
            self.logger.debug(
                "Channel %s v_load is set to %s", channel_id, voltage_l[idx]
            )

    def set_v_w(self, channel: Union[int, str] = 0, voltage: float = 0) -> float:
        """
        Set the terminal W voltage for a given channel.

        :param channel: Channel number or label (int | str)
        :param voltage: Requested voltage.
        :return: Actual voltage.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        self.__channels[channel_id].potentiometer.v_w = voltage
        self.logger.debug("Channel %s v_w is set to %s", channel_id, voltage)
        return self.__channels[channel_id].potentiometer.v_w

    def get_v_w(self, channel: Union[int, str] = 0) -> float:
        """
        Get the terminal W voltage for a given channel.

        :param channel: Channel number or label (int | str)
        :return: Voltage value as float.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        return self.__channels[channel_id].potentiometer.v_w

    @property
    def v_w(self) -> tuple[float, ...]:
        """Terminal W voltage for all channels as a tuple of floats."""
        return tuple(wiper.potentiometer.v_w for _, wiper in self.channels.items())

    @v_w.setter
    def v_w(self, voltage_w: Union[list[float], tuple[float, ...]]) -> None:
        if not isinstance(voltage_w, (list, tuple)):
            raise TypeError(f"A tuple or list of values was expected, got {voltage_w}.")
        if len(voltage_w) != self.channels_num:
            raise ValueError(
                f"A tuple or list of length {self.channels_num} was expected, "
                f"got {type(voltage_w)} of length {len(voltage_w)}."
            )
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].potentiometer.v_w = voltage_w[idx]
            self.logger.debug("Channel %s v_w is set to %s", channel_id, voltage_w[idx])
