"""Transport protocols and exceptions shared by all bus backends."""

from collections.abc import Sequence
from typing import Protocol, runtime_checkable


class TransportError(OSError):
    """Raised when a bus transaction fails."""


class TransportClosed(TransportError):
    """Raised when a transaction is attempted after close()."""


@runtime_checkable
class SpiTransport(Protocol):
    """Full-duplex SPI backend."""

    def transfer(self, tx: Sequence[int]) -> list[int]:
        """Transfer one frame and return the received words."""
        ...

    def close(self) -> None:
        """Release the bus handle."""
        ...


@runtime_checkable
class I2cTransport(Protocol):
    """I2C backend for future chips."""

    def write(self, data: Sequence[int]) -> None:
        """Write one frame."""
        ...

    def read(self, nbytes: int) -> bytes:
        """Read `nbytes` bytes."""
        ...

    def write_read(self, tx: Sequence[int], nbytes: int) -> bytes:
        """Write a frame, then read `nbytes` bytes."""
        ...

    def close(self) -> None:
        """Release the bus handle."""
        ...


def is_spi_transport(obj: object) -> bool:
    """Structural check: object can transfer and release an SPI bus."""
    if isinstance(obj, type):
        return False
    return callable(getattr(obj, "transfer", None)) and callable(
        getattr(obj, "close", None)
    )
