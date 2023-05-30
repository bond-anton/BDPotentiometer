"""Some helpers for gpiozero."""

try:
    from gpiozero import Device
    from gpiozero.pins.local import LocalPiHardwareSPI, LocalPiHardwareSPIShared
    from gpiozero.pins.rpigpio import RPiGPIOFactory
except ModuleNotFoundError:
    pass


def fix_gpiozero_dual_cs_spi() -> None:
    """
    A workaround written by slghb GitHub user to use two spi devices with hardware spi.
    Taken from https://github.com/gpiozero/gpiozero/issues/1015

    :return: None.
    """

    class LocalPiHardwareSPIFixed(LocalPiHardwareSPI):
        """Custom conflict checker"""

        # pylint: disable=too-few-public-methods
        def _conflicts_with(self, other):
            # pylint: disable=protected-access
            return not (
                isinstance(other, LocalPiHardwareSPI)
                and (self._port, self._device) != (other._port, other._device)
            )

        @property
        def value(self):
            """
            Returns a value representing the device's state. Frequently, this is a
            boolean value, or a number between 0 and 1 but some devices use larger
            ranges (e.g. -1 to +1) and composite devices usually use tuples to
            return the states of all their subordinate components.
            """
            raise NotImplementedError

    class LocalPiHardwareSPISharedFixed(LocalPiHardwareSPIShared):
        """Custom Shared SPI hardware class inheriting from fixed Hardware SPI class above"""

        def _conflicts_with(self, other):
            # pylint: disable=protected-access
            return not (
                isinstance(other, LocalPiHardwareSPI)
                and (self._port, self._device) != (other._port, other._device)
            )

        @property
        def value(self):
            """
            Returns a value representing the device's state. Frequently, this is a
            boolean value, or a number between 0 and 1 but some devices use larger
            ranges (e.g. -1 to +1) and composite devices usually use tuples to
            return the states of all their subordinate components.
            """
            raise NotImplementedError

    class FixedRPiGPIOFactory(RPiGPIOFactory):
        """Fixed RPiGPIOFactory"""

        def _get_spi_class(self, shared, hardware):
            """
            Return a Fixed SPI class if shared hardware SPI port between two devices

            :param shared: Flag for shared usage of SPI port.
            :param hardware: Flag for hardware SPI usage.
            :return:
            """
            if hardware:
                if shared:
                    return LocalPiHardwareSPISharedFixed
                return LocalPiHardwareSPIFixed
            return super()._get_spi_class(shared, hardware)

    Device.pin_factory = FixedRPiGPIOFactory()


def fix_gpiozero_dual_cs_spi_dummy() -> None:
    """
    A stub function if there will be problems importing above function
    """
