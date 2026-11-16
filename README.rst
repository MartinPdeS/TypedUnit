|logo|

.. list-table::
   :widths: 35 65
   :header-rows: 1

   * - Badge
     - Status
   * - Python versions
     - |python|
   * - Documentation
     - |docs|
   * - Continuous integration
     - |ci/cd|
   * - Test coverage
     - |coverage|
   * - PyPI package
     - |PyPI|
   * - PyPI downloads
     - |PyPI_download|
   * - Anaconda package
     - |anaconda|

TypedUnit
=========

**Physical quantities with readable types and runtime checks.**

TypedUnit adds dimensional types such as ``Length``, ``Energy``, and ``Power``
to `Pint <https://pint.readthedocs.io/>`_. Keep ordinary Pint quantities,
arithmetic, and unit conversions, then add validation where values enter your
functions. Catch a distance passed as an energy before a calculation begins.

`Documentation <https://martinpdes.github.io/TypedUnit/>`_ |
`Quick start <https://martinpdes.github.io/TypedUnit/guide/quickstart.html>`_ |
`Examples <https://martinpdes.github.io/TypedUnit/gallery/index.html>`_ |
`Report an issue <https://github.com/MartinPdeS/TypedUnit/issues>`_

Features
--------

* **Dimensional type checks:** ``isinstance(quantity, Energy)`` accepts joules,
  kilowatt hours, and other compatible energy units.
* **Function input validation:** ``@unit_validator`` checks annotated inputs
  and reports the parameter that failed. ``validate_units`` is an alias.
* **Array contracts:** distinguish scalars, vectors, and matrices, with
  optional fixed sizes such as ``Vector[3]``.
* **Value constraints:** require floating-point, finite, nonzero, positive,
  or negative magnitudes directly in annotations.
* **Direct validation:** check a quantity's dimensions, registry, shape, and
  values without replacing it.
* **Pint interoperability:** quantities retain their units, NumPy behavior,
  and explicit ``.to(...)`` conversions.

Installation
------------

Install from PyPI using Python 3.10 or newer:

.. code-block:: bash

   python -m pip install TypedUnit

Or install from the author's Conda channel:

.. code-block:: bash

   conda install --channel martinpdes typedunit

Verify the installation with the interpreter you will use for your code:

.. code-block:: bash

   python -c "import TypedUnit; print(TypedUnit.__version__)"

The current dependency range is Pint ``>=0.24,<0.26``. NumPy, Matplotlib,
and pint-pandas are installed automatically. Pydantic is optional and can
be installed separately for model or dataclass integrations.

First calculation
-----------------

Create values with the shared ``ureg`` registry, annotate a function's inputs,
and add ``@unit_validator``:

.. code-block:: python

   from TypedUnit import Energy, Power, Time, unit_validator, ureg

   @unit_validator
   def average_power(*, energy: Energy, duration: Time) -> Power:
       """Calculate average power from energy and elapsed time.

       Parameters
       ----------
       energy : Energy
           Input energy, with units compatible with joules.
       duration : Time
           Elapsed time, with units compatible with seconds; must be nonzero.

       Returns
       -------
       Power
           Average power expressed in watts.
       """
       return (energy / duration).to(ureg.watt)

   energy = 100 * ureg.joule

   duration = 10 * ureg.second

   power = average_power(
       energy=energy,
       duration=duration,
   )

   print(f"Average power: {power}")

Output:

.. code-block:: text

   Average power: 10.0 watt

The inputs remain Pint quantities. The annotation describes their physical
meaning; ``.to(ureg.watt)`` explicitly selects the output unit.

Catch a dimensional mistake
---------------------------

Using the function above, pass a length where an energy is required:

.. code-block:: python

   try:
       average_power(
           energy=5 * ureg.meter,
           duration=duration,
       )
   except ValueError as error:
       print(f"Invalid input: {error}")

Output:

.. code-block:: text

   Invalid input: Parameter 'energy' must have units compatible with Energy.

Validation runs before the function body. It checks dimensional compatibility,
so an energy in kilojoules is valid without an automatic conversion to joules.
Use additional constraints when a value must also be finite, nonzero, or positive.

Validate array shapes and values
--------------------------------

Combine a physical type with shape and value markers. This function accepts
exactly three finite, positive floating-point power samples:

.. code-block:: python

   import numpy as np
   from TypedUnit import Finite, Float, Positive, Power, Vector, unit_validator, ureg

   @unit_validator
   def mean_power(*, samples: Power[Vector[3], Float, Finite, Positive]) -> Power:
       """Calculate the mean of three positive power samples.

       Parameters
       ----------
       samples : Power[Vector[3], Float, Finite, Positive]
           Three finite, strictly positive floating-point power values.

       Returns
       -------
       Power
           Mean power expressed in watts.
       """
       return samples.mean().to(ureg.watt)

   samples = np.array([1.0, 2.0, 3.0]) * ureg.milliwatt

   power = mean_power(samples=samples)

   print(f"Mean power: {power}")

Output:

.. code-block:: text

   Mean power: 0.002 watt

``Scalar`` requires a zero-dimensional magnitude, ``Vector`` a one-dimensional
magnitude, and ``Matrix`` a two-dimensional magnitude. Use ``Vector[n]`` or
``Matrix[rows, columns]`` for exact sizes. Constraints apply to every magnitude;
``Float`` requires floating-point values rather than converting integers.

See the `validation guide <https://martinpdes.github.io/TypedUnit/guide/validation.html>`_
for optional inputs, collections, sign unions, and additional examples.

Validate a quantity directly
----------------------------

Use ``validate_quantity`` when you need an explicit validation step instead
of a decorated function:

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

   print(f"Validated wavelength: {wavelength}")

Output:

.. code-block:: text

   Validated wavelength: 850 nanometer

The function returns ``None`` and leaves the original quantity and its units
unchanged. Here it requires a finite, positive scalar length from ``ureg``.
Omit ``registry`` to accept quantities from any Pint registry; omit ``shape``
to leave the shape unrestricted. Nonfinite values are rejected by default.

Physical types and conventions
------------------------------

Some of the available dimensional types are:

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Domain
     - Types
   * - Energy and time
     - ``Energy``, ``Power`` (also ``Watt``), ``Time``, ``Frequency``
   * - Space and motion
     - ``Length``, ``Area``, ``Volume``, ``Velocity``, ``Angle``
   * - Electrical
     - ``Voltage``, ``Current``, ``Resistance``, ``Ohm``
   * - Matter and flow
     - ``Mass``, ``Concentration``, ``FlowRate``, ``Viscosity``, ``Temperature``
   * - Optical and dimensionless
     - ``ElectricField``, ``RefractiveIndex``, ``Dimensionless``

Types describe dimensionality rather than a specific display unit. Construct
values with ``3 * ureg.joule``, rather than calling ``Energy(...)``. You can
also compose dimensional types:

.. code-block:: python

   from TypedUnit import Energy, Time, ureg

   EnergyPerTime = Energy / Time

   power = 2 * ureg.watt

   print(f"Has power dimensions: {isinstance(power, EnergyPerTime)}")

Output:

.. code-block:: text

   Has power dimensions: True

Use ``Dimensionless`` for dimensionless Pint quantities. Use ``NoUnit`` when
an input must be a bare number and Pint quantities must be rejected, including
dimensionless quantities. For example, ``NoUnit[Scalar, Float, Positive]``
describes a bare positive floating-point scalar.

The `unit reference <https://martinpdes.github.io/TypedUnit/units.html>`_
lists the available types.

Common issues
-------------

* **An annotation alone does not validate a function.** Add ``@unit_validator``
  to check supported input annotations at call time. Ordinary ``str`` and
  ``int`` annotations and return values are not runtime-validated.
* **Runtime checks are distinct from static analysis.** Dimensional markers
  and shape annotations do not provide static unit or shape inference.
* **Compatible dimensions do not imply the same physical meaning.** Checks
  cannot distinguish quantities that share dimensions, such as frequency
  and angular frequency. Keep conventions explicit in your API.
* **Keep registry ownership consistent.** Prefer ``TypedUnit.ureg`` throughout
  an application. Quantities from different Pint registries can fail when
  combined, even if their dimensions match.
* **A one-element array is not a scalar.** ``Scalar`` requires shape ``()``;
  an array with shape ``(1,)`` is a vector.
* **A bare number has no physical units.** Attach units to dimensional inputs,
  or use ``NoUnit`` for deliberately unitless inputs.

Read the `Pint integration guide <https://martinpdes.github.io/TypedUnit/guide/pint.html>`_
for registry and conversion conventions.

Developer setup
---------------

Clone the repository and install it into a virtual environment:

.. code-block:: bash

   git clone https://github.com/MartinPdeS/TypedUnit.git
   cd TypedUnit
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -e ".[testing,documentation,dev]"

On Windows, activate the environment with ``.venv\Scripts\activate`` instead.
Run tests, lint checks, and the documentation build with the same interpreter:

.. code-block:: bash

   python -m pytest
   python -m ruff check TypedUnit tests
   python -m sphinx -b html docs/source docs/build/html

See `CONTRIBUTING.md <https://github.com/MartinPdeS/TypedUnit/blob/master/CONTRIBUTING.md>`_
for contribution and release guidance.

Contact and license
-------------------

Questions, bug reports, and proposed improvements are welcome on the
`issue tracker <https://github.com/MartinPdeS/TypedUnit/issues>`_.
For other inquiries, contact
`Martin Poinsinet de Sivry-Houle <mailto:martin.poinsinet.de.sivry@gmail.com>`_.

TypedUnit is distributed under the
`MIT license <https://github.com/MartinPdeS/TypedUnit/blob/master/LICENSE>`_.

.. |logo| image:: https://github.com/MartinPdeS/TypedUnit/raw/master/docs/images/logo.svg
   :target: https://github.com/MartinPdeS/TypedUnit
   :alt: TypedUnit — physical quantities with readable types and runtime checks
   :width: 520px

.. |python| image:: https://img.shields.io/pypi/pyversions/typedunit.svg
   :target: https://www.python.org/
   :alt: Supported Python versions

.. |docs| image:: https://github.com/MartinPdeS/TypedUnit/actions/workflows/deploy_documentation.yml/badge.svg
   :target: https://martinpdes.github.io/TypedUnit/
   :alt: Documentation build

.. |ci/cd| image:: https://github.com/MartinPdeS/TypedUnit/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/MartinPdeS/TypedUnit/actions/workflows/tests.yml
   :alt: Test status

.. |coverage| image:: https://raw.githubusercontent.com/MartinPdeS/TypedUnit/python-coverage-comment-action-data/badge.svg
   :target: https://htmlpreview.github.io/?https://github.com/MartinPdeS/TypedUnit/blob/python-coverage-comment-action-data/htmlcov/index.html
   :alt: Test coverage

.. |PyPI| image:: https://badge.fury.io/py/typedunit.svg
   :target: https://pypi.org/project/typedunit/
   :alt: PyPI version

.. |PyPI_download| image:: https://img.shields.io/pypi/dm/typedunit.svg
   :target: https://pypistats.org/packages/typedunit
   :alt: Monthly PyPI downloads

.. |anaconda| image:: https://anaconda.org/martinpdes/typedunit/badges/version.svg
   :target: https://anaconda.org/martinpdes/typedunit
   :alt: Anaconda version
