from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css_class):
    """Return a form field rendered with an extra CSS class.

    Usage in template:
        {{ form.city|add_class:"w-full rounded" }}

    This is a minimal replacement for the common `add_class` filter from
    `django-widget-tweaks` so the project doesn't need an extra dependency.
    """
    try:
        # `field` is a BoundField; use as_widget to inject attrs
        return field.as_widget(attrs={"class": css_class})
    except Exception:
        # If anything goes wrong, fail gracefully and return the original
        return field
