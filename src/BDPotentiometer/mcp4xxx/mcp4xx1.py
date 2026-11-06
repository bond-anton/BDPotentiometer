"""MCP4XX1 series potentiometers"""

from typing import Any

from .. import DigitalPotentiometerDevice
from ..__helpers import check_integer
from ..transport.base import SpiTransport
from .mcp4xxx import MCP4xxx, MCP4xxxPotentiometer, MCP4xxxWiper


def _coerce_max_value(max_value: int, expected: int) -> int:
    """
    Validate the full-scale divisor against the chip's fixed value.

    :param max_value: Requested full-scale divisor (int).
    :param expected: Divisor fixed by the chip class, 128 or 256 (int).
    :return: The validated divisor as int.
    :raises TypeError: If `max_value` is not a real number.
    :raises ValueError: If `max_value` differs from `expected`.
    """
    max_value = check_integer(max_value)
    if max_value != expected:
        raise ValueError(
            f"Max value must be {expected} for this chip, got {max_value}."
        )
    return max_value


def _coerce_channels(channels: int, expected: int) -> int:
    """
    Validate the channel count against the chip's channel capacity.

    :param channels: Requested channel count (int).
    :param expected: Number of channels the chip class provides (int).
    :return: The validated channel count as int.
    :raises TypeError: If `channels` is not a real number.
    :raises ValueError: If `channels` is outside ``1..expected``.
    """
    channels = check_integer(channels)
    if not 1 <= channels <= expected:
        raise ValueError(
            f"Channels must be in the range 1..{expected}, got {channels}."
        )
    return channels


class _ChipWiper(MCP4xxxWiper):
    """Wiper whose full-scale divisor is fixed by the chip that built it."""

    def __init__(self, *args, max_value: int, **kwargs) -> None:
        """
        Build the wiper with a divisor that later assignment cannot change.

        :param max_value: Full-scale divisor fixed by the chip class (int).
        :param args: Positional arguments forwarded to `MCP4xxxWiper`.
        :param kwargs: Keywords forwarded to `MCP4xxxWiper`.
        """
        self._fixed_max_value = max_value
        super().__init__(*args, max_value=max_value, **kwargs)

    @property
    def max_value(self) -> int:
        """Full-scale divisor, fixed when the chip is built."""
        return super().max_value

    @max_value.setter
    def max_value(self, max_value: int) -> None:
        """
        Reject any divisor other than the chip's fixed value.

        :param max_value: Requested full-scale divisor (int).
        :raises TypeError: If `max_value` is not a real number.
        :raises ValueError: If `max_value` is not the chip's fixed divisor.
        """
        max_value = check_integer(max_value)
        if max_value != self._fixed_max_value:
            raise ValueError(
                f"Max value is fixed at {self._fixed_max_value} for this chip, "
                f"got {max_value}."
            )
        MCP4xxxWiper.max_value.fset(self, max_value)


class MCP4xx1(DigitalPotentiometerDevice, MCP4xxx):
    """MCP4XX1 is a single or dual channel digital potentiometer."""

    _MAX_VALUE = 128
    _CHANNELS = 1

    def __init__(  # noqa: PLR0913
        self,
        r_ab: float = 10e3,
        max_value: int | None = None,
        channels: int | None = None,
        *,
        transport: SpiTransport | None = None,
        spi: SpiTransport | None = None,
        port: Any = None,
        device: Any = None,
        clock_pin: Any = None,
        mosi_pin: Any = None,
        miso_pin: Any = None,
        select_pin: Any = None,
        invert: bool = False,
        label: str | None = None,
        log_level: int | str | None = None,
    ) -> None:
        """
        Build an MCP4XX1 potentiometer device.

        :param r_ab: Total resistance in ohms; must be in `resistance_list`.
        :param max_value: Full-scale divisor; must equal the chip class
            `_MAX_VALUE` (128 for 7-bit parts, 256 for 8-bit parts). None uses
            the chip class `_MAX_VALUE`.
        :param channels: Channel count, 1..`_CHANNELS`; None uses the chip
            class `_CHANNELS`.
        :param transport: Canonical SPI transport.
        :param spi: Legacy alias for `transport`, used only when `transport`
            is None.
        :param port: spidev bus number, used when no transport is supplied.
        :param device: spidev chip-select line, used when no transport is
            supplied.
        :param clock_pin: GPIO clock pin; any pin keyword selects the
            gpiozero backend.
        :param mosi_pin: GPIO MOSI pin; selects the gpiozero backend.
        :param miso_pin: GPIO MISO pin; selects the gpiozero backend.
        :param select_pin: GPIO chip-select pin; selects the gpiozero backend.
        :param invert: Invert the wiper code mapping when True.
        :param label: Logger name for the device.
        :param log_level: Logger level for the device.
        :raises ValueError: If `r_ab` is not in `resistance_list`, `max_value`
            differs from the chip's `_MAX_VALUE`, or `channels` is outside
            1..`_CHANNELS`.
        :raises TypeError: If `max_value` or `channels` is not a real number,
            or a supplied transport lacks transfer() or close().
        :raises ImportError: If the optional package for the selected backend
            is missing.
        """
        potentiometer = MCP4xxxPotentiometer(r_ab)
        max_value = _coerce_max_value(
            self._MAX_VALUE if max_value is None else max_value, self._MAX_VALUE
        )
        channels = _coerce_channels(
            self._CHANNELS if channels is None else channels, self._CHANNELS
        )
        MCP4xxx.__init__(
            self,
            transport=transport,
            spi=spi,
            port=port,
            device=device,
            clock_pin=clock_pin,
            mosi_pin=mosi_pin,
            miso_pin=miso_pin,
            select_pin=select_pin,
        )
        try:
            wiper = _ChipWiper(
                potentiometer=potentiometer,
                transport=self._transport,
                max_value=max_value,
                invert=invert,
            )
            DigitalPotentiometerDevice.__init__(
                self,
                wiper=wiper,
                channels=channels,
                **{
                    key: value
                    for key, value in (("label", label), ("log_level", log_level))
                    if value is not None
                },
            )
        except Exception:
            self.close()
            raise


class MCP4131(MCP4xx1):
    """7-bit, single channel pot with volatile wiper"""

    _MAX_VALUE = 128
    _CHANNELS = 1


class MCP4141(MCP4xx1):
    """7-bit, single channel pot with non-volatile wiper"""

    _MAX_VALUE = 128
    _CHANNELS = 1


class MCP4151(MCP4xx1):
    """8-bit, single channel pot with volatile wiper"""

    _MAX_VALUE = 256
    _CHANNELS = 1


class MCP4161(MCP4xx1):
    """8-bit, single channel pot with non-volatile wiper"""

    _MAX_VALUE = 256
    _CHANNELS = 1


class MCP4231(MCP4xx1):
    """7-bit, dual channel pot with volatile wiper"""

    _MAX_VALUE = 128
    _CHANNELS = 2


class MCP4241(MCP4xx1):
    """7-bit, dual channel pot with non-volatile wiper"""

    _MAX_VALUE = 128
    _CHANNELS = 2


class MCP4251(MCP4xx1):
    """8-bit, dual channel pot with volatile wiper"""

    _MAX_VALUE = 256
    _CHANNELS = 2


class MCP4261(MCP4xx1):
    """8-bit, dual channel pot with non-volatile wiper"""

    _MAX_VALUE = 256
    _CHANNELS = 2
