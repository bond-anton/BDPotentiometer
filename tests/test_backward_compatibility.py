"""Backward-compatibility checks for the public API."""

import importlib
import subprocess
import sys
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_ROOT))

import BDPotentiometer as package  # noqa: E402
from BDPotentiometer import (  # noqa: E402
    DigitalPotentiometerDevice,
    DigitalWiper,
    Potentiometer,
    SpiDigitalWiper,
)
from BDPotentiometer.mcp4xxx import MCP4231, MCP4232, MCP4251  # noqa: E402
from BDPotentiometer.mcp4xxx.mcp4xxx import MCP4xxx  # noqa: E402

_TRANSPORT_NAMES = frozenset(
    {
        "FakeSpiTransport",
        "GpiozeroSpiTransport",
        "I2cTransport",
        "SpiDevTransport",
        "SpiTransport",
        "TransportClosed",
        "TransportError",
        "fix_gpiozero_dual_cs_spi",
        "is_spi_transport",
    }
)


class TestPublicExports(unittest.TestCase):
    """Public symbols stay importable from the package root."""

    def test_root_symbols(self):
        """Package root exports the documented device classes."""
        symbols = (
            Potentiometer,
            DigitalWiper,
            SpiDigitalWiper,
            DigitalPotentiometerDevice,
        )
        for symbol in symbols:
            self.assertTrue(symbol is not None)

    def test_transport_module_removed(self):
        """The bundled transport package is gone, not re-exported."""
        with self.assertRaises(ModuleNotFoundError):
            importlib.import_module(f"{package.__name__}.transport")

    def test_all_has_no_transport_names(self):
        """No transport name is advertised from the package root."""
        self.assertFalse(_TRANSPORT_NAMES & set(package.__all__))

    def test_star_import_skips_transport(self):
        """A star import works and leaves the transport surface to scietex."""
        namespace = {}
        exec("from BDPotentiometer import *", namespace)  # noqa: S102
        self.assertIn("DigitalWiper", namespace)
        self.assertFalse(_TRANSPORT_NAMES & set(namespace))

    def test_mcp4xxx_chips(self):
        """Chip classes remain importable from the mcp4xxx package."""
        for chip in (MCP4231, MCP4251, MCP4232):
            self.assertTrue(chip is not None)

    def test_version_unchanged(self):
        """Package version is still exported."""
        self.assertIsInstance(package.__version__, str)


class TestCompatibilitySurface(unittest.TestCase):
    """Legacy accessors and the non-SPIDevice change are documented by tests."""

    def test_device_close_and_spi(self):
        """MCP4xxx devices keep close() and spi attributes."""
        self.assertTrue(hasattr(MCP4231, "close"))
        self.assertTrue(hasattr(MCP4231, "spi"))

    def test_wiper_transport(self):
        """SpiDigitalWiper exposes the canonical transport accessor."""
        self.assertTrue(hasattr(SpiDigitalWiper, "transport"))

    def test_mcp4xxx_is_not_spidevice(self):
        """MCP4xxx no longer inherits from gpiozero.SPIDevice."""
        try:
            from gpiozero import SPIDevice
        except ImportError:
            self.skipTest("gpiozero is not available")
        self.assertFalse(issubclass(MCP4xxx, SPIDevice))

    def test_importing_package_does_not_import_spidev(self):
        """Importing the package alone does not import the optional spidev."""
        code = (
            "import sys\n"
            f"sys.path.insert(0, {str(SOURCE_ROOT)!r})\n"
            "import BDPotentiometer\n"
            "print('spidev' in sys.modules)\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(result.stdout.strip(), "False", result.stderr)


if __name__ == "__main__":
    unittest.main()
