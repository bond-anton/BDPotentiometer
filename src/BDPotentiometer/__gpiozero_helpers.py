"""gpiozero patch that lets two hardware-SPI devices share one SPI port.

gpiozero refuses to create a second hardware-SPI device on a port that is
already in use, even when the two devices use different chip-select lines (as
the MCP4xxx dual-potentiometer boards do). `fix_gpiozero_dual_cs_spi` replaces
`Device.pin_factory` with a factory whose SPI classes treat only a same port and
same device pair as a conflict. Without the Raspberry Pi pin backend the
function is a no-op stub.
"""

try:
    from gpiozero import Device
    from gpiozero.pins.local import LocalPiHardwareSPI, LocalPiHardwareSPIShared
    from gpiozero.pins.rpigpio import RPiGPIOFactory
except ModuleNotFoundError:

    def fix_gpiozero_dual_cs_spi() -> None:
        """No-op stub: the gpiozero Raspberry Pi pin backend is unavailable."""

else:

    def fix_gpiozero_dual_cs_spi() -> None:
        """
        Patch gpiozero so two hardware-SPI devices can share one SPI port.

        Installs a `RPiGPIOFactory` subclass into `Device.pin_factory`. Its SPI
        classes report a conflict only when both the port and the device (chip
        select) match, instead of whenever the port matches. Based on
        https://github.com/gpiozero/gpiozero/issues/1015

        :return: None.
        """

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

        Device.pin_factory = FixedRPiGPIOFactory()
