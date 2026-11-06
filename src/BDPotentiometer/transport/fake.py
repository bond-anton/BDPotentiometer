"""Scripted SPI transport for tests."""

from collections.abc import Sequence
from typing import Optional

from .base import TransportClosed, TransportError


class FakeSpiTransport:
    """SPI transport that replays scripted response frames.

    Responses are consumed FIFO. `default` is returned once the queue is
    empty; with `strict=False` an empty queue yields zero-filled frames
    instead of an error.
    """

    def __init__(
        self,
        responses: Optional[list[list[int]]] = None,
        default: Optional[list[int]] = None,
        strict: bool = True,
    ) -> None:
        self._responses = list(responses) if responses is not None else []
        self._default = list(default) if default is not None else None
        self._strict = strict
        self.calls: list[list[int]] = []
        self.closed = False

    def queue(self, *responses: list[int]) -> None:
        """Append scripted response frames."""
        self._responses.extend(responses)

    def transfer(self, tx: Sequence[int]) -> list[int]:
        """Return the next scripted frame for `tx`, validating its length."""
        if self.closed:
            raise TransportClosed("FakeSpiTransport is closed")
        frame = list(tx)
        self.calls.append(frame)
        if self._responses:
            rx = list(self._responses.pop(0))
        elif self._default is not None:
            rx = list(self._default)
        elif self._strict:
            raise TransportError("FakeSpiTransport has no scripted response")
        else:
            return [0] * len(frame)
        if len(rx) != len(frame):
            raise TransportError(
                f"Response length {len(rx)} does not match request length {len(frame)}"
            )
        return rx

    def close(self) -> None:
        """Close the transport. Repeated calls have no effect."""
        self.closed = True
