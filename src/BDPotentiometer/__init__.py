"""Module to operate SPI digital potentiometer devices"""

__version__ = "0.1.0"


from .__gpiozero_helpers import fix_gpiozero_dual_cs_spi
from .digital_potentiometer import DigitalPotentiometerDevice
from .digital_wiper import DigitalWiper, SpiDigitalWiper
from .potentiometer import Potentiometer
from .transport import (
    FakeSpiTransport,
    GpiozeroSpiTransport,
    I2cTransport,
    SpiDevTransport,
    SpiTransport,
    TransportClosed,
    TransportError,
    is_spi_transport,
)

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
