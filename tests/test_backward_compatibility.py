"""Phase 5 backward-compatibility checks for the public API."""

import subprocess
import sys
import unittest
from pathlib import Path

try:
    import BDPotentiometer as package
    import BDPotentiometer.transport  # noqa: F401
    from BDPotentiometer import (
        DigitalPotentiometerDevice,
        DigitalWiper,
        FakeSpiTransport,
        GpiozeroSpiTransport,
        I2cTransport,
        Potentiometer,
        SpiDevTransport,
        SpiDigitalWiper,
        SpiTransport,
        TransportClosed,
        TransportError,
        fix_gpiozero_dual_cs_spi,
        is_spi_transport,
    )
    from BDPotentiometer.mcp4xxx import MCP4231, MCP4232, MCP4251
    from BDPotentiometer.mcp4xxx.mcp4xxx import MCP4xxx
except ModuleNotFoundError:
    import src.BDPotentiometer.transport  # noqa: F401
    from src import BDPotentiometer as package
    from src.BDPotentiometer import (
        DigitalPotentiometerDevice,
        DigitalWiper,
        FakeSpiTransport,
        GpiozeroSpiTransport,
        I2cTransport,
        Potentiometer,
        SpiDevTransport,
        SpiDigitalWiper,
        SpiTransport,
        TransportClosed,
        TransportError,
        fix_gpiozero_dual_cs_spi,
        is_spi_transport,
    )
    from src.BDPotentiometer.mcp4xxx import MCP4231, MCP4232, MCP4251
    from src.BDPotentiometer.mcp4xxx.mcp4xxx import MCP4xxx


class TestPublicExports(unittest.TestCase):
    """Public symbols stay importable from the package root."""

    def test_root_symbols(self):
        """Package root exports the documented classes and helper."""
        symbols = (
            Potentiometer,
            DigitalWiper,
            SpiDigitalWiper,
            DigitalPotentiometerDevice,
            fix_gpiozero_dual_cs_spi,
        )
        for symbol in symbols:
            self.assertTrue(symbol is not None)

    def test_transport_symbols(self):
        """Package root re-exports the transport surface."""
        symbols = (
            SpiTransport,
            I2cTransport,
            TransportError,
            TransportClosed,
            is_spi_transport,
            FakeSpiTransport,
            SpiDevTransport,
            GpiozeroSpiTransport,
        )
        for symbol in symbols:
            self.assertTrue(symbol is not None)

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

    def test_fix_helper_callable(self):
        """fix_gpiozero_dual_cs_spi stays callable."""
        self.assertTrue(callable(fix_gpiozero_dual_cs_spi))

    def test_mcp4xxx_is_not_spidevice(self):
        """MCP4xxx no longer inherits from gpiozero.SPIDevice."""
        try:
            from gpiozero import SPIDevice
        except ImportError:
            self.skipTest("gpiozero is not available")
        self.assertFalse(issubclass(MCP4xxx, SPIDevice))

    def test_importing_package_does_not_import_spidev(self):
        """Importing the package alone does not import the optional spidev."""
        self.assertIsNotNone(SpiDevTransport)
        source_root = Path(__file__).resolve().parents[1] / "src"
        code = (
            "import sys\n"
            f"sys.path.insert(0, {str(source_root)!r})\n"
            "import BDPotentiometer\n"
            "print('spidev' in sys.modules)\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.stdout.strip(), "False", result.stderr)


if __name__ == "__main__":
    unittest.main()
