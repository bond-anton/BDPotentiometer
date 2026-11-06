# BDPotentiometer

![Build](https://github.com/bond-anton/BDPotentiometer/actions/workflows/python-package.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/bdpotentiometer/badge/?version=latest)](https://bdpotentiometer.readthedocs.io/en/latest/?badge=latest)

Module to operate digital potentiometers over SPI. Supports the MCP4xxx series
through a pluggable transport layer.

## Installation

The bare package installs the core library only: the model classes and
`FakeSpiTransport` work, while building a device for real hardware raises an
`ImportError` naming the extra to install.

```shell
$ pip install BDPotentiometer
```

The default hardware backend is spidev; the transport package's `spi` extra
installs it:
```shell
$ pip install 'scietex.hal.spi[spi]'
```

The optional gpiozero backend needs its own extra:
```shell
$ pip install 'scietex.hal.spi[gpiozero]'
```

## Usage

Import the correct potentiometer class, for example MCP4231, and start operating your pot.

```python
from BDPotentiometer.mcp4xxx import MCP4231


my_pot = MCP4231(r_ab=10e3, device=0)
my_pot.channels[0].value = 43
```

`device=` is the spidev chip-select line, so this selects `SpiDevTransport` and
needs the `spi` extra. Pin keywords select the gpiozero backend instead:

```python
my_pot = MCP4231(r_ab=10e3, clock_pin=11, select_pin=8)
```

`value` is an integer code clamped to `0..max_code`, which equals `max_value`:
`0..128` on 7-bit parts and `0..256` on 8-bit parts. Fractional values and
booleans are rejected. Backend keywords cannot be combined with `transport=`
or `spi=`; doing so raises `TypeError`.

## Transports

The transport layer lives in the `scietex.hal.spi` distribution
(https://github.com/bond-anton/scietex.hal.spi). SPI access goes through a
transport object passed with `transport=`:

* `SpiDevTransport` (default) opens `/dev/spidev<bus>.<device>` through
  `spidev`; needs `scietex.hal.spi[spi]`. `port=` maps to the bus, `device=` to
  the chip-select line.
* `GpiozeroSpiTransport` (optional) wraps gpiozero hardware SPI; passing
  `clock_pin=`, `mosi_pin=`, `miso_pin=`, or `select_pin=` builds one, and it
  needs `scietex.hal.spi[gpiozero]`.
* `FakeSpiTransport` replays scripted responses, so code can run without
  hardware or extras.

```python
from BDPotentiometer.mcp4xxx import MCP4231
from scietex.hal.spi import SpiDevTransport


my_pot = MCP4231(r_ab=10e3, transport=SpiDevTransport(bus=0, device=0))
```

For tests, the fake backend needs no extra:

```python
from BDPotentiometer.mcp4xxx import MCP4231
from scietex.hal.spi import FakeSpiTransport


my_pot = MCP4231(r_ab=10e3, transport=FakeSpiTransport(default=[0, 0]))
```

`spi=` is a legacy alias for `transport=`. `MCP4xxx` is not a
`gpiozero.SPIDevice`; `.spi` returns the backend's raw handle (a
`spidev.SpiDev` or a gpiozero SPI object), and `.close()` / `.closed` release
and report the underlying transport.

Transports are owned by whoever constructs them: a device closes only a
transport it built itself from backend keywords, and leaves a transport passed
with `transport=` or `spi=` open.

`from BDPotentiometer import *` follows `__all__`, which lists only the model
classes: `DigitalPotentiometerDevice`, `DigitalWiper`, `Potentiometer`, and
`SpiDigitalWiper`. Import transports and transport exceptions from
`scietex.hal.spi`.

## Upgrading to 0.4.0

0.4.0 moves the transport layer out of this package into the published
`scietex.hal.spi` 0.1.0 distribution.

Breaking changes:

* `BDPotentiometer.transport` is gone; `scietex.hal.spi` replaces it.
* These names are no longer importable from `BDPotentiometer`: `SpiTransport`,
  `SpiDevTransport`, `FakeSpiTransport`, `I2cTransport`, `TransportError`,
  `TransportClosed`, `is_spi_transport`, `fix_gpiozero_dual_cs_spi`, and
  `GpiozeroSpiTransport`.
* `__all__` now lists only `DigitalPotentiometerDevice`, `DigitalWiper`,
  `Potentiometer`, and `SpiDigitalWiper`.
* The `ImportError` for a missing backend now names `scietex.hal.spi[spi]` or
  `scietex.hal.spi[gpiozero]` instead of the `BDPotentiometer` extras.

Migration:

```python
# before
from BDPotentiometer.transport import SpiDevTransport

# after
from scietex.hal.spi import SpiDevTransport
```

Install the matching transport extra, for example
`pip install 'scietex.hal.spi[spi]'`. Device constructors, the
`transport=`/`spi=`/pin keywords, `.close()`, `.closed`, `.transport`, and
`.spi` are unchanged.

Please see the [examples](examples) directory for more usage examples.

Detailed documentation is available at https://bdpotentiometer.readthedocs.io

## License

BDPotentiometer is free open source software licensed under MIT License
