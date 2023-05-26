""" MCP4XX2 series rheostats """

from BDPotentiometer import DigitalPotentiometerDevice
from .mcp4xxx import MCP4xxxPotentiometer, MCP4xxxWinder, MCP4xxx


class MCP4xx2(DigitalPotentiometerDevice, MCP4xxx):
    """ MCP4XX2 is a single or dual channel digital rheostat.  """

    def __init__(self,
                 r_ab: float = 10e3,
                 max_value: int = 128,
                 channels: int = 1,
                 **spi_args) -> None:
        MCP4xxx.__init__(self, **spi_args)
        winder = MCP4xxxWinder(spi=self._spi, max_value=max_value)
        potentiometer = MCP4xxxPotentiometer(r_ab, rheostat=True)
        DigitalPotentiometerDevice.__init__(self,
                                            potentiometer=potentiometer,
                                            winder=winder,
                                            channels=channels)


class MCP4132(MCP4xx2):
    """ 7-bit, single channel rheostat with volatile winder """

    def __init__(self,
                 r_ab: float = 10e3,
                 **spi_args) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=1, **spi_args)


class MCP4142(MCP4xx2):
    """ 7-bit, single channel rheostat with non-volatile winder """

    def __init__(self,
                 r_ab: float = 10e3,
                 **spi_args) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=1, **spi_args)


class MCP4152(MCP4xx2):
    """ 8-bit, single channel rheostat with volatile winder """

    def __init__(self,
                 r_ab: float = 10e3,
                 **spi_args) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=1, **spi_args)


class MCP4162(MCP4xx2):
    """ 8-bit, single channel rheostat with non-volatile winder """

    def __init__(self,
                 r_ab: float = 10e3,
                 **spi_args) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=1, **spi_args)


class MCP4232(MCP4xx2):
    """ 7-bit, dual channel rheostat with volatile winder """

    def __init__(self,
                 r_ab: float = 10e3,
                 **spi_args) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=2, **spi_args)


class MCP4242(MCP4xx2):
    """ 7-bit, dual channel rheostat with non-volatile winder """

    def __init__(self,
                 r_ab: float = 10e3,
                 **spi_args) -> None:
        super().__init__(r_ab=r_ab, max_value=128, channels=2, **spi_args)


class MCP4252(MCP4xx2):
    """ 8-bit, dual channel rheostat with volatile winder """

    def __init__(self,
                 r_ab: float = 10e3,
                 **spi_args) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=2, **spi_args)


class MCP4262(MCP4xx2):
    """ 8-bit, dual channel rheostat with non-volatile winder """

    def __init__(self,
                 r_ab: float = 10e3,
                 **spi_args) -> None:
        super().__init__(r_ab=r_ab, max_value=256, channels=2, **spi_args)
