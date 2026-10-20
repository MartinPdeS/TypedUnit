.. _theory:

Theoretical background
======================

TypedUnit separates values from meaning. Pint stores a magnitude and unit and
performs dimensional arithmetic. TypedUnit maps selected Pint dimensionalities
to Python classes, allowing the same meaning to appear in annotations and
runtime checks without changing the quantity object.

For practical usage, start with :doc:`guide/quickstart` and
:doc:`guide/validation`.
