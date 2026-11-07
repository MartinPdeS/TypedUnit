Quick start
===========

Create quantities as you would with Pint, and use TypedUnit classes where
physical meaning matters:

.. code-block:: python

   from TypedUnit import Energy, Power, Time, ureg, validate_units

   energy = 100 * ureg.joule
   duration = 10 * ureg.second

   assert isinstance(energy, Energy)
   assert isinstance(duration, Time)

   @validate_units
   def average_power(energy: Energy, duration: Time) -> Power:
       return (energy / duration).to(ureg.watt)

   print(average_power(energy, duration))  # 10.0 watt

Passing ``5 * ureg.meter`` as ``energy`` raises an error before the function
body runs. Conversion remains explicit: ``energy.to(ureg.kilojoule)``.

TypedUnit checks dimensionality, not the display unit. Joules and kilowatt
hours are both ``Energy``; metres are not.
