from django import template
from django.template.defaultfilters import stringfilter

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
	pass
