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

    print(
        f"Potentiometer: R_AB={pot.r_ab:g} Ohm, R_A={pot.r_a:g} Ohm, "
        f"R_B={pot.r_b:g} Ohm, R_W={pot.r_w:g} Ohm"
    )
    print(
        f"Terminal voltages: V_A={pot.v_a:g} V, V_B={pot.v_b:g} V, V_L={pot.v_load:g} V"
    )

    v_out = np.linspace(-1, 6, num=71)
    values = np.zeros_like(v_out)
    v_act = np.zeros_like(v_out)
    for i, voltage in enumerate(v_out):
        pot.v_w = voltage
        v_act[i] = pot.v_w
        values[i] = pot.wiper_position

    print("Requested V_W [V] -> achieved V_W [V], wiper position:")
    for voltage, actual, position in zip(
        v_out[::10], v_act[::10], values[::10], strict=False
    ):
        print(f"  {voltage:6.2f} -> {actual:6.2f}, {position:5.3f}")
    # plt.plot(v_out, values, 'r-o')
    # plt.plot(v_out, v_act, "b-o")
    # plt.grid(True)
    # plt.show()


if __name__ == "__main__":
    main()
