""" MCP4XXX series SPI device base class """

from typing import Union
from gpiozero import SPIDevice


def _coerce_r_ab(r_ab: float) -> float:
    if r_ab in (5e3, 10e3, 50e3, 100e3):
        return float(r_ab)
    if r_ab < 7.5e3:
        return 5.e3
    if r_ab < 30.e3:
        return 10.e3
    if r_ab < 75.e3:
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
        raise ValueError('Wrong response %s' % data)


def _check_tcon_response(data: list) -> None:
    reserved = (0b1,)
    if not data[0] & reserved[0] == reserved[0]:
        raise ValueError('Wrong response %s' % data)


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
    a = 0b0100 if tcon['A'] else 0
    w = 0b0010 if tcon['W'] else 0
    b = 0b0001 if tcon['B'] else 0
    return shdn | a | w | b


_w_cmd = 0b00000000
_r_cmd = 0b00001100
_ch = (0b00000000, 0b00010000)
_status = 0b01010000
_tcon = 0b01000000
_shdn = 0b10


class MCP4xxx(SPIDevice):

    def __init__(self, **spi_args) -> None:
        super(MCP4xxx, self).__init__(shared=True, **spi_args)

    @property
    def value(self) -> tuple[int]:
        return tuple(self._values)

    @value.setter
    def value(self, v: Union[list[int], tuple[int]]) -> None:
        for i in range(len(self.channels)):
            ch = self.channels[i]
            value = self._coerce_value(v[i])
            data = self._set_value(ch, value)
            self._values[ch] = data

    def _set_value(self, ch, value):
        data = self._spi.transfer([_w_cmd | _ch[ch], value])
        _check_write_response(data)
        return value

    def _read_value(self, ch):
        data = self._spi.transfer([_r_cmd | _ch[ch], 0])
        _check_read_response(data)
        return data[1]

    def get_shdn_pin_status(self):
        data = self._spi.transfer([_r_cmd | _status, 0])
        _check_status_response(data)
        if data[1] & _shdn == _shdn:
            return True
        return False

    def read_tcon(self):
        data = self._spi.transfer([_r_cmd | _tcon, 0])
        _check_tcon_response(data)
        ch0 = data[1] & 0b1111
        ch1 = (data[1] & 0b11110000) >> 4
        return _parse_tcon_response(ch0), _parse_tcon_response(ch1)

    def write_tcon(self, ch0=None, ch1=None):
        default_tcon_value = {'shdn': False, 'A': True, 'W': True, 'B': True}
        if ch0 is None:
            ch0 = default_tcon_value
        if ch1 is None:
            ch1 = default_tcon_value
        ch0_cmd = _tcon_to_cmd(ch0)
        ch1_cmd = _tcon_to_cmd(ch1)
        data = ch0_cmd | (ch1_cmd << 4)
        _ = self._spi.transfer([_w_cmd | _tcon, data])
        resp = self._spi.transfer([_r_cmd | _tcon, 0])
        _check_tcon_response(resp)
        if resp[1] == data:
            return True
        return False

    def shdn(self, ch0=False, ch1=False):
        return self.write_tcon(ch0={'shdn': ch0, 'A': True, 'W': True, 'B': True},
                               ch1={'shdn': ch1, 'A': True, 'W': True, 'B': True})
