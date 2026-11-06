"""End-to-end test of MCP4231 over SpiDevTransport with a stubbed spidev."""

import sys
import types
import unittest
from unittest import mock

try:
    from src.BDPotentiometer.mcp4xxx import MCP4231
    from src.BDPotentiometer.transport import SpiDevTransport
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4231
    from BDPotentiometer.transport import SpiDevTransport


def _stub_module(raw):
    module = types.ModuleType("spidev")
    module.SpiDev = mock.MagicMock(return_value=raw)
    return module


class TestMCP4xxxSpiDevTransport(unittest.TestCase):
    """
    Testing the opt-in spidev transport end to end.
    """

    def test_write_goes_through_xfer2(self):
        """
        A chip built on SpiDevTransport submits the MCP4231 write frame.
        """
        raw = mock.MagicMock()

        def _xfer2(tx):
            # The constructor and the post-write read both issue a read frame.
            if tx[0] & 0b00001100 == 0b00001100:
                return [0xFE, 0x00]
            return [0] * len(tx)

        raw.xfer2.side_effect = _xfer2
        with mock.patch.dict(sys.modules, {"spidev": _stub_module(raw)}):
            transport = SpiDevTransport(bus=0, device=0)
            pot = MCP4231(r_ab=10e3, transport=transport)
            raw.xfer2.reset_mock()
            pot.set_value(0, 43)
        raw.open.assert_called_once_with(0, 0)
        self.assertEqual(raw.xfer2.call_args_list[0][0][0], [0b00000000, 43])
        raw.xfer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
