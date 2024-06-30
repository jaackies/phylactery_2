from markdown2 import Markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
@stringfilter
def render_markdown(raw_text: str):
	"""
	A template tag.
	Uses the markdown2 library to convert markdown formatted text into html.
	
	Usage in a template:
	{% load markdown_extras %}
	{{ text_to_render|render_markdown }}
	"""
	markdown_renderer = Markdown()
	output_html = markdown_renderer.convert(raw_text)
	return mark_safe(output_html)
