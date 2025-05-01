from django import template

register = template.Library()

@register.filter
def get_systolic(blood_pressure):
    """Extract systolic value from blood pressure string"""
    try:
        return int(blood_pressure.split('/')[0])
    except (ValueError, IndexError, AttributeError):
        return 0

@register.filter
def format_date(date):
    """Format date in a consistent way"""
    if date:
        return date.strftime("%B %d, %Y, %I:%M %p")
    return "" 