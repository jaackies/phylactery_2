from django.contrib import admin
from django.db import models
from django.forms.widgets import Textarea
from .models import MailingList, BlogPost


class MarkdownWidget(Textarea):
	"""
	Custom widget for Markdown fields.
	Sets the font to a monospace font and the width to 100%.
	"""
	def __init__(self):
		super().__init__(attrs={"style": "width: 100%; font-family: monospace, monospace;"})


class BlogPostAdmin(admin.ModelAdmin):
	model = BlogPost
	
	# Set the slug field to generate automatically from the title.
	prepopulated_fields = {"slug_title": ("title",)}
	
	# Set the TextFields to use our custom widget.
	formfield_overrides = {
		models.TextField: {"widget": MarkdownWidget}
	}


class MailingListAdmin(admin.ModelAdmin):
	model = MailingList
	exclude = ["members"]


admin.site.register(MailingList, MailingListAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
