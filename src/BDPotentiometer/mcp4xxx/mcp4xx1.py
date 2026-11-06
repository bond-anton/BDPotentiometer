"""MCP4XX1 series potentiometers"""

from typing import Any, Union

from .. import DigitalPotentiometerDevice
from ..transport.base import SpiTransport
from .mcp4xxx import MCP4xxx, MCP4xxxPotentiometer, MCP4xxxWiper


class MCP4xx1(DigitalPotentiometerDevice, MCP4xxx):
    """MCP4XX1 is a single or dual channel digital potentiometer."""

    _MAX_VALUE = 128
    _CHANNELS = 1

    def __init__(  # noqa: PLR0913
        self,
        r_ab: float = 10e3,
        max_value: Union[int, None] = None,
        channels: Union[int, None] = None,
        *,
        transport: Union[SpiTransport, None] = None,
        spi: Union[SpiTransport, None] = None,
        port: Any = None,
        device: Any = None,
        clock_pin: Any = None,
        mosi_pin: Any = None,
        miso_pin: Any = None,
        select_pin: Any = None,
        invert: bool = False,
        label: Union[str, None] = None,
        log_level: Union[int, str, None] = None,
    ) -> None:
        """
        Build an MCP4XX1 potentiometer device.

        :param r_ab: Total resistance in ohms; must be in `resistance_list`.
        :param max_value: Full-scale divisor, 128 or 256; None uses the chip
            class `_MAX_VALUE`.
        :param channels: Channel count; None uses the chip class `_CHANNELS`.
        :param transport: Canonical SPI transport.
        :param spi: Legacy alias for `transport`, used only when `transport`
            is None.
        :param port: gpiozero SPI port, used when no transport is supplied.
        :param device: gpiozero SPI device, used when no transport is supplied.
        :param clock_pin: GPIO clock pin, used when no transport is supplied.
        :param mosi_pin: GPIO MOSI pin, used when no transport is supplied.
        :param miso_pin: GPIO MISO pin, used when no transport is supplied.
        :param select_pin: GPIO chip-select pin, used when no transport is
            supplied.
        :param invert: Invert the wiper code mapping when True.
        :param label: Logger name for the device.
        :param log_level: Logger level for the device.
        :raises ValueError: If `r_ab`, `max_value`, or `channels` is invalid.
        :raises TypeError: If `max_value` is not a real number, or a supplied
            transport lacks transfer() or close().
        """
        if max_value is None:
            max_value = self._MAX_VALUE
        if channels is None:
            channels = self._CHANNELS
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
        potentiometer = MCP4xxxPotentiometer(r_ab)
        wiper = MCP4xxxWiper(
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
