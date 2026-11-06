"""Module contains basic digital wiper class implementation"""

from copy import deepcopy
from typing import cast

from scietex.hal.spi import SpiTransport, is_spi_transport

from .__helpers import (
    check_bool,
    check_integer,
    check_not_negative,
    check_positive,
    clamp,
)
from .__logger import get_logger
from .potentiometer import Potentiometer


class DigitalWiper:
    """
    Generic digital wiper.

    Moves the wiper of a `Potentiometer` in discrete steps between `min_value`
    (always 0) and `max_code`. The step count is `max_value`, which is also the
    full-scale divisor for the wiper position; `max_code` equals `max_value` by
    default, so the reachable codes span `0..max_value`.
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
        :raises TypeError: If `potentiometer` is not a `Potentiometer`, or
            `invert` is not a bool.
        """
        if isinstance(potentiometer, Potentiometer):
            self.__potentiometer: Potentiometer = potentiometer
        else:
            raise TypeError(
                f"Expected an instance of Potentiometer class, got {type(potentiometer)}"
            )
        self.__channel: int = 0
        self.__invert: bool = check_bool(invert)
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
        """
        Set the wiper channel number and reload the cached value.

        The cache belongs to the previous channel, so it is refreshed with
        `read()`. If that read fails (a detached transport or a bus error),
        the previous channel number and the cached code are restored before the
        error is re-raised, so the wiper never reports a new channel while
        still holding the old channel's code.

        :param channel_id: Channel number, a non-negative int.
        :raises TypeError: If `channel_id` is not a real number.
        :raises ValueError: If `channel_id` is negative, fractional, `NaN`, or
            infinite.
        :raises ConnectionError: If `read()` cannot reach the device.
        """
        new_channel = check_integer(check_not_negative(channel_id))
        previous_channel = self.__channel
        previous_value = self.__value
        self.__channel = new_channel
        try:
            self.read()
        except Exception:
            self.__channel = previous_channel
            self.__value = previous_value
            raise

    @property
    def invert(self) -> bool:
        """Wiper inversion"""
        return self.__invert

    @invert.setter
    def invert(self, invert: bool) -> None:
        """
        Set whether the wiper position is mirrored.

        :param invert: True to mirror the position (bool).
        :raises TypeError: If `invert` is not a bool.
        """
        self.__invert = check_bool(invert)
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
        Return the full-scale divisor for wiper positions.

        This is the divisor stored in `potentiometer.wiper_position`; `max_code`
        is the highest accepted code and equals `max_value` by default.
        Subclasses may narrow `max_code`, in which case the top
        `value_relative` step is `max_code / max_value`.

        :return: Full-scale divisor as int.
        """
        return self.__max_value

    @max_value.setter
    def max_value(self, max_value: int) -> None:
        """
        Set the number of discrete steps, preserving the user-facing value.

        The stored code is raw (already inverted), so the user-facing value is
        recomputed before `max_code` changes and then re-applied to the new
        code range. If the re-application fails, both the divisor and the
        cached code are restored before the error is re-raised.

        :param max_value: New full-scale divisor, a positive int.
        :raises TypeError: If `max_value` is not a real number.
        :raises ValueError: If `max_value` is not positive, fractional, `NaN`,
            or infinite.
        """
        new_max_value = check_integer(check_positive(max_value))
        current = self.max_code - self.__value if self.__invert else self.__value
        previous_max_value = self.__max_value
        previous_value = self.__value
        self.__max_value = new_max_value
        self.logger.debug("Set max value to %d", self.__max_value)
        try:
            self.value = current
        except Exception:
            self.__max_value = previous_max_value
            self.__value = previous_value
            raise

    @property
    def max_code(self) -> int:
        """
        Highest wiper code accepted by the device.

        This equals `max_value` by default. Subclasses may narrow it, in which
        case the top `value_relative` step becomes `max_code / max_value`.

        :return: Highest wiper code as int.
        """
        return self.max_value

    def _read_value(self) -> int:
        """
        Read the wiper position as a code.

        The base class has no bus: it derives the code from
        `potentiometer.wiper_position` and clamps it to `0..max_code`, so a
        position of 1.0 never exceeds the accepted code range. Bus-backed
        subclasses override this method and return the device register code
        as read, so the clamp only guards the model-backed base class.

        :return: Wiper position value (int).
        """
        code = int(round(self.potentiometer.wiper_position * self.max_value))
        return min(max(code, 0), self.max_code)

    def _set_value(self, value: int) -> int:
        """
        Convert a value to a valid code and write it to the wiper.

        The value must be an integer: integral floats are accepted, fractional
        values, booleans, `NaN`, and infinities are rejected. It is then
        clamped to `0..max_code` (`min_value` is always 0 and not a bound of
        its own) and inverted when `invert` is set, then stored in
        `potentiometer.wiper_position` as `value / max_value`.
        Bus-backed subclasses override this to send the code to the device.

        :param value: Requested wiper position value (int).
        :return: Raw code applied to the device, already inverted when `invert`
            is set (`_set_value(0)` returns `max_code` on an inverted wiper).
        :raises TypeError: If `value` is not a real number.
        :raises ValueError: If `value` is fractional, `NaN`, or infinite.
        """
        value = int(clamp(check_integer(value), 0, self.max_code))
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

        Fractional values are rejected rather than rounded.

        :param value: Requested wiper position value (int), clamped to the valid code range.
        :raises TypeError: If `value` is not a real number.
        :raises ValueError: If `value` is fractional, `NaN`, or infinite.
        """
        # Validate here as well as in `_set_value`: subclasses that override
        # `_set_value` must still reject fractions through the property.
        self.__value = self._set_value(check_integer(value))

    @property
    def value_relative(self) -> float:
        """
        Relative wiper position, `value / max_value`.

        For the shipped parts `max_code` equals `max_value`, so the reachable
        range is 0..1. A subclass that narrows `max_code` tops out at
        `max_code / max_value`.

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
        spi: SpiTransport | None = None,
        max_value: int = 128,
        invert: bool = False,
        transport: SpiTransport | None = None,
        **kwargs,
    ):
        """
        Initialize the wiper with an optional SPI transport.

        `SpiDigitalWiper` holds the transport without touching the bus, so it can
        be created before the bus exists and attached later through the
        `transport` or `spi` property. Bus-backed subclasses may read the device
        during construction and then require the transport up front.

        :param potentiometer: `Potentiometer` instance the wiper drives.
        :param spi: SPI transport used when `transport` is None; the older name
            for the same argument.
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
    def _resolve_transport(value: object) -> SpiTransport | None:
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
    def transport(self) -> SpiTransport | None:
        """Canonical SPI transport; `spi` is a compatibility accessor."""
        return self._transport

    @transport.setter
    def transport(self, value: SpiTransport | None) -> None:
        """Set the SPI transport, replacing the current one."""
        self._transport = self._resolve_transport(value)
        self.logger.debug("Transport set to %s", self._transport)

    @property
    def spi(self) -> SpiTransport | None:
        """
        Compatibility accessor for the SPI interface; `transport` is canonical.

        :return: The backend's raw handle when the transport exposes a non-None
            `raw` attribute, otherwise the transport itself; `None` when no
            transport is attached.
        """
        if self._transport is None:
            return None
        raw = getattr(self._transport, "raw", None)
        return self._transport if raw is None else raw

    @spi.setter
    def spi(self, spi: SpiTransport | None) -> None:
        """
        Compatibility setter for the SPI interface.

        Assigning the value currently returned by `spi` is a no-op, so
        `wiper.spi = wiper.spi` keeps the transport attached. `None` detaches
        the bus; any other value must satisfy the SPI transport protocol.

        :param spi: SPI transport, the currently exposed handle, or `None`.
        :raises TypeError: If `spi` is neither `None` nor an SPI transport.
        """
        if spi is not None and spi is self.spi:
            return
        self.transport = spi

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
