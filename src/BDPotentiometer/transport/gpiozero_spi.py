"""SPI transport backed by gpiozero's hardware SPI device."""

from collections.abc import Sequence
from typing import Any

from gpiozero import SPIDevice

from .base import TransportClosed, TransportError


class _GpiozeroSpiHandle(SPIDevice):
    """Private SPIDevice used only to obtain a shared gpiozero SPI object."""

    def __init__(self, **spi_args) -> None:
        super().__init__(shared=True, **spi_args)

    @property
    def raw(self) -> Any:
        """Return the gpiozero SPI object held by the device."""
        return self._spi

    @property
    def value(self):
        """A raw SPI handle exposes no digital value."""
        raise NotImplementedError


class GpiozeroSpiTransport:
    """SPI transport over a gpiozero SPI interface.

    With no `spi` argument the transport builds a private gpiozero
    `SPIDevice` from the same keyword arguments the legacy `MCP4xxx`
    constructor accepted (`channel`, `port`, `device`, `clock_pin`,
    `mosi_pin`, `miso_pin`, `select_pin`). `shared=True` is kept so that
    several devices can share one hardware SPI port.
    """

    _SPI_ARGS = (
        "channel",
        "port",
        "device",
        "clock_pin",
        "mosi_pin",
        "miso_pin",
        "select_pin",
    )

    def __init__(self, spi: Any = None, **spi_args) -> None:
        self._closed = False
        self._handle = None
        if spi is None:
            self._handle = _GpiozeroSpiHandle(**spi_args)
            self._raw = self._handle.raw
        else:
            self._raw = spi

    @property
    def raw(self) -> Any:
        """Return the underlying gpiozero SPI object."""
        return self._raw

    @property
    def closed(self) -> bool:
        """Return True once close() has run."""
        return self._closed

    def transfer(self, tx: Sequence[int]) -> list[int]:
        """Transfer one frame and validate the response length."""
        if self._closed:
            raise TransportClosed("GpiozeroSpiTransport is closed")
        frame = list(tx)
        rx = list(self._raw.transfer(frame))
        if len(rx) != len(frame):
            raise TransportError(
                f"gpiozero returned {len(rx)} words for a {len(frame)}-word request"
            )
        return rx

    def close(self) -> None:
        """Close the SPI handle. Repeated calls have no effect."""
        if self._closed:
            return
        self._closed = True
        if self._handle is not None:
            self._handle.close()
        else:
            self._raw.close()
