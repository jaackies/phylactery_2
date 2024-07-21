import datetime
from django import forms
from django.utils.text import slugify
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from members.models import RankChoices


class ControlPanelForm(forms.Form):
	"""
	Base class for a Control Panel Form
	
	Subclasses must define the following:
		Attributes:
			form_name:
				Human-readable name for the form.
				Will be displayed in the list view and detail view.
				The slug value of the form_name will also be used internally.
			form_short_description:
				Human-readable short description of what the form does.
				Will be displayed in the list view.
			form_long_description:
				Optional human-readable long description of what the form does.
				If not provided, the short description will be used instead.
				Will be displayed only in the detail view.
			form_allowed_ranks:
				A whitelist of ranks that are allowed to access the form.
		
		Methods:
			get_layout(self):
				Returns the Crispy layout used for the form.
			submit(self, request):
				Processes the form.
	"""
	
	form_name: str | None = None
	form_short_description: str | None = None
	form_long_description: str | None = None
	form_allowed_ranks: list = []
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		if self.form_name is None:
			raise NotImplemented
		if self.form_short_description is None:
			raise NotImplemented
		if self.form_long_description is None:
			self.form_long_description = self.form_short_description
		
		self.slug_name = slugify(self.form_name)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.include_media = False
		
		self.helper.layout = self.get_layout()
	
	def get_layout(self):
		raise NotImplemented
	
	def submit(self, request):
		raise NotImplemented
	

class GatekeeperWebkeeperPurgeForm(ControlPanelForm):
	form_name = "Purge Gatekeepers / Webkeepers"
	form_short_description = "Expire the Gatekeeper and/or Webkeeper rank of all non-Committee members"
	form_long_description = ""
	form_allowed_ranks = [
		RankChoices.PRESIDENT,
		RankChoices.VICEPRESIDENT,
		RankChoices.SECRETARY
	]
	
	CHOICES = (
		("gatekeeper", "Gatekeepers only"),
		("webkeeper", "Webkeepers only"),
		("both", "Both Gatekeepers and Webkeepers")
	)
	
	purge_choice = forms.ChoiceField(
		choices=CHOICES,
		label="Purge the status of:",
		widget=forms.RadioSelect(),
		required=True,
	)
	
	def get_layout(self):
		return Layout(
			Field("purge_choice"),
		)
	
	def submit(self, request):
		if self.is_valid():
			# Expire the chosen ranks
			print("Valid!")


class ExpireMembershipsForm(ControlPanelForm):
	form_name = "Invalidate Memberships"
	form_short_description = "Expires any active memberships purchased before a given date."
	form_allowed_ranks = [
		RankChoices.PRESIDENT,
		RankChoices.VICEPRESIDENT,
		RankChoices.SECRETARY,
	]
	
	cut_off_date = forms.DateField(
		label="Invalidate memberships purchased before:",
		required=True,
		widget=forms.DateInput(
			attrs={
				"type": "date"
			}
		),
		initial=datetime.date.today().replace(day=1, month=1)
	)
	
	def get_layout(self):
		return Layout(
			Field("cut_off_date"),
		)
	
	def submit(self, request):
		if self.is_valid():
			print("Valid!")


FORM_CLASSES = {}
for form_class in (
	GatekeeperWebkeeperPurgeForm,
	ExpireMembershipsForm,
):
	FORM_CLASSES[slugify(form_class.form_name)] = form_class
