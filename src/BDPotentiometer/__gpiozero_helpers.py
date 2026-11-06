"""gpiozero patch that lets two hardware-SPI devices share one SPI port.

gpiozero refuses to create a second hardware-SPI device on a port that is
already in use, even when the two devices use different chip-select lines (as
the MCP4xxx dual-potentiometer boards do). `fix_gpiozero_dual_cs_spi` replaces
`Device.pin_factory` with a factory whose SPI classes treat only a same port and
same device pair as a conflict. Without the Raspberry Pi pin backend the
function is a no-op.
"""

import logging
import os
from typing import Any

_LOGGER = logging.getLogger(__name__)

# The factory class installed by the last successful call. It lives at module
# scope so a later call can recognize its own factory instead of stacking
# another subclass on top of it.
_PATCHED_FACTORY_CLS: type | None = None


def _fixed_factory_for(base_factory_cls: type) -> type:
    """
    Build a dual-CS factory subclass for `base_factory_cls`.

    The base class is the active gpiozero factory type, so the patch keeps the
    pin backend gpiozero already selected instead of forcing RPi.GPIO.

    :param base_factory_cls: Local pin factory type to subclass.
    :return: Factory class whose hardware-SPI classes only conflict on the
        same port and device pair.
    """
    from gpiozero.pins.local import (  # noqa: PLC0415
        LocalPiHardwareSPI,
        LocalPiHardwareSPIShared,
    )

    class LocalPiHardwareSPIFixed(LocalPiHardwareSPI):
        """Hardware SPI that conflicts only on the same port and device."""

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
        """Shared hardware SPI with the same port/device conflict rule."""

        def _conflicts_with(self, other):
            return not (
                isinstance(other, LocalPiHardwareSPI)
                and (self._port, self._device) != (other._port, other._device)
            )

        @property
        def value(self):
            """SPI pins carry no device state, so the value is not implemented."""
            raise NotImplementedError

    def _get_spi_class(self, shared, hardware):
        """
        Return the fixed SPI class for hardware SPI.

        :param shared: Flag for shared usage of the SPI port.
        :param hardware: Flag for hardware SPI usage.
        :return: Fixed SPI class for hardware SPI, the parent class otherwise.
        """
        if hardware:
            if shared:
                return LocalPiHardwareSPISharedFixed
            return LocalPiHardwareSPIFixed
        # `base_factory_cls` is typed as plain `type` because gpiozero is an
        # optional dependency and its factory protocol cannot be imported for
        # static analysis.
        factory: Any = base_factory_cls
        return factory._get_spi_class(self, shared, hardware)

    # Built with type() rather than a class statement because the base class is
    # only known at runtime; a class statement over a variable base prevents
    # static analysis of the MRO.
    return type(
        "FixedFactory",
        (base_factory_cls,),
        {
            "__doc__": "Active local factory whose hardware SPI can share a port.",
            "_get_spi_class": _get_spi_class,
        },
    )


def fix_gpiozero_dual_cs_spi() -> None:
    """
    Patch gpiozero so two hardware-SPI devices can share one SPI port.

    Installs a subclass of the active `LocalPiFactory` into
    `Device.pin_factory`. Its SPI classes report a conflict only when both the
    port and the device (chip select) match, instead of whenever the port
    matches. Based on https://github.com/gpiozero/gpiozero/issues/1015

    The patch applies only to gpiozero's own default `RPiGPIOFactory`. A
    factory chosen explicitly by the application is left untouched, and the
    function returns without patching when `GPIOZERO_PIN_FACTORY` is set
    because gpiozero honors that variable itself. A second call recognizes the
    factory installed by the first call and is a no-op.

    The gpiozero imports are deferred so that importing this module never
    imports gpiozero; on hosts without gpiozero or its Raspberry Pi pin backend
    the call is a no-op.

    :return: None.
    """
    global _PATCHED_FACTORY_CLS

    if "GPIOZERO_PIN_FACTORY" in os.environ:
        return

    try:
        # Imported lazily so the core install needs no gpiozero package.
        from gpiozero import Device  # noqa: PLC0415
        from gpiozero.pins.rpigpio import RPiGPIOFactory  # noqa: PLC0415
    except Exception as exc:  # gpiozero or its pin backend is unavailable
        _LOGGER.debug("gpiozero dual-CS patch skipped: %s", exc)
        return

    current_factory = Device.pin_factory
    if current_factory is None:
        try:
            default_factory = Device._default_pin_factory()
        except Exception:  # any backend failure means no patch
            _LOGGER.debug(
                "gpiozero could not choose a default pin factory", exc_info=True
            )
            return
        base_factory_cls = type(default_factory)
        if base_factory_cls is not RPiGPIOFactory:
            _LOGGER.debug(
                "gpiozero default factory %s is not supported; not patching",
                base_factory_cls.__name__,
            )
            return
    else:
        base_factory_cls = type(current_factory)
        if base_factory_cls is _PATCHED_FACTORY_CLS:
            return
        # Any factory the application selected is a real choice, so keep it.
        if base_factory_cls is not RPiGPIOFactory:
            return

    if _PATCHED_FACTORY_CLS is None or not issubclass(
        _PATCHED_FACTORY_CLS, base_factory_cls
    ):
        _PATCHED_FACTORY_CLS = _fixed_factory_for(base_factory_cls)
    Device.pin_factory = _PATCHED_FACTORY_CLS()
