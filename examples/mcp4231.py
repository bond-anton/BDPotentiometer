"""Example of MCP4231 usage"""

from BDPotentiometer.mcp4xxx import MCP4231

# Create potentiometer with total resistance 10 kOhm
# `device=` selects the spidev backend and needs the `spi` extra
my_pot = MCP4231(r_ab=10e3, device=0)

# Label the two available channels with meaningful names
my_pot.set_channel_label(0, "V_CTRL")
my_pot.set_channel_label(1, "AMPL")

# Set the current limiting resistor at terminal A for the V_CTRL channel
my_pot.set_r_a("V_CTRL", 1.1e3)
# The properties are also available
my_pot.r_a = (1.1e3, 0)
print(f"Terminal A resistors: {my_pot.r_a}")

# Set load resistor value for V_CTRL channel
my_pot.set_r_load("V_CTRL", 50e3)
my_pot.r_load = (100e3, 1e3)
print(f"Load resistors: {my_pot.r_load}")

# Set input voltage at terminal A
my_pot.set_v_a("V_CTRL", 5.0)
my_pot.v_a = (5.0, 0.0)
print(f"Input voltage: {my_pot.v_a}")

# All Done! Now you can control the pot
my_pot.set_v_w("V_CTRL", 3.3)
my_pot.v_w = (3.7, 0)
print(f"Output voltage: {my_pot.v_w}")

# You can also control the resistance
my_pot.set_r_wb("AMPL", 1e3)
# OR
my_pot.set_r_wa("AMPL", 9e3)

# You can also set pot's wiper position to exact value
my_pot.set_value("AMPL", 64)
print(f"Wiper position for AMPL channel is {my_pot.get_value('AMPL')}")
print(f"Wiper position for all channels: {my_pot.value}")
