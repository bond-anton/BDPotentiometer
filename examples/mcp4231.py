""" Example of MCP4231 usage """

from BDPotentiometer.mcp4xxx import MCP4231

# Create potentiometer with total resistance 10 kOhm
my_pot = MCP4231(r_ab=10e3, device=0)

# Label the two available channels with meaningful names
my_pot.set_channel_label(0, "V_CTRL")
my_pot.set_channel_label(1, "AMPL")

# Set current limiting resistor value for V_CTRL channel
my_pot.set_r_lim("V_CTRL", 1.1e3)
# The properties are also available
my_pot.r_lim = (1.1e3, 0)
print(f"Current limiting resistors: {my_pot.r_lim}")

# Set load resistor value for V_CTRL channel
my_pot.set_r_load("V_CTRL", 50e3)
my_pot.r_load = (100e3, 1e3)
print(f"Load resistors: {my_pot.r_load}")

# Set input voltage
my_pot.set_voltage_in("V_CTRL", 5.0)
my_pot.voltage_in = (5.0, 0.0)
print(f"Input voltage: {my_pot.voltage_in}")

# All Done! Now you can control the pot
my_pot.set_voltage_out("V_CTRL", 3.3)
my_pot.voltage_out = (3.7, 0)
print(f"Output voltage: {my_pot.voltage_out}")

# You can also control the resistance
my_pot.set_r_wb("AMPL", 1e3)
# OR
my_pot.set_r_wa("AMPL", 9e3)

# You can also set pot's winder position to exact value
my_pot.set_value("AMPL", 64)
print(f"Winder position for AMPL channel is {my_pot.get_value('AMPL')}")
print(f"Winder position for all channels: {my_pot.value}")
