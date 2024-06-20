from django.db import models


class BlogPost(models.Model):
	"""
	A model for Blog Posts.
	Each one represents a single post.
	"""
	
	title = models.CharField(
		max_length=200,
		help_text="The title of this Blog Post."
	)
	slug_title = models.SlugField(
		max_length=200,
		unique=True,
		help_text="An automatically generated, URL-safe title. Generally you don't edit these once the post is created.",
	)
	author = models.CharField(
		max_length=200,
		help_text="The author of the post. (e.g. 'Donald Sutherland', or 'Unigames Committee')",
	)
	publish_on = models.DateTimeField(
		blank=True,
		null=True,
		default=None,
		help_text="The date and time at which the post will become published. "
		"If this is set to a future date, the post will be hidden until then."
	)
	body = models.TextField(
		blank=True,
		help_text="The body of the post. Markdown enabled."
	)
	
	
class MailingList(models.Model):
	"""
	Previously called MemberFlags - Members can self-assign these to "subscribe" to various mailing lists.
	Blog Post writers can email them out to all Members in one or more of these lists.
	"""
	name = models.CharField(
		max_length=20,
		help_text="The name for this Mailing List. e.g. Magic, Wargaming, 2023 Freshers, etc."
	)
	description = models.CharField(
		max_length=200,
		help_text="A brief description of the mailing list. e.g. News about Major Unigames events."
	)
	verbose_description = models.CharField(
		max_length=200,
		help_text="This text will appear as a prompt on the Membership forms. e.g. 'I want to receive news about MtG events.'"
	)
	is_active = models.BooleanField(
		default=True,
		help_text="This controls whether people are able to subscribe to this group."
	)
	
	members = models.ManyToManyField(
		to="members.Member",
		related_name="mailing_lists",
	)
	
	def __str__(self):
		return f"{self.name} {'(inactive)' if self.is_active is False else ''}"
	
