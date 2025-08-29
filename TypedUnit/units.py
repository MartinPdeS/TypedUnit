# Initialize a unit registry
import pint as _pint
from pint import Quantity, UnitRegistry
import pint_pandas as pint

ureg = UnitRegistry()
ureg.setup_matplotlib()

_pint.set_application_registry(ureg)

ureg.define("photoelectron = [Float64]")  # Define a custom unit 'photoelectron'
ureg.define("event = [Int64]")  # Define a custom unit 'events'
ureg.define("sqrt_hertz = Hz**0.5")
ureg.define("bit_bins = ![Int64]")

__all__ = [
    "Energy",
    "Time",
    "Power",
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
        expected = f"{getattr(cls, '_expected_dim')}/{getattr(other, '_expected_dim')}"
        # Create a new subclass that uses the same metaclass
        return UnitMeta(name, (BaseUnit,), {"_expected_dim": expected})

    # (Optional) multiplication, powers, etc., if you ever want them.
    def __mul__(cls, other):
        if not (isinstance(other, UnitMeta) and issubclass(other, BaseUnit)):
            return NotImplemented
        a = cls.__name__
        b = other.__name__
        name = f"{a}Times{b}"
        expected = (
            f"({getattr(cls, '_expected_dim')})*({getattr(other, '_expected_dim')})"
        )
        return UnitMeta(name, (BaseUnit,), {"_expected_dim": expected})

    def __pow__(cls, power):
        if not isinstance(power, int):
            return NotImplemented
        name = f"{cls.__name__}Pow{power}"
        expected = f"({getattr(cls, '_expected_dim')})**{power}"
        return UnitMeta(name, (BaseUnit,), {"_expected_dim": expected})


class BaseUnit(metaclass=UnitMeta):
    _expected_dim: str | None = None

    @classmethod
    def check(cls, value):
        if cls._expected_dim is None:
            return value
        assert isinstance(
            value, Quantity
        ), f"Expected a pint Quantity instance, got {type(value)}"
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
