"""Optional backend isolation: the core install needs no gpiozero or spidev."""

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"


def _run_isolated(code: str) -> subprocess.CompletedProcess:
    """Run `code` in a fresh interpreter rooted at the package sources."""
    bootstrap = f"import sys\nsys.path.insert(0, {str(SOURCE_ROOT)!r})\n"
    return subprocess.run(
        [sys.executable, "-c", bootstrap + code],
        cwd=str(SOURCE_ROOT.parent),
        capture_output=True,
        text=True,
        check=False,
    )


class TestOptionalBackends(unittest.TestCase):
    """The package imports and runs without the optional SPI backends."""

    def assert_ran(self, result: subprocess.CompletedProcess) -> None:
        """Fail with the subprocess stderr when its script did not finish."""
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ok", result.stderr)

    def test_import_does_not_load_optional_backends(self):
        """Importing the package, mcp4xxx, and transport loads neither backend."""
        result = _run_isolated(
            "import BDPotentiometer\n"
            "import BDPotentiometer.mcp4xxx\n"
            "import BDPotentiometer.transport\n"
            "loaded = [name for name in ('gpiozero', 'spidev') "
            "if name in sys.modules]\n"
            "if loaded:\n"
            "    raise SystemExit(f'importing the package loaded {loaded}')\n"
            "print('ok')\n"
        )
        self.assert_ran(result)

    def test_missing_spidev_names_the_spi_extra(self):
        """device= without spidev raises ImportError naming the spi extra."""
        result = _run_isolated(
            "sys.modules['spidev'] = None\n"
            "from BDPotentiometer.mcp4xxx import MCP4231\n"
            "try:\n"
            "    MCP4231(r_ab=10e3, device=0)\n"
            "except ImportError as exc:\n"
            "    if 'BDPotentiometer[spi]' not in str(exc):\n"
            "        raise SystemExit(f'unexpected message: {exc}')\n"
            "    print('ok')\n"
            "else:\n"
            "    raise SystemExit('MCP4231 did not raise ImportError without spidev')\n"
        )
        self.assert_ran(result)

    def test_missing_gpiozero_names_the_gpiozero_extra(self):
        """A pin keyword without gpiozero raises ImportError naming its extra."""
        result = _run_isolated(
            "sys.modules['gpiozero'] = None\n"
            "from BDPotentiometer.mcp4xxx import MCP4231\n"
            "try:\n"
            "    MCP4231(r_ab=10e3, clock_pin=11)\n"
            "except ImportError as exc:\n"
            "    if 'BDPotentiometer[gpiozero]' not in str(exc):\n"
            "        raise SystemExit(f'unexpected message: {exc}')\n"
            "    print('ok')\n"
            "else:\n"
            "    raise SystemExit('MCP4231 did not raise ImportError without gpiozero')\n"
        )
        self.assert_ran(result)

    def test_missing_gpiozero_hides_transport_attribute(self):
        """Without gpiozero, hasattr is False and dir still advertises the name."""
        result = _run_isolated(
            "sys.modules['gpiozero'] = None\n"
            "import BDPotentiometer\n"
            "import BDPotentiometer.transport\n"
            "if hasattr(BDPotentiometer.transport, 'GpiozeroSpiTransport'):\n"
            "    raise SystemExit('transport exposes GpiozeroSpiTransport')\n"
            "if hasattr(BDPotentiometer, 'GpiozeroSpiTransport'):\n"
            "    raise SystemExit('package exposes GpiozeroSpiTransport')\n"
            "if 'GpiozeroSpiTransport' not in dir(BDPotentiometer.transport):\n"
            "    raise SystemExit('transport does not advertise GpiozeroSpiTransport')\n"
            "print('ok')\n"
        )
        self.assert_ran(result)

    def test_gpiozero_transport_resolves_when_available(self):
        """With gpiozero installed, both lazy resolvers return the class."""
        if importlib.util.find_spec("gpiozero") is None:
            self.skipTest("gpiozero is not installed")

        import BDPotentiometer
        import BDPotentiometer.transport

        self.assertIsInstance(BDPotentiometer.transport.GpiozeroSpiTransport, type)
        self.assertIsInstance(BDPotentiometer.GpiozeroSpiTransport, type)

    def test_injected_transport_works_without_both_backends(self):
        """An injected transport keeps the device usable without either backend."""
        result = _run_isolated(
            "sys.modules['spidev'] = None\n"
            "sys.modules['gpiozero'] = None\n"
            "from BDPotentiometer.mcp4xxx import MCP4231\n"
            "from BDPotentiometer.transport import FakeSpiTransport\n"
            "fake = FakeSpiTransport(default=[0, 0])\n"
            "pot = MCP4231(r_ab=10e3, transport=fake)\n"
            "pot.set_value(0, 43)\n"
            "if fake.calls[-2:] != [[0b00000000, 43], [0b00001100, 0]]:\n"
            "    raise SystemExit(f'unexpected frames: {fake.calls}')\n"
            "if pot.channels[0].potentiometer.wiper_position != 43 / 128:\n"
            "    raise SystemExit('wiper position was not applied')\n"
            "print('ok')\n"
        )
        self.assert_ran(result)


if __name__ == "__main__":
    unittest.main()
