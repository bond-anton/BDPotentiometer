"""Transport protocols and exceptions shared by all bus backends."""

from collections.abc import Sequence
from typing import Protocol, runtime_checkable


class TransportError(OSError):
    """Raised when a bus transaction fails.

    Subclasses `OSError` so callers that already handle gpiozero or spidev I/O
    errors keep catching transport failures without changes.
    """


class TransportClosed(TransportError):
    """Raised when a transaction is attempted after close()."""


@runtime_checkable
class SpiTransport(Protocol):
    """Full-duplex SPI backend.

    Structurally satisfied by any non-class object with callable `transfer`
    and `close` methods. Use `is_spi_transport` for the check: it rejects
    class objects, which `isinstance` against this protocol accepts.
    """

    def transfer(self, tx: Sequence[int]) -> list[int]:
        """Transfer one frame and return the received words."""
        ...

    def close(self) -> None:
        """Release the bus handle."""
        ...


@runtime_checkable
class I2cTransport(Protocol):
    """I2C backend protocol for future chips.

    No implementation or device uses it yet; it keeps the transport surface
    consistent for chips with an I2C interface.
    """

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
    """Check whether `obj` structurally satisfies `SpiTransport`.

    Requires callable `transfer` and `close` attributes and rejects class
    objects, so a transport class itself does not count.
    """
    if isinstance(obj, type):
        return False
    return callable(getattr(obj, "transfer", None)) and callable(
        getattr(obj, "close", None)
    )
