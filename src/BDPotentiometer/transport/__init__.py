"""Bus transport backends for BDPotentiometer devices."""

from typing import TYPE_CHECKING, Any

from .base import (
    I2cTransport,
    SpiTransport,
    TransportClosed,
    TransportError,
    is_spi_transport,
)
from .fake import FakeSpiTransport
from .selection import (
    GPIOZERO_PIN_ARGS,  # noqa: F401 - re-exported for callers
    GPIOZERO_SPI_ARGS,  # noqa: F401 - re-exported for callers
    build_default_transport,  # noqa: F401 - re-exported for callers
)
from .spidev_spi import SpiDevTransport

if TYPE_CHECKING:
    from .gpiozero_spi import GpiozeroSpiTransport

__all__ = [
    "FakeSpiTransport",
    "GpiozeroSpiTransport",
    "I2cTransport",
    "SpiDevTransport",
    "SpiTransport",
    "TransportClosed",
    "TransportError",
    "is_spi_transport",
]


def __getattr__(name: str) -> Any:
    """Resolve the optional gpiozero transport on first access."""
    if name == "GpiozeroSpiTransport":
        try:
            from .gpiozero_spi import GpiozeroSpiTransport  # noqa: PLC0415
        except ImportError as exc:
            raise AttributeError(
                "GpiozeroSpiTransport requires the optional 'gpiozero' package. "
                "Install it with: pip install 'BDPotentiometer[gpiozero]'"
            ) from exc

        return GpiozeroSpiTransport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """List the module attributes, including lazily resolved names."""
    return sorted(set(__all__) | set(globals()))
