Core concepts
=============

TypedUnit has three complementary pieces.

Dimensional types
-----------------

Classes such as ``Length`` and ``Voltage`` are lightweight marker types. They
do not wrap or copy a quantity:

.. code-block:: python

   distance = 2 * ureg.kilometer
   isinstance(distance, Length)       # True
   isinstance(distance, Mass)         # False

Pint still owns arithmetic, conversion, formatting, and NumPy integration.

The shared registry
-------------------

Import ``ureg`` from TypedUnit rather than constructing a second registry.
It includes domain units such as ``particle``, ``event``, ``photoelectron``,
and ``sqrt_hertz``.

Derived annotation types
------------------------

Unit classes can describe derived dimensions:

.. code-block:: python

   EnergyPerTime = Energy / Time
   isinstance(2 * ureg.watt, EnergyPerTime)  # True

These expressions describe dimensions; use Pint expressions for calculations.
