"""Example of DigitalWiper class usage"""

import logging
import numpy as np

# from matplotlib import pyplot as plt
from BDPotentiometer import Potentiometer, DigitalWiper


def main():
    """Example code"""
    pot = Potentiometer(
        r_ab=10e3, wiper_position=0.5, label="MY POT", log_level=logging.DEBUG
    )
    pot.r_a = 0
    pot.r_b = 0
    pot.r_w = 0
    pot.r_load = 1e6
    pot.v_b = 0
    pot.v_load = 1
    pot.v_a = 5.0

    dw = DigitalWiper(
        potentiometer=pot,
        max_value=128,
        invert=True,
        label="MY DW",
        log_level=logging.DEBUG,
    )

    v_out = np.linspace(-1, 6, num=71)
    values = np.zeros_like(v_out)
    v_act = np.zeros_like(v_out)
    for i, voltage in enumerate(v_out):
        dw.v_w = voltage
        v_act[i] = dw.v_w
        # values[i] = dw.potentiometer.wiper_position
        values[i] = dw.value
    # # plt.plot(v_out, values, 'r-o')
    # plt.plot(v_out, v_act, "b-o")

    values = np.arange(129)
    v_out = np.zeros(values.shape, dtype=float)
    v_act = np.zeros(values.shape, dtype=float)
    for i in values:
        dw.value = i
        # v_act[i] = dw.value
        v_act[i] = dw.potentiometer.wiper_position
        v_out[i] = dw.v_w
    # plt.plot(values, v_out, 'r-o')
    # plt.plot(values, v_act, "b-o")
    #
    # plt.grid(True)
    # plt.show()


if __name__ == "__main__":
    main()
