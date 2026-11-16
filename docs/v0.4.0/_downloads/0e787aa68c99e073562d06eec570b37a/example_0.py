"""
Workflow - 0
============
This shows how to use TypedUnits for unit validation in a function.
"""
from TypedUnit import Energy, Time, Power, validate_units, ureg

# Normal Pint instantiation
energy = 100 * ureg.joule
time = 10 * ureg.second

# But now isinstance works!
assert isinstance(energy, Energy)  # True
assert isinstance(time, Time)      # True

@validate_units
def calculate_power(energy: Energy, time: Time) -> Power:
    """Function with automatic unit validation."""
    return (energy / time).to(ureg.watt)

# This works
power = calculate_power(energy, time)
print(f"Power: {power}")

# This fails with clear error message
length = 5 * ureg.meter
# calculate_power(length, time)  # TypeError: Expected Energy,