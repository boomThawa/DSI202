from django import template
import math

register = template.Library()

@register.filter
def floor(value):
    try:
        return math.floor(value)
    except (ValueError, TypeError):
        return value
