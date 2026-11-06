"""Default SPI backend selection shared by the device constructors."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .base import SpiTransport


#: Keyword names accepted by both the legacy constructor and the gpiozero
#: backend, in the order the transport forwards them.
GPIOZERO_SPI_ARGS: tuple[str, ...] = (
    "port",
    "device",
    "clock_pin",
    "mosi_pin",
    "miso_pin",
    "select_pin",
)

#: Pin keywords that select the gpiozero backend; `port` and `device` alone
#: are also valid for the spidev backend.
GPIOZERO_PIN_ARGS: tuple[str, ...] = (
    "clock_pin",
    "mosi_pin",
    "miso_pin",
    "select_pin",
)


def build_default_transport(  # noqa: PLR0913
    *,
    port: Optional[int] = None,
    device: Optional[int] = None,
    clock_pin: Optional[int] = None,
    mosi_pin: Optional[int] = None,
    miso_pin: Optional[int] = None,
    select_pin: Optional[int] = None,
) -> "SpiTransport":
    """
    Build the default SPI transport from the legacy keyword arguments.

    Pin keywords select the gpiozero backend and require the optional
    ``gpiozero`` package. Without pin keywords the spidev backend is used;
    its ``spidev`` package is imported lazily when the transport is built.

    :param port: SPI port (gpiozero) or bus number (spidev).
    :param device: SPI device number (chip select).
    :param clock_pin: GPIO pin used as SPI clock.
    :param mosi_pin: GPIO pin used as SPI MOSI.
    :param miso_pin: GPIO pin used as SPI MISO.
    :param select_pin: GPIO pin used as SPI chip select.
    :return: SPI transport selected by the supplied keywords.
    :raises ImportError: If pin keywords are given and gpiozero is missing.
    """
    supplied = {
        "port": port,
        "device": device,
        "clock_pin": clock_pin,
        "mosi_pin": mosi_pin,
        "miso_pin": miso_pin,
        "select_pin": select_pin,
    }
    if any(supplied[name] is not None for name in GPIOZERO_PIN_ARGS):
        try:
            # Imported lazily so the core install needs no gpiozero package.
            from .gpiozero_spi import GpiozeroSpiTransport  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "The gpiozero pin keywords require the optional 'gpiozero' "
                "package. Install it with: pip install "
                "'BDPotentiometer[gpiozero]'"
            ) from exc
        spi_args = {
            name: supplied[name]
            for name in GPIOZERO_SPI_ARGS
            if supplied[name] is not None
        }
        return GpiozeroSpiTransport(**spi_args)
    # Imported lazily so the core install needs no spidev package.
    from .spidev_spi import SpiDevTransport  # noqa: PLC0415

    return SpiDevTransport(bus=port or 0, device=device or 0)
