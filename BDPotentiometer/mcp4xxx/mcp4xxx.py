""" MCP4XXX series SPI device base class """

from typing import Union
from gpiozero import SPI, SPIDevice

from BDPotentiometer import SpiDigitalWinder, Potentiometer


def _coerce_r_ab(r_ab: float) -> float:
    if r_ab in (5e3, 10e3, 50e3, 100e3):
        return float(r_ab)
    if r_ab < 7.5e3:
        return 5.e3
    if r_ab < 30.e3:
        return 10.e3
    if r_ab < 75.e3:
        return 50.e3
    return 100.e3


def _check_write_response(data: list) -> None:
    if data is None:
        raise ValueError(f'Wrong response {data}')


def _check_read_response(data: list) -> None:
    if data is None:
        raise ValueError(f'Wrong response {data}')


def _check_status_response(data: list) -> None:
    reserved = (0b1, 0b11100000)
    if not (data[0] & reserved[0] == reserved[0] and data[1] & reserved[1] == reserved[1]):
        raise ValueError(f'Wrong response {data}')


def _check_tcon_response(data: list) -> None:
    reserved = (0b1,)
    if not data[0] & reserved[0] == reserved[0]:
        raise ValueError(f'Wrong response {data}')


def _parse_tcon_response(data: int) -> dict[str, bool]:
    result = {
        'shdn': not (data & 0b1000 == 0b1000),
        'A': data & 0b0100 == 0b0100,
        'W': data & 0b0010 == 0b0010,
        'B': data & 0b0001 == 0b0001,
    }
    return result


def _tcon_to_cmd(tcon: dict[str, bool]) -> int:
    shdn = 0 if tcon['shdn'] else 0b1000
    terminal_a = 0b0100 if tcon['A'] else 0
    terminal_w = 0b0010 if tcon['W'] else 0
    terminal_b = 0b0001 if tcon['B'] else 0
    return shdn | terminal_a | terminal_w | terminal_b


_W_CMD = 0b00000000
_R_CMD = 0b00001100
_CH = (0b00000000, 0b00010000)
_STATUS = 0b01010000
_TCON = 0b01000000
_SHDN = 0b10


class MCP4xxxPotentiometer(Potentiometer):
    """ Potentiometer to use with MCP4XXX """

    def __init__(self, r_ab: float, rheostat: bool = False) -> None:
        r_ab = _coerce_r_ab(r_ab)
        super().__init__(r_ab=r_ab, r_w=75, rheostat=rheostat, locked=True)


class MCP4xxxWinder(SpiDigitalWinder):
    """ Special version of SPIDigitalWinder for MCP4XXX pots """

    def __init__(self, potentiometer: MCP4xxxPotentiometer, spi: Union[SPI, None] = None,
                 max_value: int = 128):
        assert max_value in (128, 256)
        super().__init__(potentiometer=potentiometer, spi=spi, max_value=max_value,
                         parameters_locked=True)

    def _set_value(self, value: int) -> int:
        if isinstance(self.spi, SPI):
            data = self.spi.transfer([_W_CMD | _CH[self.channel], value])
            _check_write_response(data)
            return value
        raise ConnectionError('SPI interface not set')

    def _read_value(self):
        if isinstance(self.spi, SPI):
            data = self.spi.transfer([_R_CMD | _CH[self.channel], 0])
            _check_read_response(data)
            return data[1]
        raise ConnectionError('SPI interface not set')


class MCP4xxx(SPIDevice):
    """ Base class for MCP4XXX series devices """

    def __init__(self, **spi_args) -> None:
        super().__init__(shared=True, **spi_args)

    @property
    def value(self):
        raise NotImplementedError

    def get_shdn_pin_status(self) -> bool:
        """
        Check status of device SHDN pin.

        :return: SHDN state (bool).
        """
        data = self._spi.transfer([_R_CMD | _STATUS, 0])
        _check_status_response(data)
        if data[1] & _SHDN == _SHDN:
            return True
        return False

    def read_tcon(self) -> tuple[dict[str, bool], dict[str, bool]]:
        """
        Read terminals connection (TCON) status of the device.

        :return: Tuple of TCON status dicts.
        """
        data = self._spi.transfer([_R_CMD | _TCON, 0])
        _check_tcon_response(data)
        ch0 = data[1] & 0b1111
        ch1 = (data[1] & 0b11110000) >> 4
        return _parse_tcon_response(ch0), _parse_tcon_response(ch1)

    def write_tcon(self,
                   ch0: Union[dict[str, bool], None] = None,
                   ch1: Union[dict[str, bool], None] = None) -> bool:
        """
        MCP4XXX terminals connection (TCON) control.

        :return: True if success, otherwise False.
        """
        default_tcon_value = {'shdn': False, 'A': True, 'W': True, 'B': True}
        if ch0 is None:
            ch0 = default_tcon_value
        if ch1 is None:
            ch1 = default_tcon_value
        ch0_cmd = _tcon_to_cmd(ch0)
        ch1_cmd = _tcon_to_cmd(ch1)
        data = ch0_cmd | (ch1_cmd << 4)
        _ = self._spi.transfer([_W_CMD | _TCON, data])
        resp = self._spi.transfer([_R_CMD | _TCON, 0])
        _check_tcon_response(resp)
        if resp[1] == data:
            return True
        return False

    def shdn(self, ch0: bool = False, ch1: bool = False) -> bool:
        """
        Shutdown of device channels using TCON control.
        :param ch0: Boolean True for SHDN.
        :param ch1: Boolean True for SHDN.
        :return: True if success, otherwise False.
        """
        return self.write_tcon(ch0={'shdn': ch0, 'A': True, 'W': True, 'B': True},
                               ch1={'shdn': ch1, 'A': True, 'W': True, 'B': True})
