from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(is_safe=True)
def is_empty(value):
    """Return True if value is considered empty/NaN for display purposes.

    Treat None, empty strings, strings equal to 'nan' (case-insensitive) and
    strings consisting only of whitespace as empty.
    """
    if value is None:
        return True
    try:
        # If it's a float NaN
        import math
        if isinstance(value, float) and math.isnan(value):
            return True
    except Exception:
        pass

    if isinstance(value, str):
        if value.strip() == '' or value.strip().lower() == 'nan':
            return True

    return False