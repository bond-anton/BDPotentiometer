"""Digital potentiometer base class"""

import copy
from typing import Any, Callable, Union

from .__helpers import (
    check_bool,
    check_integer,
    check_label,
    check_not_negative,
    check_number,
    check_positive,
)
from .__logger import get_logger
from .digital_wiper import DigitalWiper


def _require_sequence(
    values: Union[list[Any], tuple[Any, ...]],
    length: int,
    check: Callable[[Any], Any],
) -> tuple[Any, ...]:
    """
    Validate the container and every element of a per-channel sequence.

    Every element is checked before the caller writes anything, so a rejected
    element cannot leave the device partially updated.

    :param values: Sequence of per-channel values (list or tuple).
    :param length: Expected sequence length, one element per channel.
    :param check: Validator applied to every element.
    :return: Tuple of validated values.
    :raises TypeError: If `values` is not a list or tuple.
    :raises ValueError: If the sequence length differs from `length`.
    """
    if not isinstance(values, (list, tuple)):
        raise TypeError(f"A tuple or list of values was expected, got {values}.")
    if len(values) != length:
        raise ValueError(
            f"A tuple or list of length {length} was expected, "
            f"got {type(values)} of length {len(values)}."
        )
    return tuple(check(value) for value in values)


class DigitalPotentiometerDevice:
    """
    Container for the channels of a digital potentiometer device.

    The class is transport-agnostic: it only manages `DigitalWiper` channels and
    the `Potentiometer` model behind each of them. Bus access lives in the wiper
    subclass.

        A     ┌─────────────┐     B
         o────┤Potentiometer├─────o
              └──────▲──────┘
        max_code <── │ ──> 0
                     o W

    Total resistance of the potentiometer is `r_ab`. All terminals are available for connection.
    W is a programmable wiper terminal. Wiper position can be set between 0 and `max_code`
    through the per-channel `value` and `value_relative` properties.

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

    def __init__(self, wiper: DigitalWiper, channels: int = 1, **kwargs) -> None:
        """
        Create `channels` independent copies of the prototype wiper.

        :param wiper: `DigitalWiper` prototype; each channel gets a deep copy.
        :param channels: Number of channels to create, must be positive (int).
        :param kwargs: Optional `label` (logger name) and `log_level`.
        """
        self.__channels: dict[int, DigitalWiper] = {}
        self.__labels: dict[int, str] = {0: "0"}
        for i in range(check_integer(check_positive(channels))):
            wiper = copy.deepcopy(wiper)
            wiper.channel = i
            wiper.read()
            self.__channels[i] = wiper
            self.__labels[i] = str(i)
        self.logger = get_logger(
            kwargs.get("label", "DigiPot"), kwargs.get("log_level")
        )

    def _get_channel_number_by_label_or_id(
        self, channel: Union[int, str]
    ) -> Union[int, None]:
        """
        Look for channel number by label or number provided.

        A string is matched against the channel labels first, so a custom label
        always wins over a numeric id. If no label matches, a string that spells
        a non-negative channel number is resolved as an id, so both a custom
        label and the default numeric label reach the same channel. The lookup
        strips surrounding whitespace exactly as `set_channel_label` does.

        Invalid input is reported as "not found" rather than raised. An unknown
        label, a bool, a negative or fractional number, and a value that is not
        a number all return `None`, so callers only check for `None`.

        :param channel: Channel number or label (int | str).
        :return: Channel number if channel found, the matching label's channel
            number, or `None`.
        """
        if isinstance(channel, str):
            text = channel.strip()
            for channel_id, label in self.__labels.items():
                if label == text:
                    return channel_id
            if not text.isdecimal():
                return None
            channel_id = int(text)
            return channel_id if channel_id in self.__channels else None
        if isinstance(channel, bool):
            return None
        try:
            channel_id = check_integer(check_not_negative(channel))
        except (TypeError, ValueError):
            return None
        if channel_id in self.__channels:
            return channel_id
        return None

    def set_channel_label(
        self, channel: Union[int, str] = 0, label: Union[str, None] = None
    ) -> None:
        """
        Assign a string label to a channel.

        Labels must stay unique. Without a label the channel number is used as
        the label, which is how the default numeric labels are restored. A label
        must be a string; it is normalized by stripping surrounding whitespace
        and must stay non-empty after stripping.

        Resetting a label with `label=None` raises `ValueError` as well when the
        channel number is currently taken by another channel: the reset would
        otherwise duplicate that label, and uniqueness is never broken
        silently.

        :param channel: Channel number or label.
        :param label: Label for the channel (str).
        :raises TypeError: If `label` is not a str.
        :raises ValueError: If the channel does not exist, the label is empty,
            too long, or already assigned to another channel.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} does not exist.")
        text = str(channel_id) if label is None else check_label(label)
        for idx, lbl in self.__labels.items():
            if lbl == text and idx != channel_id:
                raise ValueError(f"Label {text} already assigned to channel {idx}.")
        self.__labels[channel_id] = text
        self.logger.debug("Channel %s label is set to %s", channel_id, text)

    @property
    def channels(self) -> dict[int, DigitalWiper]:
        """
        Available channels of the device.

        The returned dictionary is a shallow copy, so adding or removing
        entries does not affect the device.

        :return: dict of DigitalWiper objects
        """
        return dict(self.__channels)

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
        """
        Set the wiper value for all channels.

        :param value: Sequence of length `channels_num`, one value per channel.
        :raises TypeError: If `value` is not a list or tuple, or an element is
            not an integer.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is not a whole, finite number.
        """
        value = _require_sequence(value, self.channels_num, check_integer)
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].value = value[idx]
            self.logger.debug("Channel %s value is set to %d", channel_id, value[idx])

    def set_invert(self, channel: Union[int, str] = 0, invert: bool = False) -> int:
        """
        Set the invert property for a given channel.

        :param channel: Channel number or label (int | str)
        :param invert: bool.
        :return: Wiper position value as int.
        :raises TypeError: If `invert` is not a boolean.
        """
        channel_id = self._get_channel_number_by_label_or_id(channel)
        if channel_id is None:
            raise ValueError(f"Channel {channel} not found.")
        invert = check_bool(invert)
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
        """
        Set the invert property for all channels.

        :param invert: Sequence of length `channels_num`, one flag per channel.
        :raises TypeError: If `invert` is not a list or tuple, or an element is
            not a boolean.
        :raises ValueError: If the sequence length differs from `channels_num`.
        """
        invert = _require_sequence(invert, self.channels_num, check_bool)
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
        return tuple(wiper.r_wb for _, wiper in self.__channels.items())

    @r_wb.setter
    def r_wb(self, resistance_wb: Union[list[float], tuple[float, ...]]) -> None:
        """
        Set the B-W resistance for all channels.

        :param resistance_wb: Sequence of length `channels_num`, one resistance per channel.
        :raises TypeError: If `resistance_wb` is not a list or tuple, or an
            element is not a real number.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is negative, infinite, or `NaN`.
        """
        resistance_wb = _require_sequence(
            resistance_wb, self.channels_num, check_not_negative
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
        return tuple(wiper.r_wa for _, wiper in self.__channels.items())

    @r_wa.setter
    def r_wa(self, resistance_wa: Union[list[float], tuple[float, ...]]) -> None:
        """
        Set the A-W resistance for all channels.

        :param resistance_wa: Sequence of length `channels_num`, one resistance per channel.
        :raises TypeError: If `resistance_wa` is not a list or tuple, or an
            element is not a real number.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is negative, infinite, or `NaN`.
        """
        resistance_wa = _require_sequence(
            resistance_wa, self.channels_num, check_not_negative
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
        return tuple(wiper.potentiometer.r_a for _, wiper in self.__channels.items())

    @r_a.setter
    def r_a(self, resistance_a: Union[list[float], tuple[float, ...]]) -> None:
        """
        Set the A-terminal resistance for all channels.

        :param resistance_a: Sequence of length `channels_num`, one resistance per channel.
        :raises TypeError: If `resistance_a` is not a list or tuple, or an
            element is not a real number.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is negative, infinite, or `NaN`.
        """
        resistance_a = _require_sequence(
            resistance_a, self.channels_num, check_not_negative
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
        return tuple(wiper.potentiometer.r_b for _, wiper in self.__channels.items())

    @r_b.setter
    def r_b(self, resistance_b: Union[list[float], tuple[float, ...]]) -> None:
        """
        Set the B-terminal resistance for all channels.

        :param resistance_b: Sequence of length `channels_num`, one resistance per channel.
        :raises TypeError: If `resistance_b` is not a list or tuple, or an
            element is not a real number.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is negative, infinite, or `NaN`.
        """
        resistance_b = _require_sequence(
            resistance_b, self.channels_num, check_not_negative
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
        return tuple(wiper.potentiometer.r_load for _, wiper in self.__channels.items())

    @r_load.setter
    def r_load(self, resistance_l: Union[list[float], tuple[float, ...]]) -> None:
        """
        Set the load resistance for all channels.

        :param resistance_l: Sequence of length `channels_num`, one resistance per channel.
        :raises TypeError: If `resistance_l` is not a list or tuple, or an
            element is not a real number.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is negative, infinite, or `NaN`.
        """
        resistance_l = _require_sequence(
            resistance_l, self.channels_num, check_not_negative
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
        return tuple(wiper.potentiometer.v_a for _, wiper in self.__channels.items())

    @v_a.setter
    def v_a(self, voltage_a: Union[list[float], tuple[float, ...]]) -> None:
        """
        Set the A-terminal voltage for all channels.

        :param voltage_a: Sequence of length `channels_num`, one voltage per channel.
        :raises TypeError: If `voltage_a` is not a list or tuple, or an element
            is not a real number.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is infinite or `NaN`.
        """
        voltage_a = _require_sequence(voltage_a, self.channels_num, check_number)
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
        """Terminal B voltage for all channels as a tuple of floats."""
        return tuple(wiper.potentiometer.v_b for _, wiper in self.__channels.items())

    @v_b.setter
    def v_b(self, voltage_b: Union[list[float], tuple[float, ...]]) -> None:
        """
        Set the B-terminal voltage for all channels.

        :param voltage_b: Sequence of length `channels_num`, one voltage per channel.
        :raises TypeError: If `voltage_b` is not a list or tuple, or an element
            is not a real number.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is infinite or `NaN`.
        """
        voltage_b = _require_sequence(voltage_b, self.channels_num, check_number)
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
        return tuple(wiper.potentiometer.v_load for _, wiper in self.__channels.items())

    @v_load.setter
    def v_load(self, voltage_l: Union[list[float], tuple[float, ...]]) -> None:
        """
        Set the load voltage for all channels.

        :param voltage_l: Sequence of length `channels_num`, one voltage per channel.
        :raises TypeError: If `voltage_l` is not a list or tuple, or an element
            is not a real number.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is infinite or `NaN`.
        """
        voltage_l = _require_sequence(voltage_l, self.channels_num, check_number)
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
        return tuple(wiper.potentiometer.v_w for _, wiper in self.__channels.items())

    @v_w.setter
    def v_w(self, voltage_w: Union[list[float], tuple[float, ...]]) -> None:
        """
        Set the W-terminal voltage for all channels.

        :param voltage_w: Sequence of length `channels_num`, one voltage per channel.
        :raises TypeError: If `voltage_w` is not a list or tuple, or an element
            is not a real number.
        :raises ValueError: If the sequence length differs from `channels_num`,
            or an element is infinite or `NaN`.
        """
        voltage_w = _require_sequence(voltage_w, self.channels_num, check_number)
        for idx, channel_id in enumerate(self.__channels):
            self.__channels[channel_id].potentiometer.v_w = voltage_w[idx]
            self.logger.debug("Channel %s v_w is set to %s", channel_id, voltage_w[idx])
