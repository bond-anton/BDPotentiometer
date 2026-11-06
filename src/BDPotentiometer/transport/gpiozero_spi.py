"""SPI transport backed by gpiozero's hardware SPI device."""

from collections.abc import Sequence
from typing import Any

from gpiozero import SPIDevice
from gpiozero.exc import DeviceClosed

from ..__gpiozero_helpers import fix_gpiozero_dual_cs_spi
from .base import TransportClosed, TransportError
from .selection import GPIOZERO_SPI_ARGS


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
    constructor accepted (`port`, `device`, `clock_pin`, `mosi_pin`,
    `miso_pin`, `select_pin`). `shared=True` is kept so that several
    devices can share one hardware SPI port.

    Ownership follows construction: a transport that built its own handle
    closes it. A transport wrapping a caller-supplied `spi=` never closes it
    and does not join gpiozero's shared reference count, so the supplied
    handle's owner must outlive the wrapper. Once the owner closes the handle,
    this transport's transfers raise `TransportClosed`.
    """

    _SPI_ARGS = GPIOZERO_SPI_ARGS

    def __init__(self, spi: Any = None, **spi_args) -> None:
        """
        Wrap an existing gpiozero SPI object or build a shared one.

        :param spi: Existing gpiozero SPI object to wrap. The caller keeps
            ownership and must keep it open for the lifetime of this transport;
            when None a private `SPIDevice` is built from `spi_args` and owned
            by this transport.
        :param spi_args: gpiozero `SPIDevice` keywords (`port`, `device`,
            `clock_pin`, `mosi_pin`, `miso_pin`, `select_pin`).
        """
        self._closed = False
        self._owns_raw = spi is None
        self._handle = None
        if spi is None:
            fix_gpiozero_dual_cs_spi()
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
        """Return True once close() has completed successfully."""
        return self._closed

    def transfer(self, tx: Sequence[int]) -> list[int]:
        """Transfer one frame and validate the response length.

        :param tx: Request frame.
        :return: Response frame of the same length.
        :raises TransportClosed: If this transport is closed or the owner of a
            caller-supplied SPI handle has closed it.
        :raises TransportError: If gpiozero returns the wrong number of words.
        """
        if self._closed:
            raise TransportClosed("GpiozeroSpiTransport is closed")
        raw_closed = getattr(self._raw, "closed", False)
        if isinstance(raw_closed, bool) and raw_closed:
            raise TransportClosed(
                "The underlying gpiozero SPI handle is closed; its owner must "
                "outlive this wrapper"
            )
        frame = list(tx)
        try:
            rx = list(self._raw.transfer(frame))
        except DeviceClosed as exc:
            raise TransportClosed(
                "The underlying gpiozero SPI handle was closed by its owner"
            ) from exc
        if len(rx) != len(frame):
            raise TransportError(
                f"gpiozero returned {len(rx)} words for a {len(frame)}-word request"
            )
        return rx

    def close(self) -> None:
        """Close an owned SPI handle.

        A wrapper around a caller-supplied handle only marks itself closed and
        leaves that handle untouched; its owner must close it. Repeated calls
        after a successful close have no effect; a failed close of an owned
        handle leaves the transport open and retryable.
        """
        if self._closed:
            return
        if self._owns_raw and self._handle is not None:
            self._handle.close()
        self._closed = True
