from TypedUnit.units import BaseUnit
from typing import get_type_hints, get_origin, get_args, Union
import inspect

def _get_unit_type(hint):
    """Extract BaseUnit type from hint, handling Optional and List."""
    # Direct BaseUnit subclass
    if inspect.isclass(hint) and issubclass(hint, BaseUnit):
        return hint, False, False  # (unit_type, is_optional, is_list)

    origin = get_origin(hint)
    args = get_args(hint)

    if origin is Union:
        # Handle Optional[BaseUnit] (Union[BaseUnit, None])
        unit_types = [arg for arg in args if arg is not type(None)]
        if len(unit_types) == 1 and inspect.isclass(unit_types[0]) and issubclass(unit_types[0], BaseUnit):
            return unit_types[0], True, False  # Optional BaseUnit

    elif origin in (list, tuple):
        # Handle List[BaseUnit] or Tuple[BaseUnit]
        if len(args) == 1 and inspect.isclass(args[0]) and issubclass(args[0], BaseUnit):
            return args[0], False, True  # List of BaseUnit

    return None, False, False

def validate_units(function):
    def wrapper(*args, **kwargs):
        hints = get_type_hints(function)
        sig = inspect.signature(function)

        # Bind arguments to get parameter names
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for param_name, value in bound_args.arguments.items():
            if param_name not in hints:
                continue

            hint = hints[param_name]
            unit_type, is_optional, is_list = _get_unit_type(hint)

            if unit_type is None:
                continue  # No unit validation needed

            # Handle None values for Optional types
            if value is None and is_optional:
                continue
            elif value is None and not is_optional:
                raise ValueError(f"Parameter '{param_name}' cannot be None")

            # Handle List/Tuple types
            if is_list:
                for i, item in enumerate(value):
                    try:
                        unit_type.check(item)
                    except (AssertionError, ValueError) as e:
                        raise ValueError(f"Parameter '{param_name}[{i}]': {e}")
            else:
                # Handle single values
                try:
                    unit_type.check(value)
                except (AssertionError, ValueError) as e:
                    raise ValueError(f"Parameter '{param_name}': {e}")

        return function(*args, **kwargs)
    return wrapper