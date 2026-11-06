"""MCP4XX2 series rheostats"""

from typing import Any, Union

from .. import DigitalPotentiometerDevice
from ..transport.base import SpiTransport
from .mcp4xxx import MCP4xxx, MCP4xxxPotentiometer, MCP4xxxWiper


class MCP4xx2(DigitalPotentiometerDevice, MCP4xxx):
    """MCP4XX2 is a single or dual channel digital rheostat."""

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


class MCP4132(MCP4xx2):
    """7-bit, single channel rheostat with volatile wiper"""

    _MAX_VALUE = 128
    _CHANNELS = 1


class MCP4142(MCP4xx2):
    """7-bit, single channel rheostat with non-volatile wiper"""

    _MAX_VALUE = 128
    _CHANNELS = 1


class MCP4152(MCP4xx2):
    """8-bit, single channel rheostat with volatile wiper"""

    _MAX_VALUE = 256
    _CHANNELS = 1


class MCP4162(MCP4xx2):
    """8-bit, single channel rheostat with non-volatile wiper"""

    _MAX_VALUE = 256
    _CHANNELS = 1


class MCP4232(MCP4xx2):
    """7-bit, dual channel rheostat with volatile wiper"""

    _MAX_VALUE = 128
    _CHANNELS = 2


class MCP4242(MCP4xx2):
    """7-bit, dual channel rheostat with non-volatile wiper"""

    _MAX_VALUE = 128
    _CHANNELS = 2


class MCP4252(MCP4xx2):
    """8-bit, dual channel rheostat with volatile wiper"""

    _MAX_VALUE = 256
    _CHANNELS = 2


class MCP4262(MCP4xx2):
    """8-bit, dual channel rheostat with non-volatile wiper"""

    _MAX_VALUE = 256
    _CHANNELS = 2
