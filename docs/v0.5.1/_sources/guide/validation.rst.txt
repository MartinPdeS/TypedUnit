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

Validate a typed annotation directly
------------------------------------

Use ``validate_annotation`` when validation is needed outside a decorated
function, such as while checking dataclass fields. It accepts the same
annotations as ``@unit_validator`` and leaves conversion to the caller::

   from TypedUnit import NoUnit, Scalar, validate_annotation

   validate_annotation(
       value=1.33,
       annotation=NoUnit[Scalar],
       name="background_refractive_index",
   )

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

Value constraints
-----------------

Use ``Float`` to require real floating-point magnitudes, ``Finite`` to reject
infinities and NaNs, and ``NonZero`` to reject zero. Use ``Positive`` or
``Negative`` to constrain a value's sign. Sign markers can be combined with a
union; each magnitude must satisfy at least one marker in that union::

   from TypedUnit import Finite, Float, Negative, NonZero, Positive, Watt, unit_validator

   @unit_validator
   def signed_power(power: Watt[Float, Finite, NonZero, Positive | Negative]) -> None:
       """Accept finite, nonzero floating-point power values."""

``Positive | Negative`` accepts positive and negative values, but rejects zero.
These markers can also be combined with shape markers such as
``Watt[Vector[3], Float, Positive]``.

Bare values without units
-------------------------

Use ``NoUnit`` when an API requires plain numeric values and must reject Pint
quantities. It composes with the same shape and value markers::

   from TypedUnit import Float, NoUnit, Positive, Scalar, unit_validator

   @unit_validator
   def refractive_index(value: NoUnit[Scalar, Float, Positive]) -> None:
       """Accept a bare positive floating-point refractive index."""

``NoUnit`` rejects quantities, including Pint's dimensionless quantities.
Use ``Dimensionless`` when dimensionless quantities such as percentages are
valid inputs. Combine them when either bare values or dimensionless quantities
are accepted::

   from TypedUnit import Dimensionless, NoUnit, unit_validator

   @unit_validator
   def normalized(value: Dimensionless | NoUnit) -> None:
       """Accept bare values or quantities with dimensionless units."""
