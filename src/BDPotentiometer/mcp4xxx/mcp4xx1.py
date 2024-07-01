""" MCP4XX1 series potentiometers """

from .. import DigitalPotentiometerDevice
from .mcp4xxx import MCP4xxxPotentiometer, MCP4xxxWiper, MCP4xxx


class MCP4xx1(DigitalPotentiometerDevice, MCP4xxx):
    """MCP4XX1 is a single or dual channel digital potentiometer."""

    def __init__(
        self, r_ab: float = 10e3, max_value: int = 128, channels: int = 1, **kwargs
    ) -> None:
        MCP4xxx.__init__(self, **kwargs)
        potentiometer = MCP4xxxPotentiometer(r_ab, **kwargs)
        wiper = MCP4xxxWiper(
            potentiometer=potentiometer, spi=self._spi, max_value=max_value, **kwargs
        )
        DigitalPotentiometerDevice.__init__(
            self, wiper=wiper, channels=channels, **kwargs
        )


class MCP4131(MCP4xx1):
    """7-bit, single channel pot with volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=1, **kwargs)


class MCP4141(MCP4xx1):
    """7-bit, single channel pot with non-volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=1, **kwargs)


class MCP4151(MCP4xx1):
    """8-bit, single channel pot with volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=1, **kwargs)


class MCP4161(MCP4xx1):
    """8-bit, single channel pot with non-volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=1, **kwargs)


class MCP4231(MCP4xx1):
    """7-bit, dual channel pot with volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=2, **kwargs)


class MCP4241(MCP4xx1):
    """7-bit, dual channel pot with non-volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=2, **kwargs)


class MCP4251(MCP4xx1):
    """8-bit, dual channel pot with volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=2, **kwargs)


class MCP4261(MCP4xx1):
    """8-bit, dual channel pot with non-volatile wiper"""

    def __init__(self, r_ab: float = 10e3, **kwargs) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=2, **kwargs)
