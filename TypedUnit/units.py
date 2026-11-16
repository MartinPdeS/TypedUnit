# Initialize a unit registry
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin

import pint as _pint
import pint_pandas as pint  # noqa: F401 -- Registers the pandas Pint extension.
from pint import Quantity, UnitRegistry

from .constraints import Finite, Float, Negative, NonZero, Positive
from .shapes import Matrix, Scalar, ShapeSpec, Vector

ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
ureg.setup_matplotlib()

_pint.set_application_registry(ureg)

ureg.define("photoelectron = [Float64]")  # Define a custom unit 'photoelectron'
ureg.define("event = [Int64]")  # Define a custom unit 'events'
ureg.define("sqrt_hertz = Hz**0.5")
ureg.define("bit_bins = ![Int64]")
ureg.define("dB_per_Hz = dB / hertz")


__all__ = [
    "Energy",
    "Time",
    "Power",
    "Watt",
    "Scalar",
    "Vector",
    "Matrix",
    "Float",
    "Finite",
    "NonZero",
    "Positive",
    "Negative",
    "Voltage",
    "Current",
    "Resistance",
    "Temperature",
    "Length",
    "Volume",
    "FlowRate",
    "Frequency",
    "Angle",
    "Mass",
    "RefractiveIndex",
    "Dimensionless",
    "Responsitivity",
    "Viscosity",
    "Area",
    "ElectricField",
    "Velocity",
    "Ohm",
    "Concentration",
    "Particle",
    "ParticleFlux",
    "AnyUnit",
]


class UnitMeta(type):
    """
    Metaclass that makes isinstance(x, SomeUnit) return True
    when x is a pint.Quantity with the right dimensionality.
    """

    def __instancecheck__(cls, obj):
        if not isinstance(obj, Quantity):
            return False
        expected = getattr(cls, "_expected_dim", None)
        if expected is None:
            return True
        # Use pint's dimensionality check; accepts strings like "energy"
        return obj.check(expected)

    def __truediv__(cls, other):
        if not (isinstance(other, UnitMeta) and issubclass(other, BaseUnit)):
            return NotImplemented
        num = cls.__name__
        den = other.__name__
        name = f"{num}Per{den}"
        expected = f"{cls._expected_dim}/{other._expected_dim}"
        # Create a new subclass that uses the same metaclass
        return UnitMeta(name, (BaseUnit,), {"_expected_dim": expected})

    # (Optional) multiplication, powers, etc., if you ever want them.
    def __mul__(cls, other):
        if not (isinstance(other, UnitMeta) and issubclass(other, BaseUnit)):
            return NotImplemented
        a = cls.__name__
        b = other.__name__
        name = f"{a}Times{b}"
        expected = f"({cls._expected_dim})*({other._expected_dim})"
        return UnitMeta(name, (BaseUnit,), {"_expected_dim": expected})

    def __pow__(cls, power):
        if not isinstance(power, int):
            return NotImplemented
        name = f"{cls.__name__}Pow{power}"
        expected = f"({cls._expected_dim})**{power}"
        return UnitMeta(name, (BaseUnit,), {"_expected_dim": expected})


class BaseUnit(metaclass=UnitMeta):
    _expected_dim: str | None = None

    @classmethod
    def __class_getitem__(cls, *metadata: Any) -> Any:
        """Attach shape and value contracts to a unit annotation.

        Parameters
        ----------
        metadata : type or ShapeSpec
            Shape marker, numeric marker, or sign marker. Multiple markers can
            be supplied, for example ``Watt[Vector, Float, Positive]``.

        Returns
        -------
        typing.Annotated
            Annotation carrying this unit class and the requested shape.

        Raises
        ------
        TypeError
            If a marker is not supported.
        """
        if len(metadata) == 1 and isinstance(metadata[0], tuple):
            metadata = metadata[0]

        valid_markers = (
            Scalar,
            Vector,
            Matrix,
            Float,
            Finite,
            NonZero,
            Positive,
            Negative,
        )
        valid = all(
            marker in valid_markers
            or isinstance(marker, ShapeSpec)
            or (
                get_origin(marker) in (Union, UnionType)
                and get_args(marker)
                and all(
                    argument in (Positive, Negative) for argument in get_args(marker)
                )
            )
            for marker in metadata
        )

        if not metadata or not valid:
            raise TypeError(
                "Unit annotations require shape, numeric, or sign constraint markers."
            )

        return Annotated[(cls, *metadata)]

    @classmethod
    def check(cls, value):
        if cls._expected_dim is None:
            return value
        assert isinstance(
            value, Quantity
        ), f"Expected a pint Quantity [{cls._expected_dim}] instance, got {type(value)}"
        assert value.check(
            cls._expected_dim
        ), f"Value units {value.dimensionality} do not match {cls.__name__} units"
        return value


class Energy(BaseUnit):
    """Quantity specifically for energy units."""

    _expected_dim = "joule"


class Time(BaseUnit):
    """Quantity specifically for time units."""

    _expected_dim = "second"


class Power(BaseUnit):
    """Quantity specifically for power units."""

    _expected_dim = "watt"


Watt = Power
"""Alias for :class:`Power`, named after the SI unit."""


class Voltage(BaseUnit):
    """Quantity specifically for voltage units."""

    _expected_dim = "volt"


class Current(BaseUnit):
    """Quantity specifically for current units."""

    _expected_dim = "ampere"


class Resistance(BaseUnit):
    """Quantity specifically for resistance units."""

    _expected_dim = "ohm"


class Temperature(BaseUnit):
    """Quantity specifically for temperature units."""

    _expected_dim = "kelvin"


class Length(BaseUnit):
    """Quantity specifically for length units."""

    _expected_dim = "meter"


class Volume(BaseUnit):
    """Quantity specifically for volume units."""

    _expected_dim = "liter"


class FlowRate(BaseUnit):
    """Quantity specifically for flow rate units."""

    _expected_dim = "liter / second"


class Frequency(BaseUnit):
    """Quantity specifically for frequency units."""

    _expected_dim = "hertz"


class Angle(BaseUnit):
    """Quantity specifically for angle units."""

    _expected_dim = "degree"


class Mass(BaseUnit):
    """Quantity specifically for mass units."""

    _expected_dim = "kilogram"


class RefractiveIndex(BaseUnit):
    """Quantity specifically for refractive index units."""

    _expected_dim = "refractive_index_units"


class Dimensionless(BaseUnit):
    """Quantity specifically for dimensionless units."""

    _expected_dim = ""


class Responsitivity(BaseUnit):
    """Quantity specifically for responsitivity units."""

    _expected_dim = "ampere / watt"


class Viscosity(BaseUnit):
    """Quantity specifically for viscosity units."""

    _expected_dim = "pascal * second"


class Area(BaseUnit):
    """Quantity specifically for viscosity units."""

    _expected_dim = "meter * meter"


class ElectricField(BaseUnit):
    """Quantity specifically for electric field units."""

    _expected_dim = "volt / meter"


class Velocity(BaseUnit):
    """Quantity specifically for velocity units."""

    _expected_dim = "meter / second"


class Ohm(BaseUnit):
    """Quantity specifically for resistance units."""

    _expected_dim = "ohm"


class Concentration(BaseUnit):
    """Quantity specifically for concentration units."""

    _expected_dim = "particle / liter"


class Particle(BaseUnit):
    """Quantity specifically for particle units."""

    _expected_dim = "particle"


class ParticleFlux(BaseUnit):
    """Quantity specifically for particle flux units."""

    _expected_dim = "particle / second"


class AnyUnit(BaseUnit):
    """Quantity that can have any unit."""

    _expected_dim = None  # Accept any dimensionality


ureg.AU = ureg.dimensionless
