def fix_gpiozero_dual_cs_spi() -> None:
    from gpiozero import Device
    from gpiozero.pins.local import (
        LocalPiHardwareSPI,
        LocalPiHardwareSPIShared,
    )
    from gpiozero.pins.rpigpio import RPiGPIOFactory

    class LocalPiHardwareSPIFixed(LocalPiHardwareSPI):
        def _conflicts_with(self, other):
            return not (
                isinstance(other, LocalPiHardwareSPI)
                and (self._port, self._device) != (other._port, other._device)
            )

    class LocalPiHardwareSPISharedFixed(
            LocalPiHardwareSPIShared, LocalPiHardwareSPIFixed
    ):
        pass

    class FixedRPiGPIOFactory(RPiGPIOFactory):
        def _get_spi_class(self, shared, hardware):
            if hardware:
                if shared:
                    return LocalPiHardwareSPISharedFixed
                return LocalPiHardwareSPIFixed
            return super()._get_spi_class(shared, hardware)

    Device.pin_factory = FixedRPiGPIOFactory()


def fix_gpiozero_dual_cs_spi_dummy() -> None:
    pass
