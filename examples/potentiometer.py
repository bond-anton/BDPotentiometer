"""Example of Potentiometer class usage"""

import logging
import numpy as np

# from matplotlib import pyplot as plt
from BDPotentiometer import Potentiometer


def main():
    """Example code"""
    pot = Potentiometer(
        r_ab=10e3, wiper_position=0.5, label="MY POT", log_level=logging.DEBUG
    )
    pot.r_a = 10
    pot.r_b = 20
    pot.r_w = 75
    pot.r_load = 1e6
    pot.v_b = 0
    pot.v_load = 1
    pot.v_a = 5.1

    v_out = np.linspace(-1, 6, num=71)
    values = np.zeros_like(v_out)
    v_act = np.zeros_like(v_out)
    for i, voltage in enumerate(v_out):
        pot.v_w = voltage
        v_act[i] = pot.v_w
        values[i] = pot.wiper_position
    # plt.plot(v_out, values, 'r-o')
    # plt.plot(v_out, v_act, "b-o")
    # plt.grid(True)
    # plt.show()


if __name__ == "__main__":
    main()
