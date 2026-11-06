# BDPotentiometer Multi-Bus Transport — Full Implementation Plan

All line anchors are against the current tree. No code is modified by this document.

---

## 0. Ground truth used by this plan

- `SpiDigitalWiper.__init__` positional order: `potentiometer, spi=None, max_value=128, invert=False, **kwargs` — `digital_wiper.py:204-211`.
- Hard gate: `isinstance(spi, SPI)` — `digital_wiper.py:213`, setter `digital_wiper.py:229`.
- Setter bug: assign then unconditional `self.__spi = None` — `digital_wiper.py:227-232`.
- Deepcopy key hack: `if "_spi" in key` — `digital_wiper.py:234-242`.
- `MCP4xxxWiper` gate and calls — `mcp4xxx.py:134-150`.
- `MCP4xxx(SPIDevice)` and SPI kwargs — `mcp4xxx.py:153-159`; kwargs set is exactly `{"channel","port","device","clock_pin","mosi_pin","miso_pin","select_pin"}`.
- Device-level transfers — `mcp4xxx.py:171,183,207-208`.
- Chip wiring — `mcp4xx1.py:10-20`, `mcp4xx2.py:10-18`.
- Channel deepcopy — `digital_potentiometer.py:57-65`.
- Public exports — `__init__.py:8-17`.
- Python `>=3.9`, `gpiozero>=1.6.2`, pytest pythonpath `src` — `pyproject.toml:19-22,44-47`.
- Optional extras currently are `dev`, `test`, `lint` — `pyproject.toml:29-32`. `spidev` is **not** a dependency today; Phase 1b adds it as an optional extra.
- Test runner: `pytest` — `.github/workflows/python-package.yml:40-42`, `tox.ini:25-31`.

---

## Phase 1 — Transport core package and fake transport

**Dependencies:** none. Independently mergeable; no production module consumes it yet.

### Files to create

| Path | Purpose |
|---|---|
| `src/BDPotentiometer/transport/__init__.py` | Export `SpiTransport`, `I2cTransport`, `TransportError`, `TransportClosed`, `is_spi_transport`, `FakeSpiTransport`. Do **not** eagerly import the gpiozero adapter here. |
| `src/BDPotentiometer/transport/base.py` | Protocols, exceptions, structural check helper. |
| `src/BDPotentiometer/transport/fake.py` | `FakeSpiTransport` test double. |

### Exact API

```python
# transport/base.py
from typing import Protocol, Sequence, runtime_checkable


class TransportError(OSError):
    """Raised when a bus transaction fails."""


class TransportClosed(TransportError):
    """Raised when a transaction is attempted after close()."""


@runtime_checkable
class SpiTransport(Protocol):
    def transfer(self, tx: Sequence[int]) -> list[int]: ...
    def close(self) -> None: ...


@runtime_checkable
class I2cTransport(Protocol):
    def write(self, data: Sequence[int]) -> None: ...
    def read(self, nbytes: int) -> bytes: ...
    def write_read(self, tx: Sequence[int], nbytes: int) -> bytes: ...
    def close(self) -> None: ...


def is_spi_transport(obj: object) -> bool:
    """Structural check: object can perform full-duplex SPI transfers."""
    return callable(getattr(obj, "transfer", None))
```

`is_spi_transport` is deliberately weaker than `isinstance(obj, SpiTransport)`: Python 3.9 `runtime_checkable` verifies method presence, and older gpiozero objects may not expose every method. `close` stays part of the documented contract but is not a hard admission gate.

### `FakeSpiTransport` specification

```python
class FakeSpiTransport:
    def __init__(
        self,
        responses: list[list[int]] | None = None,
        default: list[int] | None = None,
        strict: bool = True,
    ) -> None: ...

    calls: list[list[int]]
    closed: bool

    def queue(self, *responses: list[int]) -> None: ...
    def transfer(self, tx: Sequence[int]) -> list[int]: ...
    def close(self) -> None: ...
```

Behavior:

- `responses` is a FIFO of scripted response frames. Each `transfer` pops one frame.
- If the queue is empty and `default` is provided, return `default` (converted to `list`).
- If the queue is empty, `default is None`, and `strict=True`, raise `TransportError("FakeSpiTransport has no scripted response")`.
- If `strict=False`, return `[0] * len(tx)`.
- Record every outbound frame in `calls` as a plain `list[int]`.
- Validate `len(response) == len(tx)` after conversion; raise `TransportError` on mismatch. This mirrors the MCP4xxx read dependency on `data[1]` (`mcp4xxx.py:149`).
- After `close()`, every `transfer` raises `TransportClosed`.
- `close()` is idempotent and sets `closed = True`.
- No locking, no async, no retries.

### Behavior preservation

No existing module imports `transport`; the public API and runtime behavior are untouched.

### Verification

New tests:

- `tests/transport/test_spi_transport_protocol.py`
  - `is_spi_transport(FakeSpiTransport())` is `True`.
  - `is_spi_transport(object())` is `False`.
  - `isinstance(FakeSpiTransport(), SpiTransport)` is `True`.
- `tests/transport/test_fake_spi_transport.py`
  - queues responses and asserts `calls` recording;
  - asserts FIFO order;
  - asserts `default` fallback;
  - asserts strict missing-response `TransportError`;
  - asserts length mismatch `TransportError`;
  - asserts `TransportClosed` after `close()`;
  - asserts idempotent `close()`.

Commands:

```bash
pytest tests/transport -q
pytest -q                     # full suite must remain green
```

Pass condition: new tests pass; full suite exits 0 with no new skips.

---

## Phase 1b — `SpiDevTransport` adapter

**Dependencies:** Phase 1 only (protocols, exceptions). Does not depend on Phase 2/3/4 or on the gpiozero migration. Independently mergeable; no existing module consumes it.

**Why this phase exists:** the original requirement was "a standard SPI backend; currently there is only gpiozero." gpiozero's hardware-SPI path itself wraps the kernel spidev interface. `SpiDevTransport` exposes that standard backend directly, without gpiozero's pin-factory/device layer, for users who want plain Linux SPI. It is **opt-in**: `GpiozeroSpiTransport` remains the default when `device=/port=/*_pin` kwargs are used, while `SpiDevTransport` is the explicit standard-SPI path. Because spidev's hardware SPI is the same interface gpiozero already wraps, transfer behavior is equivalent; only the Python layer differs.

### Files to create/modify

| Path | Purpose |
|---|---|
| `src/BDPotentiometer/transport/spidev_spi.py` | New `SpiDevTransport` adapter. |
| `src/BDPotentiometer/transport/__init__.py` | Export `SpiDevTransport`. Direct export is safe because the module imports `spidev` lazily. |
| `pyproject.toml` | Add optional extra `spi = ["spidev>=3.6"]` under `[project.optional-dependencies]` (`pyproject.toml:29-32`). Keep `gpiozero>=1.6.2` in core `dependencies` (`pyproject.toml:20-22`). |

### Exact API

```python
# transport/spidev_spi.py
from typing import Sequence


class SpiDevTransport:
    def __init__(
        self,
        bus: int = 0,
        device: int = 0,
        max_speed_hz: int = 500_000,
        mode: int = 0,
        bits_per_word: int = 8,
        lsbfirst: bool = False,
    ) -> None: ...

    @property
    def raw(self):
        """Return the underlying spidev.SpiDev object."""

    @property
    def closed(self) -> bool: ...

    def transfer(self, tx: Sequence[int]) -> list[int]: ...

    def close(self) -> None: ...
```

Lazy import helper:

```python
def _load_spidev():
    try:
        from spidev import SpiDev
    except ImportError as exc:
        raise ImportError(
            "SpiDevTransport requires the optional 'spidev' package. "
            "Install it with: pip install 'BDPotentiometer[spi]'"
        ) from exc
    return SpiDev
```

Construction rules:

- `__init__` calls `_load_spidev()`, instantiates `SpiDev()`, calls `.open(bus, device)`, then applies `max_speed_hz`, `mode`, `bits_per_word`, `lsbfirst`, and `cshigh = False`.
- If `open()` fails (`ENOENT`, `EPERM`), wrap and re-raise as `TransportError` naming `/dev/spidev<bus>.<device>`, the `spi` group requirement, and `dtparam=spi=on`. Do not swallow or retry.
- `transfer(tx)`:
  1. raise `TransportClosed` if closed;
  2. `tx = list(tx)`;
  3. `rx = list(self._spi.xfer2(tx))` — **`xfer2`, never `xfer`**;
  4. raise `TransportError` if `len(rx) != len(tx)`;
  5. return `rx`.
- `xfer2` keeps CS asserted for the whole transaction. `xfer` deasserts CS between 8-bit words and would break the MCP4xxx 16-bit command+data word (`mcp4xxx.py:139,147`).
- `close()` is idempotent, sets `_closed`, calls `self._spi.close()`.
- `.raw` returns the underlying `spidev.SpiDev`; `.closed` reflects the flag.
- No `shared=True` equivalent: `bus`/`device` select `/dev/spidev<bus>.<device>`. Two chips on CE0/CE1 are two independent instances (`device=0`, `device=1`). There is no multi-device handle to share.

### Selection semantics

- `MCP4231(r_ab=10e3, device=0)` continues to build `GpiozeroSpiTransport` (Phase 4). Default path, unchanged.
- `MCP4231(r_ab=10e3, transport=SpiDevTransport(bus=0, device=0))` is the explicit standard-SPI path.
- No auto-selection and no eager `spidev` import: the core install stays free of spidev, and `import BDPotentiometer.transport` must work without it.
- Both transports satisfy `SpiTransport`; the chip codec does not know which one is in use.

### Packaging

```toml
[project.optional-dependencies]
dev = ["gpiozero>=1.6.2", "numpy"]
test = ["flake8", "pytest", "numpy"]
lint = ["pylint"]
spi = ["spidev>=3.6"]
```

Runtime requirements (Linux only), documented in the adapter docstring:

- kernel SPI enabled, e.g. `dtparam=spi=on` in `/boot/firmware/config.txt` (or the older `/boot/config.txt`);
- `/dev/spidev<bus>.<device>` present;
- the user is in the `spi` group (or runs as root).

Do not add a startup probe that imports spidev. Missing hardware must fail only when `SpiDevTransport` is actually constructed.

### Behavior preservation

- No existing module imports `transport.spidev_spi`; the core install and the gpiozero path are unchanged.
- `import BDPotentiometer.transport` must succeed without spidev installed.
- `pyproject.toml` gains an optional extra only; `gpiozero` remains a hard dependency and `pip install BDPotentiometer` installs nothing new.

### Verification

Unit tests, no spidev and no hardware:

`tests/transport/test_spidev_spi_transport.py`

Stub module pattern:

```python
import sys
import types
from unittest import mock


class _StubSpiDev:
    return_len = None

    def __init__(self):
        self.open_args = None
        self.calls = []
        self.closed = False

    def open(self, bus, device):
        self.open_args = (bus, device)

    def xfer2(self, tx):
        self.calls.append(("xfer2", list(tx)))
        length = self.return_len if self.return_len is not None else len(tx)
        return [0] * length

    def xfer(self, tx):
        self.calls.append(("xfer", list(tx)))
        raise AssertionError("xfer must not be used")

    def close(self):
        self.closed = True


def _stub_module():
    module = types.ModuleType("spidev")
    module.SpiDev = _StubSpiDev
    return module
```

Assertions:

- `with mock.patch.dict(sys.modules, {"spidev": _stub_module()}): transport = SpiDevTransport(device=1)` → `transport.raw.open_args == (0, 1)`.
- Config applied on the raw object: `max_speed_hz == 500_000`, `mode == 0`, `bits_per_word == 8`, `lsbfirst is False`, `cshigh is False`.
- `transfer([0x0C, 0])` records exactly `("xfer2", [0x0C, 0])`; assert no `("xfer", ...)` entry.
- Length mismatch: set `transport.raw.return_len = 1`, assert `TransportError`.
- `close()` twice; `closed is True`; post-close `transfer` raises `TransportClosed`.
- Missing spidev: `with mock.patch.dict(sys.modules, {"spidev": None}):` constructing `SpiDevTransport()` raises `ImportError` whose message contains `BDPotentiometer[spi]`.
- `.raw` is the stub instance.

End-to-end injection test (execution gate: Phase 4):

```python
# tests/mcp4xxx/test_mcp4xxx_spidev_transport.py
import sys
from unittest import mock

with mock.patch.dict(sys.modules, {"spidev": _stub_module()}):
    transport = SpiDevTransport(bus=0, device=0)
    pot = MCP4231(r_ab=10e3, transport=transport)
    pot.set_value(0, 43)
    assert transport.raw.calls == [("xfer2", [0b00000000, 43])]
```

This file is added to `tests/mcp4xxx/` in Phase 4 verification, because `MCP4231(transport=...)` does not exist before the chip wiring lands. Until then the adapter is exercised directly by `tests/transport/test_spidev_spi_transport.py`.

Commands:

```bash
pytest tests/transport/test_spidev_spi_transport.py -q
python -c "import BDPotentiometer.transport"   # must not require spidev
pytest -q
```

Pass condition: adapter tests pass in an environment without spidev installed; `import BDPotentiometer.transport` succeeds; full suite green. The gated end-to-end test passes once Phase 4 lands.

---

## Phase 2 — Fix the `spi` setter regression

**Dependencies:** none. May land before or after Phase 1; keep it a separate commit.

### File to modify

`src/BDPotentiometer/digital_wiper.py:227-232`.

Current defect:

```python
@spi.setter
def spi(self, spi):
    if isinstance(spi, SPI):
        self.__spi = spi
    self.__spi = None          # always clears
```

New behavior before the Phase 3 rewrite:

```python
@spi.setter
def spi(self, spi):
    self.__spi = spi if isinstance(spi, SPI) else None
    self.logger.debug("SPI interface set to %s", self.__spi)
```

This preserves the final `None` state for invalid input and makes the valid branch effective. Phase 3 replaces the body again with transport resolution.

### Behavior preservation

- `SpiDigitalWiper(spi=None)` still yields `.spi is None` (`tests/digital_wiper/test_digital_wiper_constructor_spi.py:21-32`).
- No other public behavior changes.
- Valid `gpiozero.SPI` assignment now actually persists; this is the intended fix.

### Verification

New test: `tests/digital_wiper/test_digital_wiper_spi_setter.py`

- `wiper.spi = None` → `wiper.spi is None`.
- `wiper.spi = object()` → `wiper.spi is None` (invalid input remains non-fatal at this phase).
- Valid-object branch is not constructed from real hardware; it is covered structurally in Phase 3 using `FakeSpiTransport`.

Command:

```bash
pytest tests/digital_wiper/test_digital_wiper_spi_setter.py -q
pytest tests/digital_wiper -q
```

Pass condition: setter test passes; existing wiper tests still pass.

---

## Phase 3 — Migrate `SpiDigitalWiper` and un-gate `MCP4xxxWiper`

**Dependencies:** Phase 1 (protocols, fake), Phase 2 (setter fix). This phase is mergeable while `MCP4xxx` still inherits `SPIDevice`, because the legacy gpiozero object satisfies `is_spi_transport`.

### Files to modify

| Path | Anchors | Change |
|---|---|---|
| `src/BDPotentiometer/digital_wiper.py` | `:5`, `:200-243` | Drop `from gpiozero import SPI`; replace `_spi` storage with `_transport`; add `transport=` kwarg, `transport` property, compat `spi` property; rewrite `__deepcopy__`. |
| `src/BDPotentiometer/mcp4xxx/mcp4xxx.py` | `:114-150` | Add `transport=` kwarg; use `self._require_transport()`; extract pure codec functions; remove `isinstance(self.spi, SPI)`. |
| `src/BDPotentiometer/mcp4xxx/mcp4xxx.py` | `:3-4` | Remove `SPI` import only after all `isinstance` checks are gone; keep file importable at this phase. |

### Exact API

```python
# digital_wiper.py
from .transport.base import SpiTransport, is_spi_transport


class SpiDigitalWiper(DigitalWiper):
    def __init__(
        self,
        potentiometer: Potentiometer,
        spi: Union[SpiTransport, None] = None,
        max_value: int = 128,
        invert: bool = False,
        transport: Union[SpiTransport, None] = None,
        **kwargs,
    ):
        self._transport = self._resolve_transport(
            transport if transport is not None else spi
        )
        super().__init__(
            potentiometer=potentiometer,
            max_value=max_value,
            invert=invert,
            **kwargs,
        )

    @staticmethod
    def _resolve_transport(value):
        if value is None:
            return None
        if is_spi_transport(value):
            return value
        raise TypeError(
            f"Expected an SPI transport with transfer(), got {type(value)}"
        )

    def _require_transport(self) -> SpiTransport:
        if self._transport is None:
            raise ConnectionError("SPI interface not set")
        return self._transport

    @property
    def transport(self) -> Union[SpiTransport, None]:
        return self._transport

    @transport.setter
    def transport(self, value) -> None:
        self._transport = self._resolve_transport(value)
        self.logger.debug("Transport set to %s", self._transport)

    @property
    def spi(self) -> Union[SpiTransport, None]:
        """Backward-compatible accessor. Returns raw gpiozero SPI if wrapped."""
        if self._transport is None:
            return None
        return getattr(self._transport, "raw", self._transport)

    @spi.setter
    def spi(self, value) -> None:
        self.transport = value

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for key, value in self.__dict__.items():
            if key == "_transport":
                setattr(result, key, value)
                continue
            setattr(result, key, deepcopy(value, memo))
        return result
```

`MCP4xxxWiper`:

```python
class MCP4xxxWiper(SpiDigitalWiper):
    def __init__(
        self,
        potentiometer: MCP4xxxPotentiometer,
        spi: Union[SpiTransport, None] = None,
        max_value: int = 128,
        invert: bool = False,
        transport: Union[SpiTransport, None] = None,
        **kwargs,
    ):
        max_value = _coerce_max_value(max_value)
        super().__init__(
            potentiometer=potentiometer,
            spi=spi,
            transport=transport,
            max_value=max_value,
            invert=invert,
            **kwargs,
        )

    def _set_value(self, value: int) -> int:
        value = int(round(clamp(value, 0, self.max_value)))
        value = self.max_value - value if self.invert else value
        self.logger.debug("Setting value to %d", value)
        data = self._require_transport().transfer(
            _encode_wiper_write(self.channel, value)
        )
        _check_write_response(data)
        self.potentiometer.wiper_position = value / self.max_value
        return value

    def _read_value(self):
        data = self._require_transport().transfer(_encode_wiper_read(self.channel))
        return _decode_wiper_read(data)
```

Pure codec functions added in `mcp4xxx.py` (keep existing constants and checkers in place):

```python
def _encode_wiper_write(channel: int, value: int) -> list[int]:
    return [_W_CMD | _CH[channel], value]


def _encode_wiper_read(channel: int) -> list[int]:
    return [_R_CMD | _CH[channel], 0]


def _decode_wiper_read(data: list) -> int:
    _check_read_response(data)
    return data[1]
```

Do **not** move `resistance_list`, `_coerce_max_value`, `_coerce_r_ab`, `_check_write_response`, `_check_read_response`; `tests/mcp4xxx/test_mcp4xxx.py:6-16` imports them from `mcp4xxx.mcp4xxx`.

### Behavior preservation

- `SpiDigitalWiper(spi=None).spi is None` preserved.
- `SpiDigitalWiper` positional second argument remains `spi`.
- `.spi` still returns a gpiozero `SPI` object when the stored object has no `.raw` (the legacy Phase-3 path), so `isinstance(self.spi, SPI)` elsewhere would still work — but the wiper no longer relies on it.
- `ConnectionError("SPI interface not set")` message and type preserved (`mcp4xxx.py:143,150`).
- `_set_value` order of operations preserved: clamp → invert → transfer → `_check_write_response` → update `potentiometer.wiper_position` → return value.
- `_read_value` returns `data[1]` after `_check_read_response`.
- Deepcopy now shares `_transport` by identity instead of matching `"_spi"` substrings. This is required because channels deepcopy the wiper (`digital_potentiometer.py:61`).
- Invalid non-`None` `spi`/`transport` now raises `TypeError` instead of silently becoming `None`. Listed as an intentional change for invalid inputs only.

### Verification

New tests:

- `tests/digital_wiper/test_digital_wiper_transport.py`
  - `SpiDigitalWiper(potentiometer=..., transport=FakeSpiTransport())` stores it; `.transport is fake`; `.spi is fake`.
  - `spi=None` and `transport=None` → `.transport is None`; `.spi is None`.
  - invalid object raises `TypeError`.
  - `SpiDigitalWiper(potentiometer=..., spi=None).transport` is `None`.
- `tests/digital_wiper/test_digital_wiper_deep_copy_transport.py`
  - `deepcopy(wiper).transport is wiper.transport` (identity, not equality).
  - everything else still deep-copied (reuse assertions from `test_digital_wiper_deep_copy_spi.py:37-66`).
- `tests/mcp4xxx/test_mcp4xxx_codec.py`
  - `_encode_wiper_write(0, 43) == [0b00000000, 43]`.
  - `_encode_wiper_write(1, 43) == [0b00010000, 43]`.
  - `_encode_wiper_read(0) == [0b00001100, 0]`.
  - `_encode_wiper_read(1) == [0b00011100, 0]`.
  - `_decode_wiper_read([0, 43]) == 43`.
  - `_decode_wiper_read(None)` raises `ValueError` (delegated to `_check_read_response`).
- Extend `tests/mcp4xxx/test_mcp4xxx.py` only if needed; do not reorder existing imports.

Commands:

```bash
pytest tests/digital_wiper tests/mcp4xxx -q
pytest -q
```

Pass condition: all existing and new tests pass; `test_digital_wiper_constructor_spi.py` and `test_digital_wiper_deep_copy_spi.py` remain green unchanged.

---

## Phase 4 — Adapter, `MCP4xxx` de-inheritance, chip wiring

**Dependencies:** Phase 1 and Phase 3. This is the highest-risk phase; keep it one atomic commit.

### Files to create/modify

| Path | Anchors | Change |
|---|---|---|
| `src/BDPotentiometer/transport/gpiozero_spi.py` | new | `GpiozeroSpiTransport` adapter. |
| `src/BDPotentiometer/transport/__init__.py` | — | Export `GpiozeroSpiTransport` only if eager import is acceptable; otherwise leave it module-local. |
| `src/BDPotentiometer/mcp4xxx/mcp4xxx.py` | `:3-4`, `:153-224` | Remove `SPIDevice` inheritance; resolve/build transport; replace `self._spi.transfer` at `:171,183,207-208`; add `.transport`, `.spi`, `.close()`. |
| `src/BDPotentiometer/mcp4xx1.py` | `:10-20` | Pass `transport=self._transport`; filter `spi`/`transport` before passing `**kwargs`. |
| `src/BDPotentiometer/mcp4xx2.py` | `:10-18` | Pass `transport=self._transport`; stop using `self._spi`. |

### Exact API

```python
# transport/gpiozero_spi.py
from typing import Sequence
from .base import TransportError, TransportClosed


class GpiozeroSpiTransport:
    _SPI_ARGS = (
        "channel", "port", "device",
        "clock_pin", "mosi_pin", "miso_pin", "select_pin",
    )

    def __init__(self, spi=None, **spi_args) -> None:
        # spi: an already-constructed gpiozero SPI, or a compatible object.
        # spi_args: same kwargs the old MCP4xxx(SPIDevice) constructor accepted.
        ...

    @property
    def raw(self):
        """Return the underlying gpiozero SPI object."""

    @property
    def closed(self) -> bool: ...

    def transfer(self, tx: Sequence[int]) -> list[int]:
        # 1. raise TransportClosed if closed
        # 2. tx = list(tx)
        # 3. rx = list(underlying.transfer(tx))
        # 4. if len(rx) != len(tx): raise TransportError
        # 5. return rx

    def close(self) -> None: ...
```

Construction rule: when `spi is None`, replicate the proven path from `mcp4xxx.py:156-159` exactly. Use a private handle:

```python
class _GpiozeroSpiHandle(SPIDevice):
    def __init__(self, **spi_args) -> None:
        super().__init__(shared=True, **spi_args)
```

then expose `self._handle._spi` as `raw` and delegate `transfer`. This preserves `shared=True` and the `SPI` kwargs set without guessing gpiozero constructor signatures. When `spi` is provided, wrap it directly and do not create a handle.

`MCP4xxx` new shape:

```python
class MCP4xxx:
    _SPI_ARGS = GpiozeroSpiTransport._SPI_ARGS

    def __init__(self, transport=None, spi=None, **kwargs) -> None:
        if transport is None and spi is not None:
            transport = spi
        if transport is None:
            spi_args = {k: kwargs[k] for k in self._SPI_ARGS if k in kwargs}
            if spi_args:
                transport = GpiozeroSpiTransport(**spi_args)
        if transport is not None and not is_spi_transport(transport):
            raise TypeError(...)
        self._transport = transport

    @property
    def transport(self):
        return self._transport

    @property
    def spi(self):
        if self._transport is None:
            return None
        return getattr(self._transport, "raw", self._transport)

    @property
    def closed(self) -> bool:
        return bool(getattr(self._transport, "closed", self._transport is None))

    def close(self) -> None:
        if self._transport is not None:
            self._transport.close()

    def _require_transport(self):
        if self._transport is None:
            raise ConnectionError("SPI interface not set")
        return self._transport
```

Replace:

- `mcp4xxx.py:171` → `self._require_transport().transfer([_R_CMD | _STATUS, 0])`
- `mcp4xxx.py:183` → `self._require_transport().transfer([_R_CMD | _TCON, 0])`
- `mcp4xxx.py:207-208` → `self._require_transport().transfer(...)` twice.

`MCP4xxx.__init__` must **not** call `super().__init__(shared=True, ...)`; after removing `SPIDevice`, `super()` resolves to `object` and would raise.

`MCP4xx1.__init__` (`mcp4xx1.py:10-20`):

```python
def __init__(self, r_ab=10e3, max_value=128, channels=1, **kwargs):
    MCP4xxx.__init__(self, **kwargs)
    pot_kwargs = {
        k: v for k, v in kwargs.items() if k not in ("transport", "spi")
    }
    potentiometer = MCP4xxxPotentiometer(r_ab, **pot_kwargs)
    wiper = MCP4xxxWiper(
        potentiometer=potentiometer,
        transport=self._transport,
        max_value=max_value,
        **pot_kwargs,
    )
    DigitalPotentiometerDevice.__init__(
        self, wiper=wiper, channels=channels, **pot_kwargs
    )
```

`MCP4xx2.__init__` (`mcp4xx2.py:10-18`):

```python
def __init__(self, r_ab=10e3, max_value=128, channels=1, **kwargs):
    MCP4xxx.__init__(self, **kwargs)
    potentiometer = MCP4xxxPotentiometer(r_ab, rheostat=True)
    wiper = MCP4xxxWiper(
        potentiometer=potentiometer,
        transport=self._transport,
        max_value=max_value,
    )
    DigitalPotentiometerDevice.__init__(self, wiper=wiper, channels=channels)
```

Import `GpiozeroSpiTransport` at module level in `mcp4xxx.py` for patchability. gpiozero remains a declared dependency (`pyproject.toml:20-22`), so this does not change install requirements.

### Behavior preservation

- `MCP4231(r_ab=10e3, device=0)` still constructs: `device` stays in `kwargs`, `MCP4xxx.__init__` builds `GpiozeroSpiTransport(device=0)`.
- `.channels[i].value`, `.value`, `.set_value`, `.get_value` unchanged (`digital_potentiometer.py:129-163`).
- `.spi` on wiper and device returns the raw gpiozero SPI object when using the gpiozero adapter.
- `.close()` exists and delegates to the transport.
- `MCP4231(spi=<gpiozero SPI>)` now works; previously the explicit `spi=self._spi` plus `**kwargs` collision in `mcp4xx1.py:16` made it fail.
- `MCP4231(transport=<anything with transfer>)` is new.
- `MCP4231(r_ab=10e3, device=0)` keeps `GpiozeroSpiTransport` as the **default**. `SpiDevTransport` is never auto-selected; it is used only when the caller injects it explicitly with `transport=SpiDevTransport(...)`.
- `MCP4231(transport=SpiDevTransport(...))` and `MCP4231(transport=GpiozeroSpiTransport(...))` are equivalent at the codec layer; both satisfy `SpiTransport`.
- `MCP4xxx` is **no longer** a `gpiozero.SPIDevice`; this is intentional. Code using gpiozero device internals (`_spi`, `pin_factory`, `isinstance(..., SPIDevice)`) breaks.
- `fix_gpiozero_dual_cs_spi()` remains exported and functional; dual-CS is now also achievable by creating two transports with distinct `device=`.

### Verification

New tests:

- `tests/transport/test_gpiozero_spi_transport.py`
  - Passe a stub with `.transfer(tx)` and `.close()`; assert delegation and call recording.
  - Assert length mismatch raises `TransportError`.
  - Assert `TransportClosed` after `close()`.
  - No hardware: never construct the default gpiozero handle.
- `tests/mcp4xxx/test_mcp4xxx_transport.py`
  - `fake = FakeSpiTransport(responses=[[0, 43], [0, 0]])`
  - `pot = MCP4231(r_ab=10e3, transport=fake)`.
  - `pot.set_value(0, 43)`; assert `fake.calls[0] == [0b00000000, 43]`.
  - `pot.get_value(0)`; assert submitted `[0b00001100, 0]` and returned `43`.
  - channel 1: assert `[0b00010000, ...]` / `[0b00011100, 0]`.
  - `pot.transport is fake`; `pot.channels[0].transport is fake`; both channels share identity.
  - `pot.close()` → `fake.closed is True`; subsequent use raises `TransportClosed`.
- `tests/mcp4xxx/test_chip_constructor_wiring.py`
  - Patch `BDPotentiometer.mcp4xxx.mcp4xxx.GpiozeroSpiTransport`.
  - `MCP4231(r_ab=10e3, device=0)`; assert called once with `device=0`.
  - `MCP4231(r_ab=10e3, port=0, device=1, clock_pin=11)`; assert all kwargs forwarded.
  - `MCP4231(r_ab=10e3, spi=<stub>)`; assert adapter created with `spi=stub` or used directly (whichever branch the implementation chooses; assert the resulting `pot.transport` is the stub or wraps it).
- `tests/mcp4xxx/test_mcp4xxx_spidev_transport.py` (deferred from Phase 1b)
  - Patch `sys.modules["spidev"]` with the stub module from Phase 1b.
  - `SpiDevTransport(bus=0, device=0)`, then `MCP4231(r_ab=10e3, transport=transport)`.
  - `set_value(0, 43)`; assert `transport.raw.calls == [("xfer2", [0b00000000, 43])]` and that `xfer` was never called.

Commands:

```bash
pytest tests/transport tests/mcp4xxx -q
pytest tests/digital_wiper tests/digital_potentiometer -q
pytest -q
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

Pass condition: full suite green; adapter tests pass without hardware; constructor wiring asserts `device=0` path.

---

## Phase 5 — Backward-compatibility hardening and exports

**Dependencies:** Phase 4.

### Files to modify

| Path | Anchors | Change |
|---|---|---|
| `src/BDPotentiometer/__init__.py` | `:8-17` | Export `transport` symbols (`SpiTransport`, `I2cTransport`, `TransportError`, `TransportClosed`, `FakeSpiTransport`, `SpiDevTransport`), keeping existing exports and the `fix_gpiozero_dual_cs_spi` try/except block unchanged. |
| `src/BDPotentiometer/transport/__init__.py` | — | Finalize exports; decide whether `GpiozeroSpiTransport` is exported. If exported, it pulls gpiozero at import; since gpiozero stays a hard dependency, this is acceptable. `SpiDevTransport` is always safe to export because its spidev import is lazy. |
| `docs`/docstrings | minimal | One-line notes on `MCP4xxx` no longer being `SPIDevice` and on `.spi` returning raw gpiozero. No README rewrite. |

### Behavior preservation

- `fix_gpiozero_dual_cs_spi` behavior and import path preserved (`__gpiozero_helpers.py:11-77`, exported at `__init__.py:12-17`).
- `__version__` unchanged.
- No change to `DigitalPotentiometerDevice`, `Potentiometer`, or `DigitalWiper`.

### Verification

New test: `tests/test_backward_compatibility.py`

- Assert public symbols importable: `Potentiometer`, `DigitalWiper`, `SpiDigitalWiper`, `DigitalPotentiometerDevice`, `fix_gpiozero_dual_cs_spi`.
- Assert `MCP4231`, `MCP4251`, `MCP4232` importable from `BDPotentiometer.mcp4xxx`.
- Assert `hasattr(MCP4231, "close")`, `hasattr(MCP4231, "spi")`, `hasattr(SpiDigitalWiper, "transport")`.
- Assert `SpiDevTransport` is importable from `BDPotentiometer.transport` without importing `spidev` as a side effect (`"spidev" not in sys.modules` before construction).
- Assert `MCP4xxx` is not a `gpiozero.SPIDevice` only if gpiozero is importable; otherwise skip. This documents the intentional change without making the test fragile on non-Pi hosts.
- Assert `fix_gpiozero_dual_cs_spi` is callable.

Commands:

```bash
pytest tests/test_backward_compatibility.py -q
pytest -q
```

Pass condition: full suite green; all compatibility assertions pass.

---

## Phase 6 — CI verification and cleanup

**Dependencies:** Phases 1–5, including the additive Phase 1b.

### Actions

- Run the exact CI commands from `.github/workflows/python-package.yml:31-42`.
- Run `mypy src` if the project expects it (`tox.ini:19-23`); fix only new errors introduced by transport typing.
- Run `pylint src tests examples` (`tox.ini:14-17`); add narrow `# pylint: disable=too-few-public-methods` on Protocol classes if needed, matching existing style (`mcp4xxx.py:22`).
- Do not modify examples (`examples/mcp4231.py` already references methods not present in current code — out of scope).

### Verification

```bash
pytest -q
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
mypy src
pylint src tests examples
```

Pass condition: `pytest` exit 0; flake8 hard checks exit 0; mypy/pylint no new failures relative to baseline. Record the baseline before Phase 1 so pre-existing lint/type issues are not attributed to this change.

---

## 7. Test plan summary

### Pure codec tests

`tests/mcp4xxx/test_mcp4xxx_codec.py` — encode/decode commands and TCON helpers without any transport.

### Fake-transport contract tests

`tests/transport/test_spi_transport_protocol.py` and `tests/transport/test_fake_spi_transport.py` — structural admission, FIFO scripting, recording, default/strict behavior, length validation, close/`TransportClosed`.

### spidev adapter tests

`tests/transport/test_spidev_spi_transport.py` — `sys.modules["spidev"]` stub, `xfer2` used (never `xfer`), config applied, `bus`/`device` open args, length validation, close/`TransportClosed`, missing-package `ImportError` naming `BDPotentiometer[spi]`. No spidev install and no hardware.

`tests/mcp4xxx/test_mcp4xxx_spidev_transport.py` — gated on Phase 4: `MCP4231(transport=SpiDevTransport(...))` with the spidev module stubbed, proving the injection path and exact wire bytes.

### Device-level tests

`tests/mcp4xxx/test_mcp4xxx_transport.py` — `MCP4231(transport=FakeSpiTransport(...))`, channel 0/1 command bytes, read/write round trip, close semantics, `device=0` wiring via patch.

### Deepcopy / transport-sharing identity

`tests/digital_wiper/test_digital_wiper_deep_copy_transport.py` and `tests/digital_potentiometer/test_digital_potentiometer_transport_sharing.py` — `assertIs(copy.transport, original.transport)` and all channels share the same object.

### Setter regression

`tests/digital_wiper/test_digital_wiper_spi_setter.py` — valid assignment persists, invalid assignment yields `None`, no unconditional clear.

### Existing suite

Run `pytest -q` after every phase. Key files that must remain unchanged and green:

- `tests/digital_wiper/test_digital_wiper_constructor_spi.py`
- `tests/digital_wiper/test_digital_wiper_deep_copy_spi.py`
- `tests/digital_wiper/test_digital_wiper_value.py`
- `tests/digital_potentiometer/test_digital_potentiometer.py`
- `tests/mcp4xxx/test_mcp4xxx.py`

---

## 8. Backward-compatibility matrix

| Symbol / usage | Status | Notes |
|---|---|---|
| `Potentiometer`, `DigitalWiper` | Preserved | No changes. |
| `SpiDigitalWiper` | Preserved | Same name, same positional `spi` argument; new optional `transport=`. |
| `SpiDigitalWiper.spi` | Preserved (compat accessor) | Returns raw gpiozero SPI if the transport exposes `.raw`, else the transport itself. |
| `SpiDigitalWiper.transport` | New | Canonical accessor. |
| `SpiDigitalWiper(spi=<invalid>)` | Intentionally changed | Previously silently `None`; now `TypeError`. Valid inputs unchanged. |
| `SpiDigitalWiper.__deepcopy__` | Preserved semantics | Still deep-copies everything except the bus handle; now identity-shares `_transport`. |
| `DigitalPotentiometerDevice` | Preserved | No changes; channels still deepcopy the wiper. |
| `MCP4xxx` as `gpiozero.SPIDevice` | Intentionally changed | No longer a subclass. `.close()`, `.spi`, `.closed` shimmed. gpiozero internals break. |
| `MCP4231(r_ab=10e3, device=0)` | Preserved | Builds `GpiozeroSpiTransport(device=0)`. |
| `MCP4231(r_ab=10e3)` (no SPI kwargs) | Preserved | Builds a default `GpiozeroSpiTransport()`; gpiozero opens its default SPI device as before. |
| `MCP4231(spi=<gpiozero SPI>)` | Preserved, now functional | Previously collided in `mcp4xx1.py:16`. |
| `MCP4231(transport=<fake>)` | New | Primary test path. |
| `MCP4231(transport=SpiDevTransport(...))` | New (opt-in) | Explicit standard-SPI path; no auto-selection. Requires `pip install 'BDPotentiometer[spi]'` at runtime. |
| `SpiDevTransport` | New | Public class in `BDPotentiometer.transport`; `bus`/`device` map to `/dev/spidev<bus>.<device>`; `xfer2` only. |
| spidev dependency | New optional extra | `spi = ["spidev>=3.6"]`; core install and `gpiozero` hard dependency unchanged; `import BDPotentiometer.transport` must not import spidev. |
| `MCP4231(r_ab=..., port=..., channel=..., clock_pin=..., mosi_pin=..., miso_pin=..., select_pin=...)` | Preserved | Same `_SPI_ARGS` set (`mcp4xxx.py:157`); still builds `GpiozeroSpiTransport` by default. |
| `.channels[i].value`, `.set_value`, `.get_value`, `.value` | Preserved | No changes to `digital_potentiometer.py`. |
| `MCP4xxxWiper.spi` | Preserved | Same compat accessor. |
| `resistance_list`, `_coerce_max_value`, `_coerce_r_ab`, `_check_write_response`, `_check_read_response` | Preserved | Stay in `mcp4xxx.mcp4xxx`; existing tests import them from there. |
| `fix_gpiozero_dual_cs_spi` | Preserved | Still exported and callable; no removal, no behavior change. |
| `__version__` | Preserved | Unchanged. |
| Package import without gpiozero | Improved partially | `digital_wiper` drops the `SPI` import; `mcp4xxx` still imports gpiozero because it stays a declared dependency. |
| Package import without spidev | Preserved | `SpiDevTransport` imports `spidev` lazily; `import BDPotentiometer.transport` works on a clean install. |
| `I2cTransport` Protocol | New (unused) | Available for future I2C chips; no I2C chip implementation in scope. |

---

## 9. Risk register

| Risk | Impact | Mitigation | Containment / rollback |
|---|---|---|---|
| Removing `SPIDevice` inheritance changes MRO and `super()` behavior | `MCP4xxx.__init__` calling `super().__init__(shared=True, ...)` would fail against `object` | Rewrite `__init__` to build the transport directly; never call `super()` with args | Phase 4 is one atomic commit; revert it to restore `SPIDevice` path |
| Users rely on gpiozero device APIs (`.pin_factory`, `.closed`, `isinstance(..., SPIDevice)`) | Breakage outside documented API | Shim `.close()`, `.closed`, `.spi`; document the intentional change | Revert Phase 4 only; Phases 1–3 remain valid |
| Bus sharing / CS framing changes | Two channels could open separate SPI handles or lose `shared=True` | Adapter replicates `SPIDevice(shared=True, ...)` verbatim; deepcopy identity test; chip constructors pass one `_transport` | Keep adapter construction logic isolated in `transport/gpiozero_spi.py`; revert that file plus Phase 4 wiring |
| Thread safety | Concurrent access corrupts transactions | Document transports as not thread-safe; no locks added | Out of scope; users serialize externally |
| Import-time gpiozero coupling | Importing the package on a non-Pi host could fail | gpiozero imports cleanly on Linux; adapter imports remain localized; `digital_wiper` no longer imports `SPI` | If import breaks, move adapter import inside the default-construction branch |
| gpiozero version drift (`>=1.6.2`) | `SPI` constructor or `SPIDevice` behavior changes | Adapter uses only the existing `SPIDevice(shared=True, **spi_kwargs)` path already proven in `mcp4xxx.py:156-159`; no new gpiozero APIs | Pin adapter to that path; revert adapter commit independently |
| spidev not installed | `SpiDevTransport()` fails at runtime | Lazy import raises `ImportError` naming `BDPotentiometer[spi]`; test patches `sys.modules["spidev"] = None`; core import never touches spidev | Phase 1b is additive; users on the gpiozero path are unaffected |
| Kernel SPI disabled or missing device node | `open()` raises `ENOENT` even with spidev installed | Wrap in `TransportError` naming `/dev/spidev<bus>.<device>` and `dtparam=spi=on`; document `/boot/firmware/config.txt` | Do not retry; construction failure is explicit and isolated to the opt-in path |
| Permissions (`EPERM`, user not in `spi` group) | `open()` fails on a correctly configured Pi | Wrap `PermissionError` in `TransportError` with the `spi` group hint; document `sudo usermod -aG spi $USER` | Same containment as above; no fallback to gpiozero |
| `xfer` vs `xfer2` misuse | CS deasserts between the two 8-bit words, corrupting the MCP4xxx 16-bit transaction | `SpiDevTransport.transfer` calls `xfer2` only; the stub test raises if `xfer` is called | Adapter-local bug; revert Phase 1b without touching other phases |
| SPI mode/clock mismatch | Wrong mode or excessive `max_speed_hz` yields garbled reads | Explicit constructor args (`max_speed_hz=500_000`, `mode=0`, `bits_per_word=8`, `lsbfirst=False`, `cshigh=False`); test asserts all are applied; document datasheet limits | User can override per instance; no global defaults changed |
| spidev version drift (`>=3.6`) | API or attribute behavior changes | Adapter uses only `SpiDev()`, `open`, `xfer2`, `close`, and the standard config attributes; no private spidev APIs | Pin extra to `>=3.6`; adapter is isolated in one module |
| Setter fix changes behavior for valid SPI assignment | Previously assignment never persisted; now it does | Intended fix; regression test documents both valid and invalid branches | Phase 2 is a standalone commit |
| `runtime_checkable` only checks presence in Python 3.9 | Invalid objects could pass if they have a `transfer` attribute | Use `is_spi_transport` checking callability; transfer errors surface at call time | Helper isolated in `transport/base.py` |
| `**kwargs` leakage (`transport`, `spi`, `device`) into `Potentiometer`/`DigitalPotentiometerDevice` | Silent wrong attributes or duplicate keyword `spi` | Filter `transport`/`spi` in chip constructors; keep `device`/pin kwargs out of wiper where possible | Covered by constructor-wiring test |
| Fake transport strictness makes tests brittle | Tests fail on unexpected extra reads | Provide `default=` and `strict=False`; record calls for assertions | Fake is test-only |

---

## 10. Out of scope

- I2C chip family implementation (MCP4551/MCP4561 codecs, `mcp45xx` package).
- Bus registry / plugin discovery / string-based device opening.
- Async, non-blocking, or callback-based transports.
- Internal locking, retries, or thread-safety guarantees.
- smbus2 backend or additional I2C dependencies (`spidev` is now in scope as the optional `spi` extra).
- Making `SpiDevTransport` the default or auto-selecting a backend from device kwargs.
- Removing gpiozero from `pyproject.toml` or making it optional at install time.
- README/docs site rewrite beyond minimal docstrings.
- Fixing stale `examples/mcp4231.py` methods (`set_r_lim`, `set_voltage_in`, etc. are not in current source).
- Removing or deprecating `fix_gpiozero_dual_cs_spi`.
- Changing `DigitalPotentiometerDevice` or `Potentiometer` math.

---

## 11. Effort estimates

| Phase | Scope | Estimate |
|---|---|---|
| 1 | Transport core + `FakeSpiTransport` + tests | 0.5 day |
| 1b | `SpiDevTransport`, `spi` extra, stubbed-module tests | 0.5–1 day |
| 2 | Setter bug fix + regression test | 0.25 day |
| 3 | `SpiDigitalWiper` + `MCP4xxxWiper` migration, codec extraction, deepcopy | 1–1.5 days |
| 4 | gpiozero adapter, `MCP4xxx` de-inheritance, chip wiring, device tests | 2–3 days |
| 5 | Compatibility exports and assertions | 0.5–1 day |
| 6 | CI verification, mypy/pylint cleanup | 0.5–1 day |
| **Total** | | **5–8 days** |

---

## 12. Atomic TODO checklist

Format: `path: <action> for <scenario> — verify by <check>`

1. `src/BDPotentiometer/transport/base.py`: create `SpiTransport`, `I2cTransport`, `TransportError`, `TransportClosed`, `is_spi_transport` for all backend typing — verify by `pytest tests/transport/test_spi_transport_protocol.py -q`.
2. `src/BDPotentiometer/transport/fake.py`: implement `FakeSpiTransport` with FIFO responses, `default`, `strict`, `calls`, `closed`, length validation — verify by `pytest tests/transport/test_fake_spi_transport.py -q`.
3. `src/BDPotentiometer/transport/__init__.py`: export core transport symbols without importing the gpiozero adapter — verify by `python -c "import BDPotentiometer.transport"`.
3a. `src/BDPotentiometer/transport/spidev_spi.py`: implement `SpiDevTransport` with lazy spidev import, `open(bus, device)`, config (`max_speed_hz`, `mode`, `bits_per_word`, `lsbfirst`, `cshigh=False`), `xfer2`-only transfer, length validation, idempotent close, `.raw`, `.closed` — verify by `pytest tests/transport/test_spidev_spi_transport.py -q`.
3b. `pyproject.toml:29-32`: add optional extra `spi = ["spidev>=3.6"]` for standard SPI installs while keeping `gpiozero>=1.6.2` in core dependencies — verify by `grep -q 'spidev>=3.6' pyproject.toml`.
3c. `src/BDPotentiometer/transport/__init__.py`: export `SpiDevTransport` without importing spidev at module import time — verify by `python -c "import sys, BDPotentiometer.transport; assert 'spidev' not in sys.modules"`.
3d. `tests/mcp4xxx/test_mcp4xxx_spidev_transport.py`: add the gated end-to-end test using `mock.patch.dict(sys.modules, {"spidev": stub})` and `MCP4231(transport=SpiDevTransport(...))` after Phase 4 — verify by `pytest tests/mcp4xxx/test_mcp4xxx_spidev_transport.py -q`.
4. `src/BDPotentiometer/digital_wiper.py:227-232`: fix `spi` setter to persist valid input and not unconditionally clear — verify by `pytest tests/digital_wiper/test_digital_wiper_spi_setter.py -q`.
5. `src/BDPotentiometer/digital_wiper.py:5`: remove the `gpiozero` `SPI` import for base-package importability — verify by `python -c "import BDPotentiometer"`.
6. `src/BDPotentiometer/digital_wiper.py:204-217`: add `transport=` kwarg and `_resolve_transport` for injected backends — verify by `pytest tests/digital_wiper/test_digital_wiper_transport.py -q`.
7. `src/BDPotentiometer/digital_wiper.py:219-232`: replace `spi` property/setter with `transport` plus compat `spi` accessor for legacy callers — verify by `pytest tests/digital_wiper/test_digital_wiper_constructor_spi.py -q`.
8. `src/BDPotentiometer/digital_wiper.py:234-242`: rewrite `__deepcopy__` to identity-share `_transport` for channel cloning — verify by `pytest tests/digital_wiper/test_digital_wiper_deep_copy_transport.py -q`.
9. `src/BDPotentiometer/mcp4xxx/mcp4xxx.py:98-103`: keep constants; add `_encode_wiper_write`, `_encode_wiper_read`, `_decode_wiper_read` for pure codec tests — verify by `pytest tests/mcp4xxx/test_mcp4xxx_codec.py -q`.
10. `src/BDPotentiometer/mcp4xxx/mcp4xxx.py:114-150`: add `transport=` to `MCP4xxxWiper`; replace `isinstance(self.spi, SPI)` with `_require_transport()` — verify by `pytest tests/mcp4xxx/test_mcp4xxx_codec.py tests/digital_wiper -q`.
11. `src/BDPotentiometer/transport/gpiozero_spi.py`: implement `GpiozeroSpiTransport` wrapping `SPIDevice(shared=True, **spi_kwargs)` for existing hardware — verify by `pytest tests/transport/test_gpiozero_spi_transport.py -q`.
12. `src/BDPotentiometer/mcp4xxx/mcp4xxx.py:153-159`: remove `SPIDevice` inheritance and build/accept a transport for `MCP4xxx` — verify by `pytest tests/mcp4xxx/test_chip_constructor_wiring.py -q`.
13. `src/BDPotentiometer/mcp4xxx/mcp4xxx.py:171,183,207-208`: replace `self._spi.transfer` with `self._require_transport().transfer` for device-level TCON/status — verify by `pytest tests/mcp4xxx/test_mcp4xxx_transport.py -q`.
14. `src/BDPotentiometer/mcp4xxx/mcp4xxx.py:153-224`: add `.transport`, `.spi`, `.closed`, `.close()` compatibility surface — verify by `pytest tests/test_backward_compatibility.py -q`.
15. `src/BDPotentiometer/mcp4xxx/mcp4xx1.py:10-20`: filter `transport`/`spi` from `**kwargs` and pass `transport=self._transport` into the wiper — verify by `pytest tests/mcp4xxx/test_chip_constructor_wiring.py -q`.
16. `src/BDPotentiometer/mcp4xxx/mcp4xx2.py:10-18`: pass `transport=self._transport` and drop `self._spi` for rheostats — verify by `pytest tests/mcp4xxx -q`.
17. `src/BDPotentiometer/__init__.py:8-17`: export transport symbols while preserving the `fix_gpiozero_dual_cs_spi` try/except — verify by `pytest tests/test_backward_compatibility.py -q`.
18. `tests/digital_potentiometer/test_digital_potentiometer_transport_sharing.py`: assert all channels share one transport instance — verify by `pytest tests/digital_potentiometer/test_digital_potentiometer_transport_sharing.py -q`.
19. `tests/mcp4xxx/test_mcp4xxx_transport.py`: assert exact wire bytes for channel 0/1 write and read via fake — verify by `pytest tests/mcp4xxx/test_mcp4xxx_transport.py -q`.
20. `pyproject.toml`: confirm `gpiozero>=1.6.2` retained, `spi = ["spidev>=3.6"]` present, and pytest `pythonpath=["src"]` unchanged — verify by `grep -q 'spidev>=3.6' pyproject.toml && pytest -q`.
21. Repo root: run full verification for the release candidate — verify by `pytest -q && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`.
22. `docs`/docstrings: add one-line notes for `.transport`, `.spi` compatibility, and `MCP4xxx` no longer being `SPIDevice` — verify by `pylint src` producing no new failures.
</subagent>