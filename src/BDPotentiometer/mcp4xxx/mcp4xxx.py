""" MCP4XXX series SPI device base class """

from typing import Union
from gpiozero import SPI, SPIDevice

from .. import SpiDigitalWiper, Potentiometer
from ..__helpers import clamp


resistance_list: tuple[float, ...] = (5e3, 10e3, 50e3, 100e3)


def _coerce_max_value(max_value: int) -> int:
    if max_value not in (128, 256):
        raise ValueError("Max value must be equal to 128 or 256.")
    return max_value


def _coerce_r_ab(r_ab: float) -> float:
    """
    Coerce resistance to the closest available for MCP4XXX devices.
    :param r_ab: input resistance (float).
    :return: resistance coerced to one from `resistance_list` (float).
    """
    if r_ab not in resistance_list:
        raise ValueError(f"r_ab must be in {resistance_list}")
    return float(r_ab)


def _check_write_response(data: list) -> None:
    """
    Checks that the write response is in correct format.
    :param data: Response data (list).
    """
    if data is None:
        raise ValueError(f"Wrong response {data}")


def _check_read_response(data: list) -> None:
    """
    Checks that the read response is in correct format.
    :param data: Response data (list).
    """
    if data is None:
        raise ValueError(f"Wrong response {data}")


def _check_status_response(data: list) -> None:
    """
    Checks that the status request response is in correct format.
    :param data: Response data (list).
    """
    reserved = (0b1, 0b11100000)
    if not (
        data[0] & reserved[0] == reserved[0] and data[1] & reserved[1] == reserved[1]
    ):
        raise ValueError(f"Wrong response {data}")


def _check_tcon_response(data: list) -> None:
    """
    Checks that the TCON response is in correct format.
    :param data: Response data (list).
    """
    reserved = (0b1,)
    if not data[0] & reserved[0] == reserved[0]:
        raise ValueError(f"Wrong response {data}")


def _parse_tcon_response(data: int) -> dict[str, bool]:
    """
    Parses TCON response data.
    :param data: raw TCON response data (int).
    ":return: Parsed TCON state (dict).
    """
    result = {
        "shdn": not (data & 0b1000 == 0b1000),
        "A": data & 0b0100 == 0b0100,
        "W": data & 0b0010 == 0b0010,
        "B": data & 0b0001 == 0b0001,
    }
    return result


def _tcon_to_cmd(tcon: dict[str, bool]) -> int:
    """
    Convert TCON dict to TCON cmd ready for sending to device.
    :param tcon: TCON requested state (dict).
    :return: TCON cmd (int).
    """
    shdn = 0 if tcon["shdn"] else 0b1000
    terminal_a = 0b0100 if tcon["A"] else 0
    terminal_w = 0b0010 if tcon["W"] else 0
    terminal_b = 0b0001 if tcon["B"] else 0
    return shdn | terminal_a | terminal_w | terminal_b


_W_CMD = 0b00000000
_R_CMD = 0b00001100
_CH = (0b00000000, 0b00010000)
_STATUS = 0b01010000
_TCON = 0b01000000
_SHDN = 0b10


class MCP4xxxPotentiometer(Potentiometer):
    """Potentiometer to use with MCP4XXX"""

    def __init__(self, r_ab: float, wiper_position: float = 0.5, **kwargs) -> None:
        r_ab = _coerce_r_ab(r_ab)
        super().__init__(r_ab=r_ab, wiper_position=wiper_position, r_w=75, **kwargs)


class MCP4xxxWiper(SpiDigitalWiper):
    """Special version of SPIDigitalWiper for MCP4XXX pots"""

    def __init__(
        self,
        potentiometer: MCP4xxxPotentiometer,
        spi: Union[SPI, None] = None,
        max_value: int = 128,
        invert: bool = False,
        **kwargs,
    ):
        max_value = _coerce_max_value(max_value)
        super().__init__(
            potentiometer=potentiometer,
            spi=spi,
            max_value=max_value,
            invert=invert,
            **kwargs,
        )

    def _set_value(self, value: int) -> int:
        if isinstance(self.spi, SPI):
            value = int(round(clamp(value, 0, self.max_value)))
            value = self.max_value - value if self.invert else value
            self.logger.debug("Setting value to %d", value)
            data = self.spi.transfer([_W_CMD | _CH[self.channel], value])
            _check_write_response(data)
            self.potentiometer.wiper_position = value / self.max_value
            return value
        raise ConnectionError("SPI interface not set")

    def _read_value(self):
        if isinstance(self.spi, SPI):
            data = self.spi.transfer([_R_CMD | _CH[self.channel], 0])
            _check_read_response(data)
            return data[1]
        raise ConnectionError("SPI interface not set")


class MCP4xxx(SPIDevice):
    """Base class for MCP4XXX series devices"""

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

    def write_tcon(
        self,
        ch0: Union[dict[str, bool], None] = None,
        ch1: Union[dict[str, bool], None] = None,
    ) -> bool:
        """
        MCP4XXX terminals connection (TCON) control.

        :return: True if success, otherwise False.
        """
        default_tcon_value = {"shdn": False, "A": True, "W": True, "B": True}
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
        return self.write_tcon(
            ch0={"shdn": ch0, "A": True, "W": True, "B": True},
            ch1={"shdn": ch1, "A": True, "W": True, "B": True},
        )
