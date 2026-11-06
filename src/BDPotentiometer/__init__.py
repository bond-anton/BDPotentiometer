"""Digital potentiometer and wiper models with pluggable bus transports."""

__version__ = "0.2.0"


from typing import TYPE_CHECKING, Any

from .__gpiozero_helpers import fix_gpiozero_dual_cs_spi
from .digital_potentiometer import DigitalPotentiometerDevice
from .digital_wiper import DigitalWiper, SpiDigitalWiper
from .potentiometer import Potentiometer
from .transport import (
    FakeSpiTransport,
    I2cTransport,
    SpiDevTransport,
    SpiTransport,
    TransportClosed,
    TransportError,
    is_spi_transport,
)

if TYPE_CHECKING:
    from .transport import GpiozeroSpiTransport

__all__ = [
    "DigitalPotentiometerDevice",
    "DigitalWiper",
    "FakeSpiTransport",
    "GpiozeroSpiTransport",
    "I2cTransport",
    "Potentiometer",
    "SpiDevTransport",
    "SpiDigitalWiper",
    "SpiTransport",
    "TransportClosed",
    "TransportError",
    "fix_gpiozero_dual_cs_spi",
    "is_spi_transport",
]


def __getattr__(name: str) -> Any:
    """Resolve the optional gpiozero transport on first access."""
    if name == "GpiozeroSpiTransport":
        try:
            from .transport import GpiozeroSpiTransport  # noqa: PLC0415
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
