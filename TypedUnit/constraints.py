"""Value-constraint markers for unit annotations."""


class Float:
    """Marker requiring a real floating-point magnitude."""


class Finite:
    """Marker requiring every magnitude to be finite."""


class NonZero:
    """Marker requiring every magnitude to be nonzero."""


class Positive:
    """Marker requiring every magnitude to be strictly positive."""


class Negative:
    """Marker requiring every magnitude to be strictly negative."""


__all__ = ["Finite", "Float", "Negative", "NonZero", "Positive"]
