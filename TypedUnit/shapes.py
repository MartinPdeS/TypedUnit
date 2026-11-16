"""Array-shape markers for unit annotations."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ShapeSpec:
    """Describe an exact array rank with optional fixed dimensions.

    Parameters
    ----------
    dimensions : tuple of int or None
        Required dimension lengths. ``None`` accepts any length on that axis.
    """

    dimensions: tuple[int | None, ...]

    def __post_init__(self) -> None:
        """Reject invalid dimensions in a shape specification.

        Raises
        ------
        TypeError
            If ``dimensions`` is not a tuple or a fixed dimension is not an
            integer.
        ValueError
            If a fixed dimension is negative.
        """
        if not isinstance(self.dimensions, tuple):
            raise TypeError("Shape dimensions must be a tuple.")

        if any(
            dimension is not None
            and (isinstance(dimension, bool) or not isinstance(dimension, int))
            for dimension in self.dimensions
        ):
            raise TypeError("Shape dimensions must be integers or None.")

        if any(
            dimension is not None and dimension < 0 for dimension in self.dimensions
        ):
            raise ValueError("Shape dimensions must be nonnegative integers or None.")

    def matches(self, actual_shape: tuple[int, ...]) -> bool:
        """Return whether an observed shape satisfies this specification.

        Parameters
        ----------
        actual_shape : tuple of int
            Shape of the quantity magnitude.

        Returns
        -------
        bool
            True when rank and all fixed dimensions match.
        """
        return len(actual_shape) == len(self.dimensions) and all(
            expected is None or expected == actual
            for expected, actual in zip(self.dimensions, actual_shape, strict=True)
        )

    def __str__(self) -> str:
        """Return a readable rank and dimension description."""
        if not self.dimensions:
            return "scalar shape ()"

        if all(dimension is None for dimension in self.dimensions):
            return f"rank-{len(self.dimensions)} shape"

        dimensions = tuple(
            "*" if dimension is None else dimension for dimension in self.dimensions
        )
        return f"shape {dimensions}"


class Scalar:
    """Marker requiring a scalar quantity with a zero-dimensional magnitude."""


class Vector:
    """Marker requiring a one-dimensional quantity magnitude.

    ``Vector[n]`` specifies an exact vector length.
    """

    @classmethod
    def __class_getitem__(cls, length: Any) -> ShapeSpec:
        """Create a fixed-length vector shape specification.

        Parameters
        ----------
        length : int
            Required vector length.

        Returns
        -------
        ShapeSpec
            One-dimensional shape specification.
        """
        return ShapeSpec((length,))


class Matrix:
    """Marker requiring a two-dimensional quantity magnitude.

    ``Matrix[rows, columns]`` specifies exact matrix dimensions.
    """

    @classmethod
    def __class_getitem__(cls, dimensions: Any) -> ShapeSpec:
        """Create a fixed-dimension matrix shape specification.

        Parameters
        ----------
        dimensions : tuple of int
            Required row and column counts.

        Returns
        -------
        ShapeSpec
            Two-dimensional shape specification.

        Raises
        ------
        ValueError
            If dimensions do not specify exactly two axes.
        """
        if not isinstance(dimensions, tuple):
            dimensions = (dimensions,)

        if len(dimensions) != 2:
            raise ValueError("Matrix shape requires exactly two dimensions.")

        return ShapeSpec(dimensions)


__all__ = ["Matrix", "Scalar", "ShapeSpec", "Vector"]
