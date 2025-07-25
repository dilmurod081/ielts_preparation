import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='format_text')
def format_text(value):
    # New Pattern for "text(bold/all/bigger-10px)" to make it bold and bigger
    value = re.sub(r'([\w\s]+)\(bold/all/bigger-(\d+)px\)', r'<strong style="font-size: \2px;">\1</strong>', value)

    # Pattern 1: Finds "DisplayName(URL)" and converts it to a link.
    value = re.sub(r'([\w\s]+)\((https?://[^\)]+)\)', r'<a href="\2" target="_blank">\1</a>', value)

    # Pattern for "i am a good boy(bold/all)" to make the whole phrase bold
    value = re.sub(r'([\w\s]+)\(bold/all\)', r'<strong>\1</strong>', value)

    # Pattern 2: Finds "word(bold)" and makes only that word bold.
    value = re.sub(r'(\w+)\(bold\)', r'<strong>\1</strong>', value)

    # Mark the final string as safe to render as HTML
    return mark_safe(value)
