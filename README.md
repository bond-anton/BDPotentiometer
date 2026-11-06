# BDPotentiometer

![Build](https://github.com/bond-anton/BDPotentiometer/actions/workflows/python-package.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/bdpotentiometer/badge/?version=latest)](https://bdpotentiometer.readthedocs.io/en/latest/?badge=latest)

Module to operate digital potentiometers over SPI. Supports the MCP4xxx series
through a pluggable transport layer.

## Installation

To install BDPotentiometer use pip
```shell
$ pip install BDPotentiometer
```

The optional `spi` extra installs `spidev`, which `SpiDevTransport` needs:
```shell
$ pip install 'BDPotentiometer[spi]'
```

## Usage

Import the correct potentiometer class, for example MCP4231, and start operating your pot.

```python
from BDPotentiometer.mcp4xxx import MCP4231


my_pot = MCP4231(r_ab=10e3, device=0)
my_pot.channels[0].value = 43
```

## Transports

SPI access goes through a transport object passed with `transport=`:

* `GpiozeroSpiTransport` (default) wraps gpiozero hardware SPI. Passing
  `port=`, `device=`, or the pin keywords builds one automatically.
* `SpiDevTransport` talks to `/dev/spidev<bus>.<device>` through `spidev` and
  requires the `spi` extra.
* `FakeSpiTransport` replays scripted responses, so code can run without
  hardware.

```python
from BDPotentiometer.mcp4xxx import MCP4231
from BDPotentiometer.transport import SpiDevTransport


my_pot = MCP4231(r_ab=10e3, transport=SpiDevTransport(bus=0, device=0))
```

`spi=` is a legacy alias for `transport=`. `MCP4xxx` is not a
`gpiozero.SPIDevice`; `.spi` returns the raw gpiozero SPI object when the
gpiozero transport is in use, and `.close()` / `.closed` release and report the
underlying transport.

Please see the [examples](examples) directory for more usage examples.

Detailed documentation is available at https://bdpotentiometer.readthedocs.io

## License

BDPotentiometer is free open source software licensed under MIT License
