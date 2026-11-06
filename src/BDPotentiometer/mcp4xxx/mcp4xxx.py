"""MCP4XXX series SPI device base class"""

from typing import Any, Union

from .. import Potentiometer, SpiDigitalWiper
from ..__helpers import check_integer, clamp
from ..transport.base import SpiTransport, is_spi_transport
from ..transport.gpiozero_spi import GpiozeroSpiTransport

#: Supported `r_ab` values in ohms for MCP4XXX devices.
resistance_list: tuple[float, ...] = (5e3, 10e3, 50e3, 100e3)


def _coerce_max_value(max_value: int) -> int:
    """
    Validate the full-scale divisor of an MCP4XXX wiper.

    :param max_value: Full-scale divisor, either 128 or 256 (int).
    :return: The validated divisor as int.
    :raises TypeError: If `max_value` is not a real number.
    :raises ValueError: If `max_value` is not 128 or 256.
    """
    max_value = check_integer(max_value)
    if max_value not in (128, 256):
        raise ValueError("Max value must be equal to 128 or 256.")
    return max_value


def _coerce_r_ab(r_ab: float) -> float:
    """
    Validate `r_ab` against the resistances supported by MCP4XXX devices.

    :param r_ab: Input resistance in ohms (float).
    :return: The validated resistance as float.
    :raises ValueError: If `r_ab` is not in `resistance_list`.
    """
    if r_ab not in resistance_list:
        raise ValueError(f"r_ab must be in {resistance_list}")
    return float(r_ab)


def _check_write_response(data: list) -> None:
    """
    Reject a missing write response.

    Only ``None`` is rejected; the returned words are not inspected here.

    :param data: Response data (list or None).
    :raises ValueError: If `data` is None.
    """
    if data is None:
        raise ValueError(f"Wrong response {data}")


def _check_read_response(data: list) -> None:
    """
    Reject a missing or truncated read response.

    The returned words are not inspected here; only the frame length is
    validated.

    :param data: Response data (list or None).
    :raises ValueError: If `data` is None or shorter than two words.
    """
    if data is None or len(data) < 2:
        raise ValueError(f"Wrong response {data}")


def _check_status_response(data: list) -> None:
    """
    Validate the reserved bits of a status response.

    :param data: Response data (list).
    :raises ValueError: If the frame is shorter than two words or the reserved
        bits are not set.
    """
    if data is None or len(data) < 2:
        raise ValueError(f"Wrong response {data}")
    reserved = (0b1, 0b11100000)
    if not (
        data[0] & reserved[0] == reserved[0] and data[1] & reserved[1] == reserved[1]
    ):
        raise ValueError(f"Wrong response {data}")


def _check_tcon_response(data: list) -> None:
    """
    Validate the reserved bit of a TCON response.

    :param data: Response data (list). Both words are required even though
        only the first carries the reserved bit.
    :raises ValueError: If the frame is shorter than two words or the reserved
        bit is not set.
    """
    if data is None or len(data) < 2:
        raise ValueError(f"Wrong response {data}")
    reserved = (0b1,)
    if not data[0] & reserved[0] == reserved[0]:
        raise ValueError(f"Wrong response {data}")


def _parse_tcon_response(data: int) -> dict[str, bool]:
    """
    Parse one TCON nibble into named terminal states.

    :param data: Raw TCON nibble (int).
    :return: Parsed TCON state with keys ``shdn``, ``A``, ``W``, and ``B`` (dict).
    """
    result = {
        "shdn": data & 0b1000 != 0b1000,
        "A": data & 0b0100 == 0b0100,
        "W": data & 0b0010 == 0b0010,
        "B": data & 0b0001 == 0b0001,
    }
    return result


def _tcon_to_cmd(tcon: dict[str, bool]) -> int:
    """
    Convert a TCON state dict into the TCON command nibble.

    :param tcon: Requested TCON state (dict).
    :return: TCON command nibble (int).
    """
    shdn = 0 if tcon["shdn"] else 0b1000
    terminal_a = 0b0100 if tcon["A"] else 0
    terminal_w = 0b0010 if tcon["W"] else 0
    terminal_b = 0b0001 if tcon["B"] else 0
    return shdn | terminal_a | terminal_w | terminal_b


_W_CMD = 0b00000000  # Write command bits (C1:C0 = 00).
_R_CMD = 0b00001100  # Read command bits (C1:C0 = 11).
_CH = (0b00000000, 0b00010000)  # Register address bit AD0 for channel 0 and 1.
_STATUS = 0b01010000  # Status register address (0x5) in a read command.
_TCON = 0b01000000  # TCON register address (0x4) in a read or write command.
_SHDN = 0b10  # Status register bit 1: SHDN pin state.


def _encode_wiper_write(channel: int, value: int) -> list[int]:
    """
    Encode a wiper position write command.

    :param channel: channel number, either 0 or 1 (int).
    :param value: wiper position value (int).
    :return: Command frame ready for transfer (list).
    :raises ValueError: If `channel` is not 0 or 1, or `value` is outside the
        0..255 register range.
    """
    if channel not in (0, 1):
        raise ValueError(f"Channel must be 0 or 1, got {channel}")
    if not 0 <= value <= 0xFF:
        raise ValueError(f"Wiper value must be in the range 0..255, got {value}")
    return [_W_CMD | _CH[channel], value]


def _encode_wiper_read(channel: int) -> list[int]:
    """
    Encode a wiper position read command.

    :param channel: channel number, either 0 or 1 (int).
    :return: Command frame ready for transfer (list).
    :raises ValueError: If `channel` is not 0 or 1.
    """
    if channel not in (0, 1):
        raise ValueError(f"Channel must be 0 or 1, got {channel}")
    return [_R_CMD | _CH[channel], 0]


def _decode_wiper_read(data: list) -> int:
    """
    Decode a wiper position read response.

    :param data: Response data (list).
    :return: Wiper position value (int).
    :raises ValueError: If `data` is None or shorter than two words.
    """
    _check_read_response(data)
    return data[1]


class MCP4xxxPotentiometer(Potentiometer):
    """Potentiometer model for one MCP4XXX channel.

    The wiper resistance `r_w` is fixed at 75 ohm, the value passed to the
    `Potentiometer` base constructor.
    """

    def __init__(self, r_ab: float, wiper_position: float = 0.5, **kwargs) -> None:
        """
        Build the potentiometer model for one channel.

        :param r_ab: Total resistance in ohms; must be in `resistance_list`.
        :param wiper_position: Initial wiper position in the range 0..1 (float).
        :param kwargs: Extra keywords forwarded to `Potentiometer`; `r_w` is
            supplied as 75 ohm by this constructor.
        :raises ValueError: If `r_ab` is not in `resistance_list`.
        """
        r_ab = _coerce_r_ab(r_ab)
        super().__init__(r_ab=r_ab, wiper_position=wiper_position, r_w=75, **kwargs)


class MCP4xxxWiper(SpiDigitalWiper):
    """SPI wiper for one MCP4XXX channel.

    Values are clamped to ``0..max_code``. 8-bit parts expose `max_value` 256
    as the full-scale divisor while the wiper register holds codes 0..255.
    A failed write restores the previous wiper position before re-raising.
    """

    def __init__(
        self,
        potentiometer: MCP4xxxPotentiometer,
        spi: Union[SpiTransport, None] = None,
        max_value: int = 128,
        invert: bool = False,
        transport: Union[SpiTransport, None] = None,
        **kwargs,
    ):
        """
        Build the SPI wiper for one channel.

        Unlike `SpiDigitalWiper`, this bus-backed subclass reads the device
        during construction, so it requires a `transport` or `spi` up front.

        :param potentiometer: Potentiometer model driven by this wiper.
        :param spi: Legacy alias for `transport`, used only when `transport`
            is None.
        :param max_value: Full-scale divisor, either 128 or 256.
        :param invert: Map code 0 to `max_code` and vice versa when True.
        :param transport: Canonical SPI transport for the wiper.
        :param kwargs: Extra keywords forwarded to `SpiDigitalWiper`
            (`label`, `log_level`).
        :raises ValueError: If `max_value` is not 128 or 256, or if neither
            `transport` nor `spi` is supplied.
        """
        max_value = _coerce_max_value(max_value)
        if transport is None and spi is None:
            raise ValueError("MCP4xxxWiper requires a transport or spi")
        super().__init__(
            potentiometer=potentiometer,
            spi=spi,
            max_value=max_value,
            invert=invert,
            transport=transport,
            **kwargs,
        )

    @property
    def max_code(self) -> int:
        """
        Highest wiper code accepted by the device.

        8-bit parts use `max_value` 256 as the full-scale divisor while the
        wiper register holds codes 0..255.

        :return: Highest wiper code as int.
        """
        return min(self.max_value, 0xFF)

    def _set_value(self, value: int) -> int:
        value = int(round(clamp(value, 0, self.max_code)))
        value = self.max_code - value if self.invert else value
        self.logger.debug("Setting value to %d", value)
        previous_position = self.potentiometer.wiper_position
        try:
            data = self._require_transport().transfer(
                _encode_wiper_write(self.channel, value)
            )
            _check_write_response(data)
            self.potentiometer.wiper_position = value / self.max_value
        except Exception:
            self.potentiometer.wiper_position = previous_position
            raise
        return value

    def _read_value(self):
        data = self._require_transport().transfer(_encode_wiper_read(self.channel))
        return _decode_wiper_read(data)


class MCP4xxx:
    """Base class for MCP4XXX series devices.

    The device is no longer a ``gpiozero.SPIDevice``. ``transport=`` is the
    canonical way to inject an SPI backend; ``spi=`` is a legacy alias used
    only when ``transport`` is None.

    Compatibility surface: ``.transport`` returns the injected transport,
    ``.spi`` returns the raw gpiozero SPI object when the transport wraps one
    and the transport itself otherwise, ``.close()`` closes the transport, and
    ``.closed`` is True after ``close()`` has run, when the transport reports
    itself closed, or when there is no transport.
    """

    _SPI_ARGS = GpiozeroSpiTransport._SPI_ARGS

    def __init__(  # noqa: PLR0913
        self,
        transport: Union[SpiTransport, None] = None,
        spi: Union[SpiTransport, None] = None,
        *,
        port: Any = None,
        device: Any = None,
        clock_pin: Any = None,
        mosi_pin: Any = None,
        miso_pin: Any = None,
        select_pin: Any = None,
    ) -> None:
        """
        Build the device from an SPI transport or from gpiozero pin settings.

        When neither `transport` nor `spi` is supplied, the keyword-only pin
        settings build a `GpiozeroSpiTransport`.

        :param transport: Canonical SPI transport to use (SpiTransport).
        :param spi: Legacy alias for `transport`, used only when `transport`
            is None.
        :param port: gpiozero SPI port number.
        :param device: gpiozero SPI device number.
        :param clock_pin: GPIO pin used as SPI clock.
        :param mosi_pin: GPIO pin used as SPI MOSI.
        :param miso_pin: GPIO pin used as SPI MISO.
        :param select_pin: GPIO pin used as SPI chip select.
        :raises TypeError: If the supplied transport lacks transfer() or close().
        """
        if transport is None and spi is not None:
            transport = spi
        if transport is None:
            provided_spi_args = {
                "port": port,
                "device": device,
                "clock_pin": clock_pin,
                "mosi_pin": mosi_pin,
                "miso_pin": miso_pin,
                "select_pin": select_pin,
            }
            spi_args = {
                name: provided_spi_args[name]
                for name in self._SPI_ARGS
                if provided_spi_args[name] is not None
            }
            transport = GpiozeroSpiTransport(**spi_args)
        if transport is not None and not is_spi_transport(transport):
            raise TypeError(
                "Expected an SPI transport with transfer() and close(), "
                f"got {type(transport)}"
            )
        self._transport: Union[SpiTransport, None] = transport
        self._closed = False

    @property
    def transport(self) -> Union[SpiTransport, None]:
        """SPI transport used by the device."""
        return self._transport

    @property
    def spi(self):
        """Backward-compatible accessor: raw gpiozero SPI if wrapped."""
        if self._transport is None:
            return None
        return getattr(self._transport, "raw", self._transport)

    @property
    def closed(self) -> bool:
        """
        True when the device has no transport, `close()` has run, or the
        transport reports itself closed.
        """
        if self._transport is None:
            return True
        return self._closed or bool(getattr(self._transport, "closed", False))

    def close(self) -> None:
        """Close the underlying transport and mark the device closed."""
        if self._transport is not None:
            self._transport.close()
            self._closed = True

    def _require_transport(self) -> SpiTransport:
        """Return the transport, raising if the device has none."""
        if self._transport is None:
            raise ConnectionError("SPI interface not set")
        return self._transport

    @property
    def value(self):
        """Value is provided by the concrete device classes."""
        raise NotImplementedError

    def get_shdn_pin_status(self) -> bool:
        """
        Read the SHDN pin state reported by the status register.

        This reads the hardware SHDN pin bit, not the TCON shutdown bit used
        by `shdn()`.

        :return: True when the status-register SHDN bit is set, otherwise False.
        :raises ValueError: If the status response has invalid reserved bits.
        :raises ConnectionError: If the device has no transport.
        """
        data = self._require_transport().transfer([_R_CMD | _STATUS, 0])
        _check_status_response(data)
        return data[1] & _SHDN == _SHDN

    def read_tcon(self) -> tuple[dict[str, bool], dict[str, bool]]:
        """
        Read the terminal connection (TCON) state of both channels.

        Each dict has keys ``shdn``, ``A``, ``W``, and ``B``. For ``A``, ``W``,
        and ``B``, True means the terminal is connected. For ``shdn``, True
        means the channel is in shutdown. Index 0 of the returned tuple is
        channel 0, index 1 is channel 1; single-channel parts still report a
        second dict.

        :return: Tuple of TCON state dicts, ``(channel 0, channel 1)``.
        :raises ValueError: If the response lacks the reserved bit.
        :raises ConnectionError: If the device has no transport.
        """
        data = self._require_transport().transfer([_R_CMD | _TCON, 0])
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
        Write the terminal connection (TCON) state of both channels.

        A channel left as ``None`` keeps all terminals connected with shutdown
        deasserted, equivalent to ``{"shdn": False, "A": True, "W": True,
        "B": True}``.

        :param ch0: Channel 0 state with keys ``shdn``, ``A``, ``W``, and ``B``.
            For ``A``, ``W``, and ``B``, True connects the terminal. For
            ``shdn``, True puts the channel in shutdown.
        :param ch1: Channel 1 state, with the same keys and meaning as `ch0`.
        :return: True if the read-back matches the written value, otherwise False.
        :raises ValueError: If the read-back response lacks the reserved bit.
        :raises ConnectionError: If the device has no transport.
        """
        default_tcon_value = {"shdn": False, "A": True, "W": True, "B": True}
        if ch0 is None:
            ch0 = default_tcon_value
        if ch1 is None:
            ch1 = default_tcon_value
        ch0_cmd = _tcon_to_cmd(ch0)
        ch1_cmd = _tcon_to_cmd(ch1)
        data = ch0_cmd | (ch1_cmd << 4)
        _ = self._require_transport().transfer([_W_CMD | _TCON, data])
        resp = self._require_transport().transfer([_R_CMD | _TCON, 0])
        _check_tcon_response(resp)
        return resp[1] == data

    def shdn(self, ch0: bool = False, ch1: bool = False) -> bool:
        """
        Put selected channels into shutdown through the TCON register.

        :param ch0: True puts channel 0 into shutdown; False leaves it on.
        :param ch1: True puts channel 1 into shutdown; False leaves it on.
        :return: True if the read-back matches the written value, otherwise False.
        :raises ValueError: If the read-back response lacks the reserved bit.
        :raises ConnectionError: If the device has no transport.
        """
        return self.write_tcon(
            ch0={"shdn": ch0, "A": True, "W": True, "B": True},
            ch1={"shdn": ch1, "A": True, "W": True, "B": True},
        )
