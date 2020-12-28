from django import template

register = template.Library()


@register.filter()
def percentof(n1, n2):
    try:
        return (float(n1) / float(n2)) * 100
    except (ZeroDivisionError, TypeError):
        return None
    # return '{0:.2%}'.format(value)
