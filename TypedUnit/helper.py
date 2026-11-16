"""Decorators that validate unit and shape annotations at runtime."""

import inspect
from collections.abc import Callable
from functools import wraps
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin, get_type_hints

import numpy as np

from TypedUnit.constraints import Finite, Float, Negative, NonZero, Positive
from TypedUnit.shapes import Matrix, Scalar, ShapeSpec, Vector
from TypedUnit.units import BaseUnit


def _shape_spec(marker: object) -> ShapeSpec | None:
    """Resolve a public shape marker to its immutable specification."""
    if marker is Scalar:
        return ShapeSpec(())

    if marker is Vector:
        return ShapeSpec((None,))

    if marker is Matrix:
        return ShapeSpec((None, None))

    if isinstance(marker, ShapeSpec):
        return marker

    return None


def _get_unit_type(
    hint: object,
) -> tuple[
    type[BaseUnit] | None,
    bool,
    bool,
    ShapeSpec | None,
    bool,
    bool,
    bool,
    tuple[frozenset[type], ...],
]:
    """Extract unit type, optionality, collection, shape, and value constraints."""
    origin = get_origin(hint)
    args = get_args(hint)

    if origin is Annotated:
        (
            unit_type,
            is_optional,
            is_list,
            shape,
            requires_float,
            requires_finite,
            requires_nonzero,
            sign_groups,
        ) = _get_unit_type(args[0])

        for metadata in args[1:]:
            candidate = _shape_spec(metadata)

            if candidate is not None:
                if shape is not None:
                    raise TypeError(
                        "A unit annotation can contain only one shape marker."
                    )

                shape = candidate

        signs = {Positive, Negative}

        for metadata in args[1:]:
            if metadata is Float:
                requires_float = True
            elif metadata is Finite:
                requires_finite = True
            elif metadata is NonZero:
                requires_nonzero = True
            elif metadata in signs:
                sign_groups += (frozenset((metadata,)),)
            elif get_origin(metadata) in (Union, UnionType):
                alternatives = get_args(metadata)

                if alternatives and all(
                    alternative in signs for alternative in alternatives
                ):
                    sign_groups += (frozenset(alternatives),)

        return (
            unit_type,
            is_optional,
            is_list,
            shape,
            requires_float,
            requires_finite,
            requires_nonzero,
            sign_groups,
        )

    if origin in (Union, UnionType):
        non_none = [argument for argument in args if argument is not type(None)]

        if len(non_none) == 1:
            (
                unit_type,
                _,
                is_list,
                shape,
                requires_float,
                requires_finite,
                requires_nonzero,
                sign_groups,
            ) = _get_unit_type(non_none[0])

            if unit_type is not None:
                return (
                    unit_type,
                    True,
                    is_list,
                    shape,
                    requires_float,
                    requires_finite,
                    requires_nonzero,
                    sign_groups,
                )

        return None, False, False, None, False, False, False, ()

    if origin in (list, tuple):
        if len(args) == 1:
            (
                unit_type,
                is_optional,
                _,
                shape,
                requires_float,
                requires_finite,
                requires_nonzero,
                sign_groups,
            ) = _get_unit_type(args[0])

            if unit_type is not None:
                return (
                    unit_type,
                    is_optional,
                    True,
                    shape,
                    requires_float,
                    requires_finite,
                    requires_nonzero,
                    sign_groups,
                )

        return None, False, False, None, False, False, False, ()

    if inspect.isclass(hint) and issubclass(hint, BaseUnit):
        return hint, False, False, None, False, False, False, ()

    return None, False, False, None, False, False, False, ()


def unit_validator(function: Callable[..., Any]) -> Callable[..., Any]:
    """Validate parameter quantities against unit and optional shape annotations.

    Annotate parameters with a :class:`BaseUnit` subclass to validate units.
    Subscript the unit with shape markers and optional ``Float``, ``Finite``,
    ``NonZero``, ``Positive``, or ``Negative`` markers to validate the magnitude. For example,
    ``Watt[Float, Positive | Negative]`` requires a real floating-point value
    that is nonzero.

    Parameters
    ----------
    function : callable
        Function whose annotated parameters should be validated.

    Returns
    -------
    callable
        Wrapped function that validates bound arguments before calling the
        original function. Return annotations are not validated.

    Raises
    ------
    ValueError
        If an annotated argument has incompatible units or violates its shape
        or value constraints.
    TypeError
        If function arguments are missing or a shape annotation contains
        conflicting shape markers.
    """

    hints = get_type_hints(function, include_extras=True)
    signature = inspect.signature(function)

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound_arguments = signature.bind(*args, **kwargs)
        bound_arguments.apply_defaults()

        for parameter_name, value in bound_arguments.arguments.items():
            if parameter_name not in hints:
                continue

            (
                unit_type,
                is_optional,
                is_list,
                shape,
                requires_float,
                requires_finite,
                requires_nonzero,
                sign_groups,
            ) = _get_unit_type(hints[parameter_name])

            if unit_type is None:
                continue

            if value is None:
                if is_optional:
                    continue

                raise ValueError(f"Parameter '{parameter_name}' cannot be None")

            values = value if is_list else (value,)

            for index, item in enumerate(values):
                item_name = f"{parameter_name}[{index}]" if is_list else parameter_name

                try:
                    unit_type.check(item)
                except (AssertionError, ValueError, TypeError) as error:
                    raise ValueError(
                        f"Parameter '{item_name}' must have units compatible with {unit_type.__name__}."
                    ) from error

                if shape is not None:
                    actual_shape = tuple(np.shape(item.magnitude))

                    if not shape.matches(actual_shape):
                        raise ValueError(
                            f"Parameter '{item_name}' must have {shape}; got shape {actual_shape}."
                        )

                magnitude = np.asarray(item.magnitude)

                if requires_finite or requires_nonzero:
                    if not np.issubdtype(magnitude.dtype, np.number):
                        raise ValueError(
                            f"Parameter '{item_name}' must have numeric magnitudes for finite and nonzero checks."
                        )

                    if requires_finite and not np.all(np.isfinite(magnitude)):
                        raise ValueError(f"Parameter '{item_name}' must be finite.")

                    if requires_nonzero and np.any(magnitude == 0):
                        raise ValueError(f"Parameter '{item_name}' must be nonzero.")

                if sign_groups and (
                    np.iscomplexobj(magnitude)
                    or not np.issubdtype(magnitude.dtype, np.number)
                ):
                    raise ValueError(
                        f"Parameter '{item_name}' must have real numeric magnitudes for sign checks."
                    )

                if requires_float and (
                    np.iscomplexobj(magnitude)
                    or not np.issubdtype(magnitude.dtype, np.floating)
                ):
                    raise ValueError(
                        f"Parameter '{item_name}' must have a real floating-point magnitude."
                    )

                for sign_group in sign_groups:
                    valid = np.zeros(magnitude.shape, dtype=bool)

                    if Positive in sign_group:
                        valid |= magnitude > 0

                    if Negative in sign_group:
                        valid |= magnitude < 0

                    if not np.all(valid):
                        expected = " or ".join(
                            sign.__name__.lower()
                            for sign in (Positive, Negative)
                            if sign in sign_group
                        )
                        raise ValueError(f"Parameter '{item_name}' must be {expected}.")

        return function(*args, **kwargs)

    return wrapper


validate_units = unit_validator


__all__ = ["unit_validator", "validate_units"]
