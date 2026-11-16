"""Unit and shape annotation validation."""

from typing import Optional

import numpy as np
import pint
import pytest

from TypedUnit import Matrix, Scalar, Vector, Watt, unit_validator, validate_units


def test_scalar_unit_annotation_checks_zero_dimensional_magnitude() -> None:
    """Scalar annotations enforce units and reject one-element arrays."""
    registry = pint.UnitRegistry()

    @unit_validator
    def identity(power: Watt[Scalar]) -> Watt[Scalar]:
        return power

    assert identity(2 * registry.watt) == 2 * registry.watt

    with pytest.raises(ValueError, match="scalar shape"):
        identity(np.array([2]) * registry.watt)

    with pytest.raises(ValueError, match="units compatible"):
        identity(2 * registry.second)


def test_vector_and_matrix_shape_annotations() -> None:
    """Rank and optional fixed dimensions are checked on quantity magnitudes."""
    registry = pint.UnitRegistry()

    @unit_validator
    def combine(vector: Watt[Vector[3]], matrix: Watt[Matrix[2, 3]]) -> None:
        assert vector.shape == (3,)
        assert matrix.shape == (2, 3)

    combine(np.arange(3) * registry.watt, np.ones((2, 3)) * registry.watt)

    with pytest.raises(ValueError, match=r"shape \(3,\)"):
        combine(np.arange(4) * registry.watt, np.ones((2, 3)) * registry.watt)

    with pytest.raises(ValueError, match=r"shape \(3,\)"):
        combine(np.ones((1, 3)) * registry.watt, np.ones((2, 3)) * registry.watt)

    with pytest.raises(ValueError, match=r"shape \(2, 3\)"):
        combine(np.arange(3) * registry.watt, np.ones((3, 2)) * registry.watt)


def test_unconstrained_vector_and_matrix_ranks() -> None:
    """Vector and Matrix markers constrain rank without fixing axis lengths."""
    registry = pint.UnitRegistry()

    @unit_validator
    def identity(vector: Watt[Vector], matrix: Watt[Matrix]) -> None:
        assert vector.ndim == 1
        assert matrix.ndim == 2

    identity(np.ones(5) * registry.watt, np.ones((2, 4)) * registry.watt)


def test_optional_and_list_unit_shapes() -> None:
    """Existing optional and list annotations compose with shape contracts."""
    registry = pint.UnitRegistry()

    @unit_validator
    def collect(values: list[Watt[Vector[2]]], maybe: Optional[Watt[Scalar]]) -> None:
        assert len(values) == 2
        assert maybe is None or maybe.ndim == 0

    collect([np.ones(2) * registry.watt, np.zeros(2) * registry.watt], None)

    with pytest.raises(ValueError, match=r"values\[1\]"):
        collect([np.ones(2) * registry.watt, np.ones(3) * registry.watt], None)


def test_pep604_optional_shape_annotation_and_invalid_marker() -> None:
    """PEP 604 optionals work, and malformed shape specifications fail early."""
    registry = pint.UnitRegistry()

    @unit_validator
    def maybe(value: Watt[Scalar] | None = None) -> Watt[Scalar] | None:
        return value

    assert maybe() is None
    assert maybe(1 * registry.watt) == 1 * registry.watt
    assert maybe(None) is None

    with pytest.raises(ValueError, match="exactly two"):
        Matrix[3]

    with pytest.raises(TypeError, match="integers"):
        Vector[True]


def test_unit_validator_preserves_function_metadata_and_legacy_alias() -> None:
    """The new spelling is introspection-safe and old decorator remains supported."""
    registry = pint.UnitRegistry()

    @unit_validator
    def identity(power: Watt) -> Watt:
        """Return power unchanged."""
        return power

    assert identity.__name__ == "identity"
    assert identity.__doc__ == "Return power unchanged."
    assert identity(3 * registry.watt) == 3 * registry.watt

    @validate_units
    def legacy_identity(power: Watt) -> Watt:
        return power

    assert legacy_identity(3 * registry.watt) == 3 * registry.watt
