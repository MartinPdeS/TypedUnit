TypedUnits
===========

|python| |docs| |coverage| |PyPi| |PyPi_download|

**Type-safe physical units for Python**

TypedUnits is a Python library that extends Pint with type safety and validation capabilities. It allows you to create unit-aware types that work seamlessly with Python's type system and provide runtime validation for physical quantities.

**Key Features:**

- **Type Safety**: Use `isinstance()` checks with unit types like `Energy`, `Time`, `Power`
- **Automatic Validation**: Function decorators for unit validation based on type annotations
- **Pydantic Integration**: Full compatibility with Pydantic dataclasses and models
- **Normal Pint Usage**: Keep your existing Pint code - just add type safety on top

----

**Quick Example**

.. code-block:: python

   from TypedUnits import Energy, Time, Power, validate, ureg

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
   # calculate_power(length, time)  # TypeError: Expected Energy, got Length

----

**Installation**

.. code-block:: bash

   pip install TypedUnits

----

**Basic Usage**

**Unit Type Checking**

.. code-block:: python

   from TypedUnits import Energy, Length, Mass, ureg

   # Create quantities the normal way
   kinetic_energy = 0.5 * 10 * ureg.kilogram * (5 * ureg.meter / ureg.second)**2
   potential_energy = 10 * ureg.kilogram * 9.81 * ureg.meter / ureg.second**2 * 2 * ureg.meter
   distance = 100 * ureg.meter
   mass = 5 * ureg.kilogram

   # Type checking works
   assert isinstance(kinetic_energy, Energy)
   assert isinstance(potential_energy, Energy)
   assert isinstance(distance, Length)
   assert isinstance(mass, Mass)

**Function Validation**

.. code-block:: python

   from TypedUnits import validate_units, Energy, Time, Power

   @validate_units
   def calculate_work(power: Power, time: Time) -> Energy:
       """Calculate work from power and time."""
       return (power * time).to(ureg.joule)

   power = 1500 * ureg.watt
   time = 3600 * ureg.second  # 1 hour
   work = calculate_work(power, time)
   print(f"Work done: {work.to(ureg.kilowatt_hour)}")

**Pydantic Integration**

.. code-block:: python

   from TypedUnits import Energy, Length, Mass
   from pydantic.dataclasses import dataclass

   @dataclass
   class Projectile:
      kinetic_energy: Energy
      height: Length
      mass: Mass

   # Automatic validation on creation
   projectile = Projectile(
      kinetic_energy=500 * ureg.joule,
      height=10 * ureg.meter,
      mass=2 * ureg.kilogram
   )

----

**Available Unit Types**

TypedUnits includes common physical unit types:

- **Mechanical**: `Energy`, `Power`, `Force`, `Pressure`
- **Spatial**: `Length`, `Area`, `Volume`, `Angle`
- **Temporal**: `Time`, `Frequency`
- **Thermal**: `Temperature`, `ThermalConductivity`
- **Electrical**: `Current`, `Voltage`, `Resistance`, `Capacitance`
- **Optical**: `RefractiveIndex`, `Wavelength`, `ElectricField`
- **Mass**: `Mass`, `Density`, `MolarMass`

----

**Advanced Features**

**Custom Unit Types**

.. code-block:: python

   from TypedUnits import create_unit_type

   # Create your own unit types
   MagneticField = create_unit_type('MagneticField', '[magnetic_flux_density]')

   field = 1.5 * ureg.tesla
   assert isinstance(field, MagneticField)

**Flexible Validation**

.. code-block:: python

   from TypedUnits import validate_enhanced

   @validate_enhanced(strict_mode=False, convert_types=True)
   def flexible_function(energy: Energy, count: int) -> str:
       """Function with flexible validation options."""
       return f"Energy per item: {energy / count}"

----

**Requirements**

- Python ≥ 3.8
- Pint ≥ 0.20
- Pydantic ≥ 2.0 (optional, for dataclass integration)

----

**Testing**

.. code-block:: bash

   git clone https://github.com/MartinPdeS/TypedUnits.git
   cd TypedUnits
   pip install -e ".[testing]"
   pytest

----

**Contributing**

TypedUnits is open source and contributions are welcome! Whether you're fixing bugs, adding new unit types, or improving documentation, your help is appreciated.

**Author:** `Martin Poinsinet de Sivry-Houle <https://github.com/MartinPdeS>`_

**Email:** `martin.poinsinet-de-sivry@polymtl.ca <mailto:martin.poinsinet-de-sivry@polymtl.ca?subject=TypedUnits>`_

----

.. |python| image:: https://img.shields.io/pypi/pyversions/typedunits.svg
   :target: https://www.python.org/
   :alt: Python version

.. |PyPi| image:: https://badge.fury.io/py/TypedUnits.svg
   :target: https://pypi.org/project/TypedUnits/
   :alt: PyPi

.. |PyPi_download| image:: https://img.shields.io/pypi/dm/typedunits.svg
   :target: https://pypistats.org/packages/typedunits
   :alt: PyPi download statistics

.. |docs| image:: https://github.com/martinpdes/typedunits/actions/workflows/deploy_documentation.yml/badge.svg
   :target: https://martinpdes.github.io/TypedUnits/
   :alt: Documentation Status

.. |coverage| image:: https://raw.githubusercontent.com/MartinPdeS/TypedUnits/python-coverage-comment-action-data/badge.svg
   :target: https://htmlpreview.github.io/?https://github.com/MartinPdeS/TypedUnits/blob/python-coverage-comment-action-data/htmlcov/index.html
   :alt: Unittest coverage
