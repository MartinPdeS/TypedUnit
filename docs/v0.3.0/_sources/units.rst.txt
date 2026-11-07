Unit types
==========

All public unit classes are re-exported from ``TypedUnit``.

.. list-table:: Common types
   :header-rows: 1
   :widths: 28 36 36

   * - Type
     - Dimension
     - Typical units
   * - ``Length`` / ``Area`` / ``Volume``
     - length / length squared / volume
     - meter, square_meter, liter
   * - ``Mass`` / ``Time`` / ``Frequency``
     - mass / time / inverse time
     - kilogram, second, hertz
   * - ``Velocity`` / ``FlowRate``
     - length per time / liter per second
     - meter / second, liter / second
   * - ``Energy`` / ``Power``
     - energy / energy per time
     - joule, watt
   * - ``Voltage`` / ``Current`` / ``Resistance``
     - potential / current / resistance
     - volt, ampere, ohm
   * - ``Temperature`` / ``Angle``
     - temperature / angle
     - kelvin, degree
   * - ``Dimensionless`` / ``AnyUnit``
     - no dimensions / any dimensionality
     - dimensionless / any Pint quantity

See :doc:`code` for the complete generated class reference.
