#!/usr/bin/env python3
"""
Comprehensive test suite for TypedUnits library.

This module tests all core functionality including:
- Unit type checking with isinstance()
- Metaclass behavior
- Validation decorators
- Unit conversions
- Error handling
- Integration features
"""

import pytest
import numpy

# Import the TypedUnits components
from TypedUnit import (
    Energy, Time, Power, Voltage, Current, Resistance,
    Temperature, Length, Volume, FlowRate, Frequency, Mass,
    Angle, RefractiveIndex, Dimensionless,
    ureg, Quantity, validate_units
)


# Test data for parametrized tests
@pytest.mark.parametrize("quantity,unit_type,expected", [
    # Energy tests
    (100 * ureg.joule, Energy, True),
    (1.5 * ureg.kilowatt_hour, Energy, True),
    (250 * ureg.calorie, Energy, True),
    (10 * ureg.second, Energy, False),  # Time, not Energy
    (5 * ureg.meter, Energy, False),   # Length, not Energy

    # Time tests
    (30 * ureg.second, Time, True),
    (5 * ureg.minute, Time, True),
    (2 * ureg.hour, Time, True),
    (500 * ureg.millisecond, Time, True),
    (100 * ureg.joule, Time, False),   # Energy, not Time

    # Power tests
    (1500 * ureg.watt, Power, True),
    (2.5 * ureg.kilowatt, Power, True),
    (1 * ureg.horsepower, Power, True),
    (12 * ureg.volt, Power, False),    # Voltage, not Power

    # Electrical units
    (12 * ureg.volt, Voltage, True),
    (2.5 * ureg.ampere, Current, True),
    (4.8 * ureg.ohm, Resistance, True),
    (12 * ureg.volt, Current, False),  # Cross-check
    (2.5 * ureg.ampere, Resistance, False),

    # Mechanical units
    (10 * ureg.meter, Length, True),
    (50 * ureg.millimeter, Length, True),
    (2 * ureg.kilometer, Length, True),
    (5 * ureg.liter, Volume, True),
    (250 * ureg.milliliter, Volume, True),
    (10 * ureg.meter, Volume, False),  # Length, not Volume

    # Temperature tests
    (300 * ureg.kelvin, Temperature, True),
    (77 * ureg.kelvin, Temperature, True),
    # (50 * ureg.hertz, Temperature, False),

    # # Frequency and angle
    (50 * ureg.hertz, Frequency, True),
    (1.57 * ureg.radian, Angle, True),

    # Other tests
    (1 * ureg.RIU, RefractiveIndex, True),
    (1 * ureg.dimensionless, Dimensionless, True),
    (1 * ureg.gram, Mass, True)
])
def test_unit_type_checking(quantity, unit_type, expected):
    """Test isinstance() functionality for all unit types."""
    assert isinstance(quantity, unit_type) == expected


@pytest.mark.parametrize("non_quantity", [
    42,           # int
    3.14,         # float
    "10 meters",  # string
    [1, 2, 3],    # list
    {'value': 10}, # dict
    None,         # None
])
def test_non_quantity_objects_rejected(non_quantity):
    """Test that non-Quantity objects are properly rejected by all unit types."""
    unit_types = [Energy, Time, Power, Voltage, Current, Resistance,
                  Temperature, Length, Volume, Frequency, Angle]

    for unit_type in unit_types:
        assert not isinstance(non_quantity, unit_type)


@pytest.mark.parametrize("unit_type,valid_quantity,invalid_quantity", [
    (Energy, 100 * ureg.joule, 10 * ureg.meter),
    (Time, 30 * ureg.second, 100 * ureg.joule),
    (Power, 1500 * ureg.watt, 10 * ureg.meter),
    (Voltage, 12 * ureg.volt, 5 * ureg.ampere),
    (Current, 2.5 * ureg.ampere, 12 * ureg.volt),
    (Resistance, 4.8 * ureg.ohm, 100 * ureg.joule),
    (Length, 100 * ureg.meter, 50 * ureg.joule),
    (Temperature, 300 * ureg.kelvin, 2.5 * ureg.ampere),
])
def test_unit_check_methods(unit_type, valid_quantity, invalid_quantity):
    """Test the check() methods for various unit types."""
    # Valid quantity should pass
    assert unit_type.check(valid_quantity) == valid_quantity

    # Invalid quantity should raise AssertionError
    with pytest.raises(AssertionError, match="Value units.*do not match.*units"):
        unit_type.check(invalid_quantity)


@pytest.mark.parametrize("invalid_input", [
    42,
    3.14,
    "not a quantity",
    None,
    [1, 2, 3],
])
def test_check_method_rejects_non_quantities(invalid_input):
    """Test that check() methods reject non-Quantity objects."""
    with pytest.raises(AssertionError, match="Expected a pint Quantity instance"):
        Energy.check(invalid_input)


@pytest.mark.parametrize("energy_quantity", [
    100 * ureg.joule,
    1.5 * ureg.kilowatt_hour,
    250 * ureg.calorie,
    500 * ureg.british_thermal_unit,
])
def test_energy_type_checking_various_units(energy_quantity):
    """Test Energy type checking with various energy units."""
    assert isinstance(energy_quantity, Energy)


@pytest.mark.parametrize("time_quantity", [
    30 * ureg.second,
    5 * ureg.minute,
    2 * ureg.hour,
    500 * ureg.millisecond,
    0.1 * ureg.microsecond,
])
def test_time_type_checking_various_units(time_quantity):
    """Test Time type checking with various time units."""
    assert isinstance(time_quantity, Time)


@pytest.mark.parametrize("power_quantity", [
    1500 * ureg.watt,
    2.5 * ureg.kilowatt,
    1 * ureg.horsepower,
    100 * ureg.milliwatt,
])
def test_power_type_checking_various_units(power_quantity):
    """Test Power type checking with various power units."""
    assert isinstance(power_quantity, Power)


def test_electrical_units_cross_checking():
    """Test that electrical units don't cross-match."""
    voltage = 12 * ureg.volt
    current = 2.5 * ureg.ampere
    resistance = 4.8 * ureg.ohm

    # Positive checks
    assert isinstance(voltage, Voltage)
    assert isinstance(current, Current)
    assert isinstance(resistance, Resistance)

    # Cross-check failures
    assert not isinstance(voltage, Current)
    assert not isinstance(current, Resistance)
    assert not isinstance(resistance, Voltage)


def test_mechanical_units_cross_checking():
    """Test mechanical units don't cross-match."""
    length = 10 * ureg.meter
    volume = 5 * ureg.liter

    assert isinstance(length, Length)
    assert isinstance(volume, Volume)
    assert not isinstance(length, Volume)
    assert not isinstance(volume, Length)


@pytest.mark.parametrize("temperature_quantity", [
    300 * ureg.kelvin,
    # 25 * ureg.celsius,
    # 77 * ureg.fahrenheit,
])
def test_temperature_type_checking_various_units(temperature_quantity):
    """Test temperature type checking with various units."""
    assert isinstance(temperature_quantity, Temperature)


@pytest.mark.parametrize("frequency_quantity", [
    50 * ureg.hertz,
    2.4 * ureg.kilohertz,
    1.0 * ureg.megahertz,
])
def test_frequency_type_checking_various_units(frequency_quantity):
    """Test frequency type checking with various units."""
    assert isinstance(frequency_quantity, Frequency)


@pytest.mark.parametrize("angle_quantity", [
    45 * ureg.degree,
    1.57 * ureg.radian,
    90 * ureg.degree,
    3.14159 * ureg.radian,
])
def test_angle_type_checking_various_units(angle_quantity):
    """Test angle type checking with various units."""
    assert isinstance(angle_quantity, Angle)


def test_basic_function_validation():
    """Test basic function parameter validation."""

    @validate_units
    def calculate_power(energy: Energy, time: Time) -> Power:
        return (energy / time).to(ureg.watt)

    # Valid inputs should work
    energy = 1000 * ureg.joule
    time = 10 * ureg.second
    result = calculate_power(energy, time)

    assert isinstance(result, Quantity)
    assert result.check("watt")

    # Invalid inputs should raise Exception
    length = 50 * ureg.meter
    with pytest.raises(Exception):
        calculate_power(length, time)  # Wrong first parameter

    with pytest.raises(Exception):
        calculate_power(energy, length)  # Wrong second parameter


def test_electrical_calculation_validation():
    """Test validation for electrical calculations."""

    @validate_units
    def calculate_resistance(voltage: Voltage, current: Current) -> Resistance:
        return (voltage / current).to(ureg.ohm)

    voltage = 12 * ureg.volt
    current = 2.5 * ureg.ampere
    resistance = calculate_resistance(voltage, current)

    assert isinstance(resistance, Quantity)
    assert resistance.check("ohm")

    # Test with wrong units
    energy = 100 * ureg.joule
    with pytest.raises(Exception):
        calculate_resistance(energy, current)


def test_mixed_parameter_types_validation():
    """Test validation with mixed parameter types."""

    @validate_units
    def calculate_work_rate(power: Power, efficiency: float, duration: Time):
        return power * efficiency * duration

    power = 1500 * ureg.watt
    efficiency = 0.85  # dimensionless float
    duration = 3600 * ureg.second

    result = calculate_work_rate(power, efficiency, duration)
    assert isinstance(result, Quantity)


def test_no_annotation_parameters_validation():
    """Test that parameters without annotations are not validated."""

    @validate_units
    def mixed_function(energy: Energy, time, factor: float):
        # 'time' has no annotation, so it won't be validated
        return energy * factor

    energy = 100 * ureg.joule
    time = "not a quantity"  # This should be fine since no annotation
    factor = 2.0

    # Should not raise an error
    result = mixed_function(energy, time, factor)
    assert isinstance(result, Quantity)


@pytest.mark.parametrize("energy_quantity", [
    1000 * ureg.joule,
    1.5 * ureg.kilowatt_hour,
    250 * ureg.calorie,
])
def test_energy_conversions(energy_quantity):
    """Test energy unit conversions preserve type checking."""
    # Convert to different energy units
    joule_energy = energy_quantity.to(ureg.joule)
    kwh_energy = energy_quantity.to(ureg.kilowatt_hour)

    # All should still be recognized as Energy
    assert isinstance(energy_quantity, Energy)
    assert isinstance(joule_energy, Energy)
    assert isinstance(kwh_energy, Energy)


def test_mathematical_operations_preserve_type_checking():
    """Test that mathematical operations preserve type checking capability."""
    energy1 = 100 * ureg.joule
    energy2 = 50 * ureg.joule
    time_val = 10 * ureg.second

    # Energy arithmetic
    total_energy = energy1 + energy2
    energy_diff = energy1 - energy2

    assert isinstance(total_energy, Energy)
    assert isinstance(energy_diff, Energy)

    # Power calculation (Energy / Time = Power)
    power = energy1 / time_val
    assert isinstance(power, Power)


def test_unit_arithmetic_cross_types():
    """Test arithmetic operations between different unit types."""
    voltage = 12 * ureg.volt
    current = 2 * ureg.ampere
    time_val = 30 * ureg.second

    # Ohm's law: V = I * R, so R = V / I
    resistance = voltage / current
    assert isinstance(resistance, Resistance)

    # Power: P = V * I
    power = voltage * current
    assert isinstance(power, Power)

    # Energy: E = P * t
    energy = power * time_val
    assert isinstance(energy, Energy)


@pytest.mark.parametrize("invalid_input", [
    None,
    42,
    "10 joules",
    [100, ureg.joule],
    {'value': 100, 'unit': 'joule'}
])
def test_invalid_quantity_detection(invalid_input):
    """Test detection of invalid quantities."""
    assert not isinstance(invalid_input, Energy)
    assert not isinstance(invalid_input, Time)
    assert not isinstance(invalid_input, Power)


def test_dimensionless_quantities():
    """Test handling of dimensionless quantities."""
    ratio = 1.5 * ureg.dimensionless
    percentage = 85 * ureg.percent

    # These should not match other unit types
    assert not isinstance(ratio, Energy)
    assert not isinstance(ratio, Time)
    assert not isinstance(percentage, Power)


def test_complex_derived_units():
    """Test handling of complex derived units."""
    # Flow rate: volume/time
    flow_rate = (5 * ureg.liter) / (1 * ureg.minute)

    # This should match FlowRate if properly defined
    assert isinstance(flow_rate, FlowRate)


def test_physics_calculations_integration():
    """Test common physics calculations with unit validation."""

    @validate_units
    def electrical_power(voltage: Voltage, current: Current) -> Power:
        return voltage * current

    @validate_units
    def work_done(power: Power, time: Time) -> Energy:
        return (power * time).to(ureg.joule)

    # Test the calculation chain
    voltage = 12 * ureg.volt
    current = 5 * ureg.ampere
    duration = 3600 * ureg.second  # 1 hour

    power = electrical_power(voltage, current)
    work = work_done(power, duration)

    assert isinstance(power, Power)
    assert isinstance(work, Energy)

    # Verify the calculation
    assert power.magnitude == 60  # 12V * 5A = 60W
    assert numpy.isclose(work.to(ureg.kilowatt_hour).magnitude, 0.06)  # 60W * 1h = 0.06 kWh


@pytest.mark.parametrize("length_quantity", [
    100 * ureg.meter,
    50 * ureg.millimeter,
    2 * ureg.kilometer,
    328 * ureg.foot,  # Imperial if supported
])
def test_multiple_unit_systems(length_quantity):
    """Test working with multiple unit systems."""
    assert isinstance(length_quantity, Length)

    # Convert and verify
    meter_length = length_quantity.to(ureg.meter)
    assert isinstance(meter_length, Length)


if __name__ == "__main__":
    pytest.main(["-W", "error", "-s", __file__])
