Validating function inputs
==========================

Decorate a function after adding TypedUnit annotations:

.. code-block:: python

   from TypedUnit import Energy, Time, unit_validator, ureg

   @unit_validator
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
   from TypedUnit import Length, Time, unit_validator, ureg

   @unit_validator
   def summarize(points: list[Length], elapsed: Optional[Time] = None):
       return len(points), elapsed

Invalid values raise ``ValueError`` with the parameter name and, for a
collection, its index. A required ``None`` is rejected as well.

Pydantic
--------

TypedUnit classes can be used as annotations in Pydantic dataclasses or
models. Use ``@unit_validator`` on calculation functions that accept those
fields when an explicit function boundary is useful.

Validate a quantity directly
----------------------------

Use ``validate_quantity`` when an API needs to check dimensions, shape, or
values without converting or replacing the quantity. It is separate from the
``unit_validator`` decorator:

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
values are rejected by default. Set ``finite=False`` only when the calling API
allows non-finite sentinels and validates them separately. Incompatible units
raise a named ``ValueError``. Validation leaves the original quantity unchanged.

Validate array shapes in annotations
-------------------------------------

Subscript a unit class with a shape marker to validate the quantity's
magnitude rank as well as its units:

.. code-block:: python

   import numpy as np
   from TypedUnit import Matrix, Scalar, Vector, Watt, unit_validator, ureg

   @unit_validator
   def process(
       total: Watt[Scalar],
       samples: Watt[Vector],
       covariance: Watt[Matrix[3, 3]],
   ):
       return total, samples, covariance

   process(
       2 * ureg.watt,
       np.ones(10) * ureg.watt,
       np.eye(3) * ureg.watt,
   )

``Scalar`` requires a zero-dimensional magnitude, ``Vector`` a one-dimensional
magnitude, and ``Matrix`` a two-dimensional magnitude. Specify exact sizes with
``Vector[n]`` or ``Matrix[rows, columns]``. ``Power`` and ``Watt`` name the same
unit type. Shape annotations are runtime checks; they do not provide static
shape inference to Python type checkers.
