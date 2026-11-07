"""Direct validation of Pint quantities without modifying their values."""

# ruff: noqa: I001
from __future__ import annotations
import numpy as np
from pint import Quantity, UnitRegistry


def validate_quantity(
    *,
    value: Quantity,
    unit: str,
    name: str,
    registry: UnitRegistry | None = None,
    shape: tuple[int, ...] | None = None,
    positive: bool = False,
    nonnegative: bool = False,
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
    positive : bool, optional
        Require every magnitude to be strictly positive. Default is False.
    nonnegative : bool, optional
        Require every magnitude to be nonnegative. Default is False.

    Returns
    -------
    None
        The supplied quantity is preserved and no converted value is returned.

    Raises
    ------
    TypeError
        If value is not a Pint quantity or belongs to a different registry.
    pint.DimensionalityError
        If the supplied units are incompatible with unit.
    ValueError
        If magnitudes are nonfinite or violate shape or sign requirements.
    """
    if not isinstance(value, Quantity):
        raise TypeError(f"{name} must be a Pint quantity.")

    if registry is not None and not isinstance(value, registry.Quantity):
        raise TypeError(f"{name} must belong to the specified unit registry.")

    magnitude = np.asarray(value.to(unit).magnitude, dtype=float)

    if shape is not None and magnitude.shape != shape:
        raise ValueError(f"{name} must have shape {shape}.")

    if not np.all(np.isfinite(magnitude)):
        raise ValueError(f"{name} must be finite.")

    if positive and np.any(magnitude <= 0):
        raise ValueError(f"{name} must be positive.")

    if nonnegative and np.any(magnitude < 0):
        raise ValueError(f"{name} must be nonnegative.")
