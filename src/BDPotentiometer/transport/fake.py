"""Scripted SPI transport for tests."""

from collections.abc import Sequence
from typing import Optional

from .base import TransportClosed, TransportError


class FakeSpiTransport:
    """SPI transport that replays scripted response frames.

    Responses are consumed FIFO. `default` is returned once the queue is
    empty; with `strict=False` an empty queue yields zero-filled frames
    instead of an error. Request words are validated to ints in 0..255.
    Frames are copied on the way in and out so that mutating a caller's list
    cannot change a scripted response or a recorded call.
    """

    def __init__(
        self,
        responses: Optional[list[list[int]]] = None,
        default: Optional[list[int]] = None,
        strict: bool = True,
    ) -> None:
        """
        Build a scripted transport.

        :param responses: Response frames consumed FIFO; each frame must have
            the same length as the request that consumes it.
        :param default: Frame returned once `responses` is exhausted; when
            omitted, an exhausted queue follows `strict`.
        :param strict: When True an empty queue with no `default` raises
            `TransportError`; when False it returns a zero-filled frame.
        """
        self._responses = (
            [list(frame) for frame in responses] if responses is not None else []
        )
        self._default = list(default) if default is not None else None
        self._strict = strict
        self.calls: list[list[int]] = []
        self._closed = False

    @property
    def closed(self) -> bool:
        """Return True once the transport has been closed."""
        return self._closed

    def queue(self, *responses: list[int]) -> None:
        """Append scripted response frames."""
        self._responses.extend(list(frame) for frame in responses)

    def transfer(self, tx: Sequence[int]) -> list[int]:
        """Return the next scripted frame for `tx`.

        Request words must be ints in 0..255; a malformed word raises
        `ValueError` before the call is recorded. A frame that fails validation
        stays at the head of the queue and is not recorded as a call, so the
        caller can retry with a matching request.

        :param tx: Request frame.
        :return: Response frame of the same length.
        :raises TransportClosed: If the transport is closed.
        :raises ValueError: If a request word is not an int in 0..255.
        :raises TransportError: If no response is available in strict mode or
            the scripted response length does not match the request.
        """
        if self._closed:
            raise TransportClosed("FakeSpiTransport is closed")
        frame = list(tx)
        for word in frame:
            if not isinstance(word, int) or not 0 <= word <= 0xFF:
                raise ValueError(
                    f"SPI frame words must be ints in the range 0..255, got {word!r}"
                )
        if self._responses:
            rx = list(self._responses[0])
            from_queue = True
        elif self._default is not None:
            rx = list(self._default)
            from_queue = False
        elif self._strict:
            raise TransportError("FakeSpiTransport has no scripted response")
        else:
            self.calls.append(frame)
            return [0] * len(frame)
        if len(rx) != len(frame):
            raise TransportError(
                f"Response length {len(rx)} does not match request length {len(frame)}"
            )
        if from_queue:
            self._responses.pop(0)
        self.calls.append(frame)
        return rx

    def close(self) -> None:
        """Close the transport. Repeated calls have no effect."""
        self._closed = True
