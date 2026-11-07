"""Direct quantity validation across registries and array shapes."""

# ruff: noqa: I001
import numpy as np
import pint
import pytest
from TypedUnit import Length, validate_quantity, validate_units


def test_valid_values_are_not_replaced_or_mutated() -> None:
    """Compatible alternate units and array shapes preserve the input."""
    registry = pint.UnitRegistry()
    value = np.array([1.0, 2.0]) * registry.mm
    assert (
        validate_quantity(
            value=value,
            unit="m",
            name="lengths",
            registry=registry,
            shape=(2,),
            positive=True,
        )
        is None
    )
    np.testing.assert_array_equal(value.magnitude, [1.0, 2.0])
    assert value.units == registry.mm
    validate_quantity(value=2 * registry.cm, unit="m", name="length", shape=())


def test_registry_is_optional_but_explicit_registry_is_enforced() -> None:
    """Foreign registries are accepted by default and rejected when specified."""
    first = pint.UnitRegistry()
    second = pint.UnitRegistry()
    validate_quantity(value=1 * first.mm, unit="m", name="length")
    with pytest.raises(TypeError, match="specified unit registry"):
        validate_quantity(
            value=1 * first.mm,
            unit="m",
            name="length",
            registry=second,
        )
    with pytest.raises(TypeError, match="length"):
        validate_quantity(value=1, unit="m", name="length")


def test_units_and_shape_are_checked() -> None:
    """Wrong dimensions propagate Pint errors and scalar shape is explicit."""
    registry = pint.UnitRegistry()
    with pytest.raises(pint.DimensionalityError):
        validate_quantity(value=1 * registry.second, unit="m", name="length")
    with pytest.raises(ValueError, match="shape"):
        validate_quantity(
            value=np.array([1]) * registry.mm,
            unit="m",
            name="length",
            shape=(),
        )


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_nonfinite_values_rejected(value: float) -> None:
    """Nonfinite values are rejected independently of sign requirements."""
    registry = pint.UnitRegistry()
    with pytest.raises(ValueError, match="finite"):
        validate_quantity(value=value * registry.mm, unit="m", name="length")


def test_sign_requirements_apply_to_every_element() -> None:
    """Strict positivity rejects zero while nonnegativity permits it."""
    registry = pint.UnitRegistry()
    zero = np.array([0, 1]) * registry.mm
    validate_quantity(value=zero, unit="m", name="length", nonnegative=True)
    with pytest.raises(ValueError, match="positive"):
        validate_quantity(value=zero, unit="m", name="length", positive=True)
    with pytest.raises(ValueError, match="nonnegative"):
        validate_quantity(
            value=np.array([1, -1]) * registry.mm,
            unit="m",
            name="length",
            nonnegative=True,
        )


def test_existing_validate_units_decorator_remains_available() -> None:
    """The separate direct validator does not replace the decorator API."""
    registry = pint.UnitRegistry()

    @validate_units
    def identity(length: Length) -> Length:
        return length

    assert identity(2 * registry.mm) == 2 * registry.mm
    with pytest.raises(ValueError):
        identity(2 * registry.second)
