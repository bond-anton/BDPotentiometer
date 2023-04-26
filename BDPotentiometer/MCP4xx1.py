from typing import Union
from BDPotentiometer.DigitalPotentiometer import DigitalPotentiometerDevice
from BDPotentiometer.MCP4xxx import MCP4xxx, _coerce_r_ab


class MCP4xx1(MCP4xxx, DigitalPotentiometerDevice):

    def __init__(self, max_value: int = 128, default_value: Union[int, None] = 64, channels: int = 1,
                 r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        MCP4xxx.__init__(self, **spi_args)
        DigitalPotentiometerDevice.__init__(self, max_value=max_value, default_value=default_value, channels=channels,
                                            r_ab=_coerce_r_ab(r_ab), r_w=75, r_lim=r_lim, r_l=r_l,
                                            max_voltage=max_voltage)

    @DigitalPotentiometerDevice.r_w.setter
    def r_w(self, r_w: float) -> None:
        pass


class MCP41x1(MCP4xx1):

    def __init__(self, max_value: int = 128, default_value: Union[int, None] = 64, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP41x1, self).__init__(max_value=max_value, default_value=default_value, channels=1,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)


class MCP4131(MCP41x1):

    def __init__(self, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP4131, self).__init__(max_value=128, default_value=64,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)


class MCP4141(MCP41x1):

    def __init__(self, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP4141, self).__init__(max_value=128, default_value=None,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)


class MCP4151(MCP41x1):

    def __init__(self, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP4151, self).__init__(max_value=256, default_value=128,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)


class MCP4161(MCP41x1):

    def __init__(self, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP4161, self).__init__(max_value=256, default_value=None,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)


class MCP42x1(MCP4xx1):

    def __init__(self, max_value: int = 128, default_value: Union[int, None] = 64, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP42x1, self).__init__(max_value=max_value, default_value=default_value, channels=2,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)


class MCP4231(MCP42x1):

    def __init__(self, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP4231, self).__init__(max_value=128, default_value=64,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)


class MCP4241(MCP42x1):

    def __init__(self, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP4241, self).__init__(max_value=128, default_value=None,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)


class MCP4251(MCP42x1):

    def __init__(self, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP4251, self).__init__(max_value=256, default_value=128,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)


class MCP4261(MCP42x1):

    def __init__(self, r_ab: float = 10e3,
                 r_lim: Union[float, int, list[float], tuple[float]] = 0,
                 r_l: Union[float, int, list[float], tuple[float]] = 1e6,
                 max_voltage: float = 5.0, **spi_args) -> None:
        super(MCP4261, self).__init__(max_value=256, default_value=None,
                                      r_ab=_coerce_r_ab(r_ab), r_lim=r_lim, r_l=r_l,
                                      max_voltage=max_voltage, **spi_args)
