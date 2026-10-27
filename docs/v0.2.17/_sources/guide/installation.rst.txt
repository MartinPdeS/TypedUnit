Installation
============

.. code-block:: console

   $ python -m pip install TypedUnit

TypedUnit supports Python 3.10 and newer. Pydantic is optional; install it
separately when using Pydantic models or dataclasses.

For a development checkout:

.. code-block:: console

   $ git clone https://github.com/MartinPdeS/TypedUnit.git
   $ cd TypedUnit
   $ python -m pip install -e ".[testing,documentation]"
   $ pytest

The package exposes one application-wide registry, :data:`TypedUnit.ureg`.
Use it when creating quantities so dimensional checks remain consistent.
