from django import template

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    try:
        if value is None:
            return "Rp 0"
        # Convert to float first to handle string representation of floats, then cast/round to int
        val = int(float(value))
        formatted = f"{val:,}".replace(",", ".")
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return value
