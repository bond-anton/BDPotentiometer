"""Tests for FakeSpiTransport."""

import unittest

try:
    from src.BDPotentiometer.transport import (
        FakeSpiTransport,
        TransportClosed,
        TransportError,
    )
except ModuleNotFoundError:
    from BDPotentiometer.transport import (
        FakeSpiTransport,
        TransportClosed,
        TransportError,
    )


class TestFakeSpiTransport(unittest.TestCase):
    """
    Testing the scripted SPI transport.
    """

    def test_responses_are_replayed_fifo(self) -> None:
        """
        Scripted frames are consumed in order and calls are recorded.
        """
        fake = FakeSpiTransport(responses=[[0, 43], [0, 44]])
        self.assertEqual(fake.transfer([0b00000000, 1]), [0, 43])
        self.assertEqual(fake.transfer([0b00010000, 2]), [0, 44])
        self.assertEqual(fake.calls, [[0b00000000, 1], [0b00010000, 2]])

    def test_queue_appends_responses(self) -> None:
        """
        queue() appends frames behind the constructor responses.
        """
        fake = FakeSpiTransport(responses=[[0, 1]])
        fake.queue([0, 2], [0, 3])
        self.assertEqual(fake.transfer([0, 0]), [0, 1])
        self.assertEqual(fake.transfer([0, 0]), [0, 2])
        self.assertEqual(fake.transfer([0, 0]), [0, 3])

    def test_calls_record_plain_lists(self) -> None:
        """
        Outbound frames are copied to plain lists.
        """
        fake = FakeSpiTransport(default=[0, 0])
        tx = (1, 2)
        fake.transfer(tx)
        self.assertEqual(fake.calls, [[1, 2]])
        self.assertIsInstance(fake.calls[0], list)

    def test_default_fallback(self) -> None:
        """
        The default frame is returned once the queue is empty.
        """
        fake = FakeSpiTransport(default=[0, 7])
        self.assertEqual(fake.transfer([0, 0]), [0, 7])
        self.assertEqual(fake.transfer([0, 0]), [0, 7])
        self.assertEqual(len(fake.calls), 2)

    def test_strict_missing_response_raises(self) -> None:
        """
        An empty queue without a default raises TransportError in strict mode.
        """
        fake = FakeSpiTransport()
        with self.assertRaises(TransportError) as context:
            fake.transfer([0, 0])
        self.assertIn("no scripted response", str(context.exception))

    def test_non_strict_returns_zeros(self) -> None:
        """
        Non-strict mode returns a zero frame of the request length.
        """
        fake = FakeSpiTransport(strict=False)
        self.assertEqual(fake.transfer([1, 2, 3]), [0, 0, 0])

    def test_length_mismatch_raises(self) -> None:
        """
        A response whose length differs from the request raises TransportError.
        """
        fake = FakeSpiTransport(responses=[[0]])
        with self.assertRaises(TransportError):
            fake.transfer([0, 0])

    def test_default_length_mismatch_raises(self) -> None:
        """
        A default frame of the wrong length raises TransportError.
        """
        fake = FakeSpiTransport(default=[0])
        with self.assertRaises(TransportError):
            fake.transfer([0, 0])

    def test_close_blocks_transfers(self) -> None:
        """
        Transfers after close() raise TransportClosed.
        """
        fake = FakeSpiTransport(default=[0, 0])
        fake.close()
        self.assertTrue(fake.closed)
        with self.assertRaises(TransportClosed):
            fake.transfer([0, 0])

    def test_close_is_idempotent(self) -> None:
        """
        close() can be called repeatedly.
        """
        fake = FakeSpiTransport()
        fake.close()
        fake.close()
        self.assertTrue(fake.closed)


if __name__ == "__main__":
    unittest.main()
