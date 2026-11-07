**Date**: |today|, **Version**: |version|

TypedUnit documentation
=======================

TypedUnit adds readable, runtime-checkable physical quantity types to Pint.
It keeps Pint's quantity objects and operations while giving APIs a vocabulary
for physical meaning such as ``Length``, ``Energy``, and ``Frequency``.

Start here
----------

A typical TypedUnit workflow has three small steps:

#. Create values with the shared :data:`TypedUnit.ureg` registry.
#. Annotate boundaries with the dimensional type that the value represents.
#. Add :func:`TypedUnit.validate_units` where runtime validation is useful.

This keeps unit conversion and arithmetic in Pint while making interfaces
self-documenting and checking dimensional mistakes close to their source.

.. code-block:: python

   from TypedUnit import Energy, ureg, validate_units

   @validate_units
   def efficiency(input_energy: Energy, output_energy: Energy) -> float:
       return (output_energy / input_energy).to_base_units().magnitude

   input_energy = 2 * ureg.kilojoule
   output_energy = 500 * ureg.joule
   print(efficiency(input_energy, output_energy))

Choose a path
-------------

* New to TypedUnit? Read :doc:`guide/installation` and :doc:`guide/quickstart`.
* Designing an API? See :doc:`guide/concepts` and :doc:`guide/validation`.
* Integrating with Pint or NumPy? Read :doc:`guide/pint`.
* Looking for a type or helper? Open :doc:`units` and :doc:`code`.
* Want runnable examples? Browse :doc:`gallery/index`.

What TypedUnit provides
-----------------------

TypedUnit supplies a shared registry, dimensional marker classes, and an
optional validation decorator. Marker classes describe what a value means;
they do not replace Pint quantities or introduce a second unit system.

The package is intentionally small at integration boundaries. Existing Pint
quantities can be passed through TypedUnit annotations, converted normally,
and used with NumPy. Applications can adopt the annotations incrementally,
starting with public functions and configuration models.

Compatibility notes
-------------------

Use :data:`TypedUnit.ureg` throughout an application. Quantities created by a
second Pint registry may have compatible dimensions but are different runtime
objects, which can make validation and comparisons surprising. Convert values
at library boundaries and keep registry ownership explicit.

.. toctree::
    :maxdepth: 2
    :hidden:

    Guide <guide>
    Reference <reference>
    Examples <gallery/index>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
