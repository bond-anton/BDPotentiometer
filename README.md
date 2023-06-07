# BDPotentiometer

![Build](https://github.com/bond-anton/BDPotentiometer/actions/workflows/python-package.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/bdpotentiometer/badge/?version=latest)](https://bdpotentiometer.readthedocs.io/en/latest/?badge=latest)

Module to operate Digital Potentiometer over SPI bus. Extends gpiozero SPIDev class.

## Installation

To install BDPotentiometer use pip
```shell
$ pip install BDPotentiometer
```

## Usage

Just import the correct potentiometer class, for example MCP4231, and start operating your pot.

```python
from BDPotentiometer.mcp4xxx import MCP4231


my_pot = MCP4231(r_ab=10e3, device=0)
my_pot.channels[0].value = 43
```

Please see the [examples](examples) directory for more usage examples.

Detailed documentation is available at https://bdpotentiometer.readthedocs.io

## License

BDPotentiometer is free open source software licensed under MIT License