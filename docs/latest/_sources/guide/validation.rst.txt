Validating function inputs
==========================

Decorate a function after adding TypedUnit annotations:

.. code-block:: python

   from TypedUnit import Energy, Time, validate_units, ureg

   @validate_units
   def energy_rate(energy: Energy, time: Time, label: str = "run"):
       return energy / time, label

Only parameters annotated with a TypedUnit class are checked. Ordinary
annotations such as ``str`` and ``int`` are not runtime-validated, and return
values are not checked.

Optional and collection inputs
------------------------------

``Optional`` unit values and homogeneous lists or tuples are supported:

.. code-block:: python

   from typing import Optional
   from TypedUnit import Length, Time, validate_units, ureg

   @validate_units
   def summarize(points: list[Length], elapsed: Optional[Time] = None):
       return len(points), elapsed

Invalid values raise ``ValueError`` with the parameter name and, for a
collection, its index. A required ``None`` is rejected as well.

Pydantic
--------

TypedUnit classes can be used as annotations in Pydantic dataclasses or
models. Use ``@validate_units`` on calculation functions that accept those
fields when an explicit function boundary is useful.

Validate a quantity directly
----------------------------

Use ``validate_quantity`` when an API needs to check dimensions, shape, or
values without converting or replacing the quantity. It is separate from the
``validate_units`` decorator:

.. code-block:: python

   from TypedUnit import ureg, validate_quantity

   wavelength = 850 * ureg.nanometer
   validate_quantity(
       value=wavelength,
       unit="m",
       name="wavelength",
       registry=ureg,
       shape=(),
       positive=True,
   )

The registry argument is optional; specifying it rejects quantities created
by other registries. Use ``shape=(3,)`` for a three-element vector, omit shape
to accept any shape, and use ``nonnegative=True`` to allow zero. Nonfinite
values are always rejected. Pint raises its usual dimensionality error for
incompatible units. Validation leaves the original quantity unchanged.
