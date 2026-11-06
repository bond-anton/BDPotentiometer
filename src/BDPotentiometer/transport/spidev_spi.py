"""SPI transport backed by the Linux spidev device interface."""

from collections.abc import Sequence
from typing import Any

from .base import TransportClosed, TransportError


def _load_spidev():
    """Import and return spidev.SpiDev, raising an actionable error if missing."""
    try:
        # Imported lazily so the core install needs no spidev package.
        from spidev import SpiDev  # noqa: PLC0415 - kept lazy so spidev stays optional
    except ImportError as exc:
        raise ImportError(
            "SpiDevTransport requires the optional 'spidev' package. "
            "Install it with: pip install 'BDPotentiometer[spi]'"
        ) from exc
    return SpiDev


class SpiDevTransport:
    """SPI transport over /dev/spidev<bus>.<device>.

    Linux only. Requires kernel SPI (`dtparam=spi=on` in
    /boot/firmware/config.txt, or the older /boot/config.txt), the device
    node to exist, and read access for the current user (member of the
    `spi` group, or root).

    Transfers use `xfer2`, which keeps CS asserted for the whole frame;
    `xfer` would deassert CS between 8-bit words and break the 16-bit
    MCP4xxx command+data words.
    """

    # One argument per spidev setting; the tuning surface is deliberately explicit.
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        bus: int = 0,
        device: int = 0,
        max_speed_hz: int = 500_000,
        mode: int = 0,
        bits_per_word: int = 8,
        lsbfirst: bool = False,
    ) -> None:
        spidev = _load_spidev()
        self._spi = spidev()
        self._closed = False
        try:
            self._spi.open(bus, device)
        except OSError as exc:
            raise TransportError(
                f"Failed to open /dev/spidev{bus}.{device}: {exc}. "
                "Ensure SPI is enabled (dtparam=spi=on) and that the current "
                "user is in the 'spi' group."
            ) from exc
        self._spi.max_speed_hz = max_speed_hz
        self._spi.mode = mode
        self._spi.bits_per_word = bits_per_word
        self._spi.lsbfirst = lsbfirst
        self._spi.cshigh = False

    @property
    def raw(self) -> Any:
        """Return the underlying spidev.SpiDev object."""
        return self._spi

    @property
    def closed(self) -> bool:
        """Return True once close() has run."""
        return self._closed

    def transfer(self, tx: Sequence[int]) -> list[int]:
        """Transfer one frame with CS held asserted for its full length."""
        if self._closed:
            raise TransportClosed("SpiDevTransport is closed")
        frame = list(tx)
        rx = list(self._spi.xfer2(frame))
        if len(rx) != len(frame):
            raise TransportError(
                f"spidev returned {len(rx)} words for a {len(frame)}-word request"
            )
        return rx

    def close(self) -> None:
        """Close the device handle. Repeated calls have no effect."""
        if self._closed:
            return
        self._closed = True
        self._spi.close()
