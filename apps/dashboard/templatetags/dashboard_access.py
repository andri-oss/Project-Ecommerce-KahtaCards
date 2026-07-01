from django import template

register = template.Library()


@register.filter(name='has_menu_access')
def has_menu_access(user, menu_key):
    if not getattr(user, 'is_authenticated', False):
        return False
    return user.has_menu_access(menu_key)


@register.filter(name='get_item')
def get_item(mapping, key):
    """Safe dict-like lookup for templates — returns '' instead of raising VariableDoesNotExist."""
    if mapping is None:
        return ''
    try:
        return mapping.get(key, '')
    except AttributeError:
        return ''
