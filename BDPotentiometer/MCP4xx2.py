from typing import Union
from BDPotentiometer.DigitalPotentiometer import DigitalRheostatDevice, check_not_negative
from BDPotentiometer.MCP4xxx import MCP4xxx, _coerce_r_ab


class MCP4xx2(MCP4xxx, DigitalRheostatDevice):

    def __init__(self, max_value: int = 128, default_value: Union[int, None] = 64, channels: int = 1,
                 r_ab: float = 10e3, **spi_args) -> None:
        MCP4xxx.__init__(self, **spi_args)
        DigitalRheostatDevice.__init__(self, max_value=max_value, default_value=default_value, channels=channels,
                                       r_ab=_coerce_r_ab(r_ab), r_w=75)

    @DigitalRheostatDevice.max_value.setter
    def max_value(self, max_value: int) -> None:
        pass

    @DigitalRheostatDevice.default_value.setter
    def default_value(self, default_value: Union[int, None]) -> None:
        pass

    @DigitalRheostatDevice.channels_num.setter
    def channels_num(self, channels_num: int) -> None:
        pass

    @DigitalRheostatDevice.r_ab.setter
    def r_ab(self, r_ab: float) -> None:
        DigitalRheostatDevice.r_ab.fset(self, _coerce_r_ab(check_not_negative(r_ab)))

    @DigitalRheostatDevice.r_w.setter
    def r_w(self, r_w: float) -> None:
        pass


class MCP41x2(MCP4xx2):

    def __init__(self, max_value: int = 128, default_value: Union[int, None] = 64,
                 r_ab: float = 10e3, **spi_args) -> None:
        super(MCP41x2, self).__init__(max_value=max_value, default_value=default_value, channels=1,
                                      r_ab=r_ab, **spi_args)


class MCP4132(MCP41x2):

    def __init__(self, r_ab: float = 10e3, **spi_args) -> None:
        super(MCP4132, self).__init__(max_value=128, default_value=64, r_ab=r_ab, **spi_args)


class MCP4142(MCP41x2):

    def __init__(self, r_ab: float = 10e3, **spi_args) -> None:
        super(MCP4142, self).__init__(max_value=128, default_value=None, r_ab=r_ab, **spi_args)


class MCP4152(MCP41x2):

    def __init__(self, r_ab: float = 10e3, **spi_args) -> None:
        super(MCP4152, self).__init__(max_value=256, default_value=128, r_ab=r_ab, **spi_args)


class MCP4162(MCP41x2):

    def __init__(self, r_ab: float = 10e3, **spi_args) -> None:
        super(MCP4162, self).__init__(max_value=256, default_value=None, r_ab=r_ab, **spi_args)
