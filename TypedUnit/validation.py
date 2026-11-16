"""Direct validation of Pint quantities without modifying their values."""

# ruff: noqa: I001
from __future__ import annotations
import numpy as np
from pint import DimensionalityError, Quantity, UnitRegistry


def validate_quantity(
    value: Quantity,
    *,
    unit: str,
    name: str,
    registry: UnitRegistry | None = None,
    shape: tuple[int, ...] | None = None,
    scalar: bool | None = None,
    positive: bool = False,
    nonnegative: bool = False,
    finite: bool = True,
) -> None:
    """Validate a quantity's registry, dimensions, shape, and magnitudes.

    Parameters
    ----------
    value : pint.Quantity
        Quantity to validate; it is not changed or replaced.
    unit : str
        Unit compatible with the required dimensionality. Magnitudes are
        checked after conversion to this unit.
    name : str
        Parameter name included in error messages.
    registry : pint.UnitRegistry or None, optional
        If supplied, require a quantity created by this exact registry. None
        accepts quantities from any Pint registry. Default is None.
    shape : tuple of int or None, optional
        Required magnitude shape. An empty tuple requires a scalar; None leaves
        the shape unrestricted. Default is None.
    scalar : bool or None, optional
        Compatibility shorthand for ``shape=()`` when true. False leaves the
        shape unrestricted. Do not combine with a non-None ``shape``.
    positive : bool, optional
        Require every magnitude to be strictly positive. Default is False.
    nonnegative : bool, optional
        Require every magnitude to be nonnegative. Default is False.
    finite : bool, optional
        Require finite magnitudes. Default is True. Set False only when the
        calling API deliberately permits non-finite sentinel values and checks
        them separately.

    Returns
    -------
    None
        The supplied quantity is preserved and no converted value is returned.

    Raises
    ------
    ValueError
        If value is not a Pint quantity, belongs to a disallowed registry, has
        incompatible units, or violates shape or sign requirements.
        If magnitudes are nonfinite or violate shape or sign requirements.
    """
    if not isinstance(value, Quantity):
        raise ValueError(
            f"{name} requires an explicit quantity with units compatible with {unit}."
        )

    if registry is not None and not isinstance(value, registry.Quantity):
        raise ValueError(f"{name} must belong to the specified unit registry.")

    if scalar is not None:
        if shape is not None:
            raise ValueError("Supply shape or scalar, not both.")

        shape = () if scalar else None

    if unit == "radian" and value.units == value._REGISTRY.dimensionless:
        raise ValueError(
            f"{name} requires explicit angular units, such as degree or radian."
        )

    try:
        magnitude = np.asarray(value.to(unit).magnitude)
    except DimensionalityError as error:
        raise ValueError(f"{name} must have units compatible with {unit}.") from error

    if shape is not None and magnitude.shape != shape:
        if shape == ():
            raise ValueError(f"{name} must be a scalar (shape ()).")

        raise ValueError(f"{name} must have shape {shape}.")

    if finite and not np.all(np.isfinite(magnitude)):
        raise ValueError(f"{name} must be finite.")

    if positive or nonnegative:
        if np.iscomplexobj(magnitude):
            raise ValueError(f"{name} must be real to check sign constraints.")

        if positive and np.any(magnitude <= 0):
            raise ValueError(f"{name} must be positive.")

        if nonnegative and np.any(magnitude < 0):
            raise ValueError(f"{name} must be nonnegative.")
