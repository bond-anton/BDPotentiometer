"""Module contains basic digital wiper class implementation"""

from copy import deepcopy
from typing import Union, cast

from .__helpers import check_integer, check_not_negative, check_positive, clamp
from .__logger import get_logger
from .potentiometer import Potentiometer
from .transport.base import SpiTransport, is_spi_transport


class DigitalWiper:
    """
    Generic digital wiper.

    Moves the wiper of a `Potentiometer` in discrete steps between `min_value`
    (always 0) and `max_code`. The step count is `max_value`; it doubles as the
    full-scale divisor for the wiper position, which is why it can differ from
    the highest accepted code.
    """

    def __init__(
        self,
        potentiometer: Potentiometer,
        max_value: int = 128,
        invert: bool = False,
        **kwargs,
    ) -> None:
        """
        Initialize the wiper.

        :param potentiometer: `Potentiometer` instance the wiper drives.
        :param max_value: Number of discrete steps, also the full-scale divisor (int).
        :param invert: Mirror the wiper position, so value 0 is at terminal A (bool).
        :param kwargs: Optional `label` (logger name) and `log_level`.
        :raises TypeError: If `potentiometer` is not a `Potentiometer`.
        """
        if isinstance(potentiometer, Potentiometer):
            self.__potentiometer: Potentiometer = potentiometer
        else:
            raise TypeError(
                f"Expected an instance of Potentiometer class, got {type(potentiometer)}"
            )
        self.__channel: int = 0
        self.__invert: bool = bool(invert)
        self.__max_value: int = check_integer(check_positive(max_value))
        self.__value: int = 0
        self.logger = get_logger(
            kwargs.get("label", "Digital Wiper"),
            kwargs.get("log_level"),
        )
        self.read()

    @property
    def potentiometer(self) -> Potentiometer:
        """
        Access Potentiometer instance.

        :return: Potentiometer
        """
        return self.__potentiometer

    @property
    def channel(self) -> int:
        """Wiper channel number"""
        return self.__channel

    @channel.setter
    def channel(self, channel_id: int):
        """Set the wiper channel number."""
        self.__channel = check_integer(check_not_negative(channel_id))

    @property
    def invert(self) -> bool:
        """Wiper inversion"""
        return self.__invert

    @invert.setter
    def invert(self, invert: bool) -> None:
        """Set whether the wiper position is mirrored."""
        self.__invert = bool(invert)
        self.logger.debug("Set wiper INVERT to %s", self.__invert)

    @property
    def min_value(self) -> int:
        """
        Returns minimal wiper position, which is always zero.

        :return: Always return 0.
        """
        return 0

    @property
    def max_value(self) -> int:
        """
        Returns device max wiper position value.

        :return: Max wiper position value as int.
        """
        return self.__max_value

    @max_value.setter
    def max_value(self, max_value: int) -> None:
        """Set the number of discrete steps and reshape the current value to it."""
        self.__max_value = check_integer(check_positive(max_value))
        self.logger.debug("Set max value to %d", self.__max_value)
        self.value = self.__value

    @property
    def max_code(self) -> int:
        """
        Highest wiper code accepted by the device.

        `max_value` is the full-scale divisor and may exceed the largest code
        the register can hold (8-bit parts have `max_value` 256 but codes 0..255).
        Override this property where the two differ.

        :return: Highest wiper code as int.
        """
        return self.max_value

    def _read_value(self) -> int:
        """
        Read the wiper position as a code.

        The base class has no bus: it derives the code from
        `potentiometer.wiper_position`. Bus-backed subclasses override this to
        read the device register instead.

        :return: Wiper position value (int).
        """
        return int(round(self.potentiometer.wiper_position * self.max_value))

    def _set_value(self, value: int) -> int:
        """
        Convert a value to a valid code and write it to the wiper.

        The value is clamped to [`min_value`, `max_code`] and inverted when
        `invert` is set, then stored in `potentiometer.wiper_position` as
        `value / max_value`. Bus-backed subclasses override this to send the
        code to the device.

        :param value: Requested wiper position value (int).
        :return: Value actually applied (int).
        """
        value = int(round(clamp(value, 0, self.max_code)))
        value = self.max_code - value if self.invert else value
        self.logger.debug("Setting value to %d", value)
        self.potentiometer.wiper_position = value / self.max_value
        return value

    def read(self) -> None:
        """
        Refresh the cached value from the device.

        Calls `_read_value` and logs a change. The base class reads the
        potentiometer model, bus-backed subclasses read the device register.
        """
        value = self._read_value()
        if self.__value != value:
            self.__value = value
            self.logger.debug("Wiper position updated to %d", value)

    @property
    def value(self) -> int:
        """
        Current wiper position.

        :return: Wiper position value (int).
        """
        self.read()
        if self.invert:
            return self.max_code - self.__value
        return self.__value

    @value.setter
    def value(self, value: int) -> None:
        """
        Set the wiper position value.

        :param value: Requested wiper position value (int), clamped to the valid code range.
        """
        self.__value = self._set_value(value)

    @property
    def value_relative(self) -> float:
        """
        Relative wiper position value in the range 0..1.

        :return: Relative wiper position (float)
        """
        return self.value / self.max_value

    @value_relative.setter
    def value_relative(self, value: float) -> None:
        """
        Set the wiper position from a relative value.

        :param value: Relative wiper position in the range 0..1 (float).
        """
        value = clamp(value, 0, 1)
        value_int = int(round(value * self.max_value))
        self.value = value_int

    @property
    def r_wb(self) -> float:
        """
        Calculates resistance between terminals B and W.

        :return: Resistance between terminals B and W (float).
        """
        return self.potentiometer.r_wb

    @r_wb.setter
    def r_wb(self, resistance: float) -> None:
        """
        Set the resistance between terminals B and W.

        :param resistance: Requested resistance in Ohm (float).
        """
        self.potentiometer.r_wb = resistance
        self.read()

    @property
    def r_wa(self) -> float:
        """
        Calculates resistance between terminals A and W.

        :return: Resistance between terminals A and W (float).
        """
        return self.potentiometer.r_wa

    @r_wa.setter
    def r_wa(self, resistance: float) -> None:
        """
        Set the resistance between terminals A and W.

        :param resistance: Requested resistance in Ohm (float).
        """
        self.potentiometer.r_wa = resistance
        self.read()

    @property
    def v_w(self) -> float:
        """Voltage at wiper terminal"""
        return self.potentiometer.v_w

    @v_w.setter
    def v_w(self, voltage: float) -> None:
        """
        Set the voltage at terminal W.

        :param voltage: Requested voltage in V (float).
        """
        self.potentiometer.v_w = voltage
        self.read()

    def __deepcopy__(self, memo):
        """Deep-copy every attribute, including the potentiometer model."""
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for key, value in self.__dict__.items():
            setattr(result, key, deepcopy(value, memo))
        return result


class SpiDigitalWiper(DigitalWiper):
    """Digital wiper that reaches the device over an SPI transport."""

    def __init__(
        self,
        potentiometer: Potentiometer,
        spi: Union[SpiTransport, None] = None,
        max_value: int = 128,
        invert: bool = False,
        transport: Union[SpiTransport, None] = None,
        **kwargs,
    ):
        """
        Initialize the wiper with an optional SPI transport.

        `SpiDigitalWiper` holds the transport without touching the bus, so it can
        be created before the bus exists and attached later through the
        `transport` or `spi` property. Bus-backed subclasses may read the device
        during construction and then require the transport up front.

        :param potentiometer: `Potentiometer` instance the wiper drives.
        :param spi: SPI transport, kept for compatibility with the old signature.
        :param max_value: Number of discrete steps, also the full-scale divisor (int).
        :param invert: Mirror the wiper position, so value 0 is at terminal A (bool).
        :param transport: Canonical SPI transport; wins over `spi` when both are given.
        :param kwargs: Optional `label` (logger name) and `log_level`.
        :raises TypeError: If the given transport does not implement the SPI protocol.
        """
        self._transport = self._resolve_transport(
            transport if transport is not None else spi
        )
        super().__init__(
            potentiometer=potentiometer, max_value=max_value, invert=invert, **kwargs
        )

    @staticmethod
    def _resolve_transport(value: object) -> Union[SpiTransport, None]:
        if value is None:
            return None
        if is_spi_transport(value):
            return cast(SpiTransport, value)
        raise TypeError(f"Expected an SPI transport with transfer(), got {type(value)}")

    def _require_transport(self) -> SpiTransport:
        if self._transport is None:
            raise ConnectionError("SPI interface not set")
        return self._transport

    @property
    def transport(self) -> Union[SpiTransport, None]:
        """Canonical SPI transport; `spi` is a compatibility accessor."""
        return self._transport

    @transport.setter
    def transport(self, value: Union[SpiTransport, None]) -> None:
        """Set the SPI transport, replacing the current one."""
        self._transport = self._resolve_transport(value)
        self.logger.debug("Transport set to %s", self._transport)

    @property
    def spi(self) -> Union[SpiTransport, None]:
        """
        Compatibility accessor for the SPI interface; `transport` is canonical.

        :return: SPI interface (raw gpiozero SPI if wrapped, else the transport)
        """
        if self._transport is None:
            return None
        return getattr(self._transport, "raw", self._transport)

    @spi.setter
    def spi(self, spi: Union[SpiTransport, None]) -> None:
        """
        Compatibility setter for the SPI interface.

        Only a value implementing the SPI transport protocol is kept; anything
        else is silently stored as `None`.

        :param spi: SPI transport, or `None` to detach the bus.
        """
        self.transport = spi if spi is None or is_spi_transport(spi) else None

    def __deepcopy__(self, memo):
        """
        Deep-copy the wiper, sharing `_transport` with the original.

        The bus handle is not cloned, so both copies talk over the same open
        transport. That is deliberate: the transport owns the device resources
        and closing either copy releases them for both.

        :param memo: Memo dictionary used by `copy.deepcopy`.
        :return: Copied wiper.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for key, value in self.__dict__.items():
            if key == "_transport":
                setattr(result, key, value)
                continue
            setattr(result, key, deepcopy(value, memo))
        return result
