"""MCP4XX2 series rheostats"""

from .. import DigitalPotentiometerDevice
from .mcp4xxx import MCP4xxx, MCP4xxxPotentiometer, MCP4xxxWiper


class MCP4xx2(DigitalPotentiometerDevice, MCP4xxx):
    """MCP4XX2 is a single or dual channel digital rheostat."""

    def __init__(
        self, r_ab: float = 10e3, max_value: int = 128, channels: int = 1, **kwargs
    ) -> None:
        MCP4xxx.__init__(self, **kwargs)
        pot_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in ("transport", "spi")
        }
        potentiometer = MCP4xxxPotentiometer(r_ab, **pot_kwargs)
        wiper = MCP4xxxWiper(
            potentiometer=potentiometer,
            transport=self._transport,
            max_value=max_value,
            **pot_kwargs,
        )
        DigitalPotentiometerDevice.__init__(
            self, wiper=wiper, channels=channels, **pot_kwargs
        )


class MCP4132(MCP4xx2):
    """7-bit, single channel rheostat with volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=1, **kwargs)


class MCP4142(MCP4xx2):
    """7-bit, single channel rheostat with non-volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=1, **kwargs)


class MCP4152(MCP4xx2):
    """8-bit, single channel rheostat with volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=1, **kwargs)


class MCP4162(MCP4xx2):
    """8-bit, single channel rheostat with non-volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=1, **kwargs)


class MCP4232(MCP4xx2):
    """7-bit, dual channel rheostat with volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=2, **kwargs)


class MCP4242(MCP4xx2):
    """7-bit, dual channel rheostat with non-volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=2, **kwargs)


class MCP4252(MCP4xx2):
    """8-bit, dual channel rheostat with volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=2, **kwargs)


class MCP4262(MCP4xx2):
    """8-bit, dual channel rheostat with non-volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=2, **kwargs)
