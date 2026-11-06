"""A transport built by the constructor must not leak when validation fails."""

import unittest
from unittest import mock

try:
    from src.BDPotentiometer.mcp4xxx import mcp4xxx as mcp4xxx_module
    from src.BDPotentiometer.mcp4xxx.mcp4xxx import MCP4xxx
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import mcp4xxx as mcp4xxx_module
    from BDPotentiometer.mcp4xxx.mcp4xxx import MCP4xxx


class _ClosableOnly:
    """Records close() but lacks transfer(), so it fails validation."""

    def __init__(self) -> None:
        self.close_calls = 0

    def close(self) -> None:
        """Count the release."""
        self.close_calls += 1


class _Accepted:
    """Satisfies the transport protocol and records close()."""

    def __init__(self) -> None:
        self.close_calls = 0

    def transfer(self, tx):
        """Return a zero response; unused by these tests."""
        return [0] * len(tx)

    def close(self) -> None:
        """Count the release."""
        self.close_calls += 1


class TestBuiltTransportLeak(unittest.TestCase):
    """Only a self-built transport is released when validation fails."""

    def tearDown(self) -> None:
        """No patching survives a test."""
        mock.patch.stopall()

    def test_rejected_built_transport_is_closed(self):
        """A built transport that fails validation is closed exactly once."""
        stub = _ClosableOnly()
        with (
            mock.patch.object(
                mcp4xxx_module, "build_default_transport", return_value=stub
            ),
            self.assertRaises(TypeError),
        ):
            MCP4xxx()
        self.assertEqual(stub.close_calls, 1)

    def test_accepted_built_transport_is_kept_open(self):
        """A built transport that validates is stored and left open."""
        stub = _Accepted()
        with mock.patch.object(
            mcp4xxx_module, "build_default_transport", return_value=stub
        ):
            device = MCP4xxx()
        self.assertIs(device.transport, stub)
        self.assertEqual(stub.close_calls, 0)

    def test_rejected_caller_transport_is_not_closed(self):
        """A caller-supplied transport stays open even when rejected."""
        stub = _ClosableOnly()
        with self.assertRaises(TypeError):
            MCP4xxx(transport=stub)
        self.assertEqual(stub.close_calls, 0)


if __name__ == "__main__":
    unittest.main()
