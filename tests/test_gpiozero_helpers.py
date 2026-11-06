"""Tests for the gpiozero dual-CS SPI helper."""

import os
import sys
import types
import unittest
from unittest import mock

try:
    import BDPotentiometer.__gpiozero_helpers as helpers
except ModuleNotFoundError:
    from src.BDPotentiometer import __gpiozero_helpers as helpers


def _fake_modules():
    """Build a gpiozero module tree with a controllable default factory."""
    local = types.ModuleType("gpiozero.pins.local")

    class FakeLocalPiHardwareSPI:
        """Stand-in for gpiozero's local hardware SPI class."""

    class FakeLocalPiHardwareSPIShared(FakeLocalPiHardwareSPI):
        """Stand-in for gpiozero's shared local hardware SPI class."""

    class FakeLocalPiFactory:
        """Stand-in for gpiozero's local pin factory."""

        def _get_spi_class(self, shared, hardware):
            """Return the stand-in SPI class for hardware transfers."""
            return FakeLocalPiHardwareSPIShared if shared else FakeLocalPiHardwareSPI

    class FakeRPiGPIOFactory(FakeLocalPiFactory):
        """Stand-in for gpiozero's default RPi.GPIO factory."""

    class FakeUserFactory:
        """Stand-in for a factory the application selected explicitly."""

    local.LocalPiHardwareSPI = FakeLocalPiHardwareSPI
    local.LocalPiHardwareSPIShared = FakeLocalPiHardwareSPIShared

    rpigpio = types.ModuleType("gpiozero.pins.rpigpio")
    rpigpio.RPiGPIOFactory = FakeRPiGPIOFactory

    class FakeDevice:
        """Stand-in for gpiozero.Device with a class-level factory."""

        pin_factory = None
        default_factory = FakeRPiGPIOFactory

        @classmethod
        def _default_pin_factory(cls):
            """Return the configured default factory."""
            return cls.default_factory()

    pins = types.ModuleType("gpiozero.pins")
    pins.local = local
    pins.rpigpio = rpigpio
    gpiozero = types.ModuleType("gpiozero")
    gpiozero.Device = FakeDevice
    gpiozero.pins = pins

    modules = {
        "gpiozero": gpiozero,
        "gpiozero.pins": pins,
        "gpiozero.pins.local": local,
        "gpiozero.pins.rpigpio": rpigpio,
    }
    return modules, FakeDevice, FakeRPiGPIOFactory, FakeUserFactory


class TestGpiozeroHelpers(unittest.TestCase):
    """The dual-CS helper degrades to a no-op without the Pi pin backend."""

    def setUp(self):
        self._saved_patched_class = helpers._PATCHED_FACTORY_CLS
        helpers._PATCHED_FACTORY_CLS = None

    def tearDown(self):
        helpers._PATCHED_FACTORY_CLS = self._saved_patched_class

    def test_helper_is_callable(self):
        """The helper is exported as a callable on every host."""
        self.assertTrue(callable(helpers.fix_gpiozero_dual_cs_spi))

    def test_helper_without_gpiozero_does_not_raise(self):
        """A host without gpiozero gets a no-op instead of an ImportError."""
        blocked = {
            "gpiozero": None,
            "gpiozero.pins.local": None,
            "gpiozero.pins.rpigpio": None,
        }
        with mock.patch.dict(sys.modules, blocked):
            self.assertIsNone(helpers.fix_gpiozero_dual_cs_spi())

    def test_helper_without_pin_backend_does_not_raise(self):
        """A host without gpiozero's RPi pin backend gets a no-op stub."""
        blocked = {"gpiozero.pins.rpigpio": None, "RPi.GPIO": None}
        with mock.patch.dict(sys.modules, blocked):
            self.assertIsNone(helpers.fix_gpiozero_dual_cs_spi())

    def test_patches_gpiozero_default_factory(self):
        """gpiozero's already-auto-selected default factory gets patched."""
        modules, device, base_factory, _ = _fake_modules()
        device.pin_factory = base_factory()

        with mock.patch.dict(sys.modules, modules):
            helpers.fix_gpiozero_dual_cs_spi()

        self.assertIsInstance(device.pin_factory, base_factory)
        self.assertIsNot(type(device.pin_factory), base_factory)
        self.assertIs(type(device.pin_factory), helpers._PATCHED_FACTORY_CLS)

    def test_patches_fresh_process_default_factory(self):
        """Before any device exists the default factory type is used."""
        modules, device, base_factory, _ = _fake_modules()
        device.pin_factory = None

        with mock.patch.dict(sys.modules, modules):
            helpers.fix_gpiozero_dual_cs_spi()

        self.assertIsInstance(device.pin_factory, base_factory)
        self.assertIs(type(device.pin_factory), helpers._PATCHED_FACTORY_CLS)

    def test_leaves_user_factory_untouched(self):
        """A factory selected by the application is a real choice."""
        modules, device, _, user_factory = _fake_modules()
        chosen = user_factory()
        device.pin_factory = chosen

        with mock.patch.dict(sys.modules, modules):
            helpers.fix_gpiozero_dual_cs_spi()

        self.assertIs(device.pin_factory, chosen)

    def test_leaves_unsupported_default_untouched(self):
        """A non-RPi default backend is not patched by this helper."""
        modules, device, _, user_factory = _fake_modules()
        device.pin_factory = None
        device.default_factory = user_factory

        with mock.patch.dict(sys.modules, modules):
            helpers.fix_gpiozero_dual_cs_spi()

        self.assertIsNone(device.pin_factory)

    def test_second_call_is_a_noop(self):
        """Calling twice does not stack another factory subclass."""
        modules, device, base_factory, _ = _fake_modules()
        device.pin_factory = base_factory()

        with mock.patch.dict(sys.modules, modules):
            helpers.fix_gpiozero_dual_cs_spi()
            first_factory = device.pin_factory
            helpers.fix_gpiozero_dual_cs_spi()

        self.assertIs(device.pin_factory, first_factory)

    def test_environment_override_is_respected(self):
        """GPIOZERO_PIN_FACTORY means gpiozero makes the choice itself."""
        modules, device, base_factory, _ = _fake_modules()
        chosen = base_factory()
        device.pin_factory = chosen

        with (
            mock.patch.dict(sys.modules, modules),
            mock.patch.dict(os.environ, {"GPIOZERO_PIN_FACTORY": "mock"}),
        ):
            helpers.fix_gpiozero_dual_cs_spi()

        self.assertIs(device.pin_factory, chosen)


if __name__ == "__main__":
    unittest.main()
