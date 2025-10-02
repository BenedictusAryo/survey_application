from django import template
import json

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