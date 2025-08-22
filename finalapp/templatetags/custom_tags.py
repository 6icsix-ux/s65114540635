from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key)

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name)
