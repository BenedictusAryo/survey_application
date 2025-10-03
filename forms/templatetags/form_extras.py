from django import template
from django.utils.safestring import mark_safe
import json
import re

register = template.Library()

@register.simple_tag
def get_record_display(attachment, record):
    """Get the display value for a record based on attachment configuration."""
    return attachment.get_record_display_value(record)

@register.filter
def record_display(record, attachment):
    """Filter version of get_record_display."""
    return attachment.get_record_display_value(record)

@register.filter
def json_script(value):
    """Safely convert Python data to JavaScript JSON."""
    return json.dumps(value)

@register.filter
def dict_get(dictionary, key):
    """
    Get a value from a dictionary using a key.
    Usage: {{ my_dict|dict_get:key_variable }}
    """
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)

@register.filter
def urlize_target_blank(text):
    """
    Convert URLs in text to clickable links that open in a new tab.
    This ensures the form stays open when users click external links.
    """
    if not text:
        return text
    
    # Regular expression to match URLs
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    def replace_url(match):
        url = match.group(0)
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer" class="text-primary underline hover:text-primary-focus transition-colors">{url}</a>'
    
    # Replace URLs with clickable links
    text_with_links = url_pattern.sub(replace_url, text)
    
    return mark_safe(text_with_links)