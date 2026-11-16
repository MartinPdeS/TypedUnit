"""Decorators that validate unit and shape annotations at runtime."""

import inspect
from collections.abc import Callable
from functools import wraps
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin, get_type_hints

import numpy as np

from TypedUnit.constraints import Finite, Float, Negative, NonZero, Positive
from TypedUnit.shapes import Matrix, Scalar, ShapeSpec, Vector
from TypedUnit.units import BaseUnit, NoUnit, Quantity


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
    tuple[type[BaseUnit] | type[NoUnit], ...] | None,
    bool,
    bool,
    ShapeSpec | None,
    bool,
    bool,
    bool,
    tuple[frozenset[type], ...],
]:
    """Extract accepted types, optionality, shape, and value constraints."""
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
        optional = len(non_none) != len(args)
        contracts = [_get_unit_type(argument) for argument in non_none]

        if not contracts:
            return None, False, False, None, False, False, False, ()

        contract_types: list[tuple[type[BaseUnit] | type[NoUnit], ...]] = []

        for contract in contracts:
            candidate_types = contract[0]

            if candidate_types is None:
                return None, False, False, None, False, False, False, ()

            contract_types.append(candidate_types)

        first = contracts[0]

        if len(contracts) == 1:
            return (
                first[0],
                True,
                first[2],
                first[3],
                first[4],
                first[5],
                first[6],
                first[7],
            )

        compatible = all(
            not contract[1] and not contract[2] and contract[3:] == first[3:]
            for contract in contracts[1:]
        )

        if not compatible or first[1] or first[2]:
            return None, False, False, None, False, False, False, ()

        unit_types = tuple(
            dict.fromkeys(
                unit_type for candidates in contract_types for unit_type in candidates
            )
        )

        return (
            unit_types,
            optional,
            False,
            first[3],
            first[4],
            first[5],
            first[6],
            first[7],
        )

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

    if hint is NoUnit:
        return (NoUnit,), False, False, None, False, False, False, ()

    if inspect.isclass(hint) and issubclass(hint, BaseUnit):
        return (hint,), False, False, None, False, False, False, ()

    return None, False, False, None, False, False, False, ()


def validate_annotation(value: Any, *, annotation: Any, name: str) -> None:
    """Validate one value directly against a TypedUnit annotation.

    Parameters
    ----------
    value : Any
        Value to validate.
    annotation : Any
        Unit, no-unit, optional, collection, shape, or value-constraint
        annotation supported by :func:`unit_validator`.
    name : str
        Name used in validation errors.

    Returns
    -------
    None
        The value is validated without being modified.

    Raises
    ------
    TypeError
        If ``annotation`` is not supported by TypedUnit.
    ValueError
        If ``value`` does not satisfy the annotation.
    """
    (
        unit_types,
        is_optional,
        is_list,
        shape,
        requires_float,
        requires_finite,
        requires_nonzero,
        sign_groups,
    ) = _get_unit_type(annotation)

    if unit_types is None:
        raise TypeError(f"Unsupported TypedUnit annotation: {annotation!r}.")

    if value is None:
        if is_optional:
            return None

        raise ValueError(f"Parameter '{name}' cannot be None")

    values = value if is_list else (value,)

    for index, item in enumerate(values):
        item_name = f"{name}[{index}]" if is_list else name

        unitless_allowed = NoUnit in unit_types
        quantity_types: list[type[BaseUnit]] = []

        for candidate in unit_types:
            if candidate is NoUnit or not issubclass(candidate, BaseUnit):
                continue

            quantity_types.append(candidate)

        if isinstance(item, Quantity):
            if unitless_allowed and not quantity_types:
                raise ValueError(f"Parameter '{item_name}' must not have units.")

            compatible_unit = False

            for candidate in quantity_types:
                try:
                    candidate.check(item)
                except (AssertionError, ValueError, TypeError):
                    continue

                compatible_unit = True

                break

            if not compatible_unit:
                expected = " or ".join(
                    candidate.__name__ for candidate in quantity_types
                )

                cause = AssertionError(f"Expected {expected}, got {item.units}")

                if unitless_allowed:
                    raise ValueError(
                        f"Parameter '{item_name}' must have units compatible with {expected}, or no units."
                    ) from cause

                raise ValueError(
                    f"Parameter '{item_name}' must have units compatible with {expected}."
                ) from cause

            magnitude = np.asarray(item.magnitude)
        elif unitless_allowed:
            magnitude = np.asarray(item)

            if not np.issubdtype(magnitude.dtype, np.number):
                raise ValueError(
                    f"Parameter '{item_name}' must be a bare numeric value."
                )
        else:
            expected = " or ".join(candidate.__name__ for candidate in quantity_types)
            raise ValueError(
                f"Parameter '{item_name}' must have units compatible with {expected}."
            )

        if shape is not None:
            actual_shape = tuple(magnitude.shape)

            if not shape.matches(actual_shape):
                raise ValueError(
                    f"Parameter '{item_name}' must have {shape}; got shape {actual_shape}."
                )

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
            np.iscomplexobj(magnitude) or not np.issubdtype(magnitude.dtype, np.number)
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


def unit_validator(function: Callable[..., Any]) -> Callable[..., Any]:
    """Validate parameter units, bare values, shapes, and value constraints.

    Annotate parameters with a :class:`BaseUnit` subclass to validate units, or
    with :class:`NoUnit` to require bare numeric values without Pint units.
    Compatible unions such as ``Dimensionless | NoUnit`` accept either form.
    Subscript these markers with shape markers and optional ``Float``,
    ``Finite``, ``NonZero``, ``Positive``, or ``Negative`` markers. For example,
    ``Watt[Float, Positive | Negative]`` requires a real floating-point value
    that is nonzero; ``NoUnit[Scalar, Float]`` accepts a bare floating-point
    scalar and rejects quantities and array magnitudes.

    Parameters
    ----------
    function : callable
        Function whose annotated parameters should be validated.
        If it has a string parameter named ``name``, that value is used to
        label validation errors.

    Returns
    -------
    callable
        Wrapped function that validates bound arguments before calling the
        original function. Return annotations are not validated.

    Raises
    ------
    ValueError
        If an annotated argument has incompatible units, is not a bare numeric
        value where required, or violates shape or value constraints.
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

            error_name = bound_arguments.arguments.get("name", parameter_name)

            if not isinstance(error_name, str):
                error_name = parameter_name

            if _get_unit_type(hints[parameter_name])[0] is None:
                continue

            validate_annotation(
                value,
                annotation=hints[parameter_name],
                name=error_name,
            )

        return function(*args, **kwargs)

    return wrapper


validate_units = unit_validator


__all__ = ["unit_validator", "validate_annotation", "validate_units"]
