from django import forms
from django.utils.text import slugify
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class ControlPanelForm(forms.Form):
	"""
	Base class for a Control Panel Form
	Attributes:
		form_name:
			Human-readable name for the form.
			Will be displayed in the list view and detail view.
			The slug value of the form_name will also be used internally.
		form_short_description:
			Human-readable short description of what the form does.
			Will be displayed in the list view.
		form_long_description:
			Human-readable long description of what the form does.
			Will be displayed only in the detail view.
		form_allowed_ranks:
			A whitelist of ranks that are allowed to access the form.
	
	Methods:
		get_layout():
			Returns the Crispy layout used for the form.
		submit():
			Processes the form.
	"""
	
	form_name = ""
	form_short_description = ""
	form_long_description = ""
	form_allowed_ranks = []
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.slug_name = slugify(self.form_name)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.include_media = False
		
		self.helper.layout = self.get_layout()
	
	def get_layout(self):
		raise NotImplemented
	
	def submit(self):
		raise NotImplemented
	