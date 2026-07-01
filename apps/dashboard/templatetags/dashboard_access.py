from django import template

register = template.Library()


@register.filter(name='has_menu_access')
def has_menu_access(user, menu_key):
    if not getattr(user, 'is_authenticated', False):
        return False
    return user.has_menu_access(menu_key)
