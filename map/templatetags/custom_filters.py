import re
from django import template

register = template.Library()

@register.filter
def normalize_phone(value):
    if not value:
        return ''
    return re.sub(r'\D', '', value)  # يشيل كل شيء غير رقم
