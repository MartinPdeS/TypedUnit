"""Decorators that validate unit and shape annotations at runtime."""

import inspect
from collections.abc import Callable
from functools import wraps
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin, get_type_hints

import numpy as np

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
) -> tuple[type[BaseUnit] | None, bool, bool, ShapeSpec | None]:
    """Extract unit type, optionality, collection, and shape constraints."""
    origin = get_origin(hint)
    args = get_args(hint)

    if origin is Annotated:
        unit_type, is_optional, is_list, shape = _get_unit_type(args[0])

        for metadata in args[1:]:
            candidate = _shape_spec(metadata)

            if candidate is not None:
                if shape is not None:
                    raise TypeError(
                        "A unit annotation can contain only one shape marker."
                    )

                shape = candidate

        return unit_type, is_optional, is_list, shape

    if origin in (Union, UnionType):
        non_none = [argument for argument in args if argument is not type(None)]

        if len(non_none) == 1:
            unit_type, _, is_list, shape = _get_unit_type(non_none[0])

            if unit_type is not None:
                return unit_type, True, is_list, shape

        return None, False, False, None

    if origin in (list, tuple):
        if len(args) == 1:
            unit_type, is_optional, _, shape = _get_unit_type(args[0])

            if unit_type is not None:
                return unit_type, is_optional, True, shape

        return None, False, False, None

    if inspect.isclass(hint) and issubclass(hint, BaseUnit):
        return hint, False, False, None

    return None, False, False, None


def unit_validator(function: Callable[..., Any]) -> Callable[..., Any]:
    """Validate parameter quantities against unit and optional shape annotations.

    Annotate parameters with a :class:`BaseUnit` subclass to validate units.
    Subscript the unit with :class:`Scalar`, :class:`Vector`, or
    :class:`Matrix` to also validate magnitude rank. Fixed dimensions are
    available as ``Vector[n]`` and ``Matrix[rows, columns]``.

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
        If an annotated argument has incompatible units or does not match its
        required shape.
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

            unit_type, is_optional, is_list, shape = _get_unit_type(
                hints[parameter_name]
            )

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

        return function(*args, **kwargs)

    return wrapper


validate_units = unit_validator


__all__ = ["unit_validator", "validate_units"]
