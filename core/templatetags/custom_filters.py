import re
from django import template
from urllib.parse import urlparse, parse_qs

register = template.Library()

@register.filter
def youtube_embed(url):
    """
    Extracts the 11-character YouTube video ID and returns the embed URL.
    Handles various YouTube URL formats.
    """
    if not url:
        return ''

    # regex for youtube video id
    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(regex, url)

    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return url

@register.filter
def replace(value, arg):
    """
    Replaces all values of arg from the given string with a new_value.
    Usage: {{ string|replace:"old_val,new_val" }}
    """
    try:
        old, new = arg.split(',')
        return value.replace(old, new)
    except ValueError:
        return value
