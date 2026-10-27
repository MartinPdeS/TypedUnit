Working with Pint
=================

TypedUnit is a thin layer over Pint. A quantity remains a normal
``pint.Quantity`` and can be converted, indexed, or used with NumPy.

.. code-block:: python

   from TypedUnit import Length, ureg

   diameter = 30 * ureg.centimeter
   area = (diameter / 2) ** 2 * 3.14159
   assert isinstance(diameter, Length)
   print(area.to(ureg.square_meter))

Dimensionality is the source of truth: metres and kilometres are both
``Length``. Avoid mixing registries; use the shared ``TypedUnit.ureg`` at
integration boundaries when external libraries return quantities.

TypedUnit classes are markers, not constructors. Create values with Pint:

.. code-block:: python

   energy = 3 * ureg.joule
