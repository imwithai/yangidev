from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all values of arg from the given string with a new_value.
    Usage: {{ string|replace:"old_val,new_val" }}
    """
    try:
        old, new = arg.split(',')
        return value.replace(old, new)
    except ValueError:
        return value
