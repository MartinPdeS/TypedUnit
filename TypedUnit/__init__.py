try:
    from ._version import version as __version__  # noqa: F401

except ImportError:
    __version__ = "0.0.0"

from TypedUnit.units import *
from TypedUnit.helper import validate_units
from TypedUnit.units import ureg, Quantity
