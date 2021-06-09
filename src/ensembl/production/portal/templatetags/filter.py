from django import template

register = template.Library()


@register.filter(name='split')
def split(value, key):
    """
      Returns the value turned into a list.
    """
    return value.split(key)


@register.filter(name='app_path')
def app_path(value):
    """
    Return the app path (remove path)
    :param value:
    :return:
    """
    splitted = value.split('/')
    return '/'.join(splitted[3:])
