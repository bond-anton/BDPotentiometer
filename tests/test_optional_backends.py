"""Optional backend isolation: the core install needs no gpiozero or spidev."""

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
        """Importing the package and mcp4xxx loads neither backend."""
        result = _run_isolated(
            "import BDPotentiometer\n"
            "import BDPotentiometer.mcp4xxx\n"
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
            "    if 'scietex.hal.spi[spi]' not in str(exc):\n"
            "        raise SystemExit(f'unexpected message: {exc}')\n"
            "    print('ok')\n"
            "else:\n"
            "    raise SystemExit('MCP4231 did not raise ImportError without spidev')\n"
        )
        self.assert_ran(result)


if __name__ == "__main__":
    unittest.main()
