from TypedUnit.units import BaseUnit

from typing import get_type_hints

def validate_units(function):
    def wrapper(*args, **kwargs):
        hints = get_type_hints(function)

        for arg, hint in zip(args, hints.values()):
            if isinstance(hint, BaseUnit):
                hint.check(arg)

        for kwarg_name, kwarg_value in kwargs.items():
            if kwarg_name in hints:
                hint = hints[kwarg_name]
                if issubclass(hint, BaseUnit):
                    hint.check(kwarg_value)

        return function(*args, **kwargs)
    return wrapper