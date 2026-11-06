"""gpiozero patch that lets two hardware-SPI devices share one SPI port.

gpiozero refuses to create a second hardware-SPI device on a port that is
already in use, even when the two devices use different chip-select lines (as
the MCP4xxx dual-potentiometer boards do). `fix_gpiozero_dual_cs_spi` replaces
`Device.pin_factory` with a factory whose SPI classes treat only a same port and
same device pair as a conflict. Without the Raspberry Pi pin backend the
function is a no-op.
"""


def fix_gpiozero_dual_cs_spi() -> None:
    """
    Patch gpiozero so two hardware-SPI devices can share one SPI port.

    Installs a `RPiGPIOFactory` subclass into `Device.pin_factory`. Its SPI
    classes report a conflict only when both the port and the device (chip
    select) match, instead of whenever the port matches. Based on
    https://github.com/gpiozero/gpiozero/issues/1015

    The gpiozero imports are deferred so that importing this module never
    imports gpiozero; on hosts without gpiozero or its Raspberry Pi pin backend
    the call is a no-op.

    :return: None.
    """
    try:
        # Imported lazily so the core install needs no gpiozero package.
        from gpiozero import Device  # noqa: PLC0415
        from gpiozero.pins.local import (  # noqa: PLC0415
            LocalPiHardwareSPI,
            LocalPiHardwareSPIShared,
        )
        from gpiozero.pins.rpigpio import RPiGPIOFactory  # noqa: PLC0415
    except ModuleNotFoundError:
        return

    class LocalPiHardwareSPIFixed(LocalPiHardwareSPI):
        """Custom conflict checker"""

        def _conflicts_with(self, other):
            return not (
                isinstance(other, LocalPiHardwareSPI)
                and (self._port, self._device) != (other._port, other._device)
            )

        @property
        def value(self):
            """SPI pins carry no device state, so the value is not implemented."""
            raise NotImplementedError

    class LocalPiHardwareSPISharedFixed(LocalPiHardwareSPIShared):
        """Custom Shared SPI hardware class inheriting from fixed Hardware SPI class above"""

        def _conflicts_with(self, other):
            return not (
                isinstance(other, LocalPiHardwareSPI)
                and (self._port, self._device) != (other._port, other._device)
            )

        @property
        def value(self):
            """SPI pins carry no device state, so the value is not implemented."""
            raise NotImplementedError

    class FixedRPiGPIOFactory(RPiGPIOFactory):
        """Fixed RPiGPIOFactory"""

        def _get_spi_class(self, shared, hardware):
            """
            Return a Fixed SPI class if shared hardware SPI port between two devices

            :param shared: Flag for shared usage of SPI port.
            :param hardware: Flag for hardware SPI usage.
            :return: Fixed SPI class for hardware SPI, the parent class otherwise.
            """
            if hardware:
                if shared:
                    return LocalPiHardwareSPISharedFixed
                return LocalPiHardwareSPIFixed
            return super()._get_spi_class(shared, hardware)

    current_factory = Device.pin_factory
    # An existing factory is the user's backend choice (MockFactory, lgpio, ...), so keep it.
    if current_factory is not None and not isinstance(
        current_factory, FixedRPiGPIOFactory
    ):
        return
    Device.pin_factory = FixedRPiGPIOFactory()
