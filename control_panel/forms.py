import datetime
from django import forms
from django.contrib import messages
from django.utils.text import slugify
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from members.models import Member, Rank, RankChoices


def expire_active_ranks(rank_to_expire, rank_to_exclude):
	"""
	Finds all ranks of the chosen type that are still active, and expires them.
	Ignores all ranks belonging to members that also have rank_to_exclude.
	Returns the names of Members with Ranks expired this way.
	"""
	members_to_exclude = Rank.objects.all_active().filter(rank_name=rank_to_exclude).values_list("member", flat=True)
	ranks_to_expire = Rank.objects.all_active().filter(rank_name=rank_to_expire).exclude(member__in=members_to_exclude)
	expired_members = list(ranks_to_expire.values_list("member__long_name", flat=True))
	for rank in ranks_to_expire:
		rank.set_expired()
	return expired_members


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
	
	form_confirm_field = forms.BooleanField(
		label="I confirm I wish to perform this action.",
		initial=False,
		required=True,
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		if self.form_name is None:
			raise NotImplemented
		if self.form_short_description is None:
			raise NotImplemented
		if self.form_long_description is None:
			self.form_long_description = self.form_short_description
		
		self.slug_name = slugify(self.form_name)
		self.prefix = self.slug_name
		
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
	form_short_description = "Expire the Gatekeeper and/or Webkeeper rank of all non-Committee members."
	form_allowed_ranks = [
		RankChoices.PRESIDENT,
		RankChoices.VICEPRESIDENT,
		RankChoices.SECRETARY,
		RankChoices.WEBKEEPER,
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
			purge_choice = self.cleaned_data["purge_choice"]
			if purge_choice in ["gatekeeper", "both"]:
				purged_gate = expire_active_ranks(
					rank_to_expire=RankChoices.GATEKEEPER,
					rank_to_exclude=RankChoices.COMMITTEE
				)
				if len(purged_gate) > 0:
					messages.success(
						request,
						message=f"Removed Gatekeeper from {len(purged_gate)} members: "
						f"{', '.join(purged_gate)}"
					)
				else:
					messages.warning(
						request,
						message="No non-committee gatekeepers to remove."
					)
			if purge_choice in ["webkeeper", "both"]:
				purged_web = expire_active_ranks(
					rank_to_expire=RankChoices.WEBKEEPER,
					rank_to_exclude=RankChoices.COMMITTEE
				)
				if len(purged_web) > 0:
					messages.success(
						request,
						message=f"Removed Webkeeper from {len(purged_web)} members: "
						f"{', '.join(purged_web)}"
					)
				else:
					messages.warning(
						request,
						message="No non-committee gatekeepers to remove."
					)


class ExpireMembershipsForm(ControlPanelForm):
	form_name = "Invalidate Memberships"
	form_short_description = "Expires any active memberships purchased before a given date."
	form_allowed_ranks = [
		RankChoices.PRESIDENT,
		RankChoices.VICEPRESIDENT,
		RankChoices.SECRETARY,
		RankChoices.WEBKEEPER,
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


class MakeGatekeepersForm(ControlPanelForm):
	form_name = "Promote Members to Gatekeepers"
	form_short_description = "Promotes the selected members to Gatekeepers."
	form_allowed_ranks = [
		RankChoices.PRESIDENT,
		RankChoices.VICEPRESIDENT,
		RankChoices.SECRETARY,
		RankChoices.WEBKEEPER,
	]
	
	gatekeepers_to_add = forms.ModelMultipleChoiceField(
		queryset=Member.objects.all(),
	)
	
	def get_layout(self):
		return Layout(
			"gatekeepers_to_add"
		)


class MakeWebkeepersForm(ControlPanelForm):
	form_name = "Promote Members to Webkeepers"
	form_short_description = "Promotes the selected members to Webkeepers."
	form_allowed_ranks = [
		RankChoices.PRESIDENT,
		RankChoices.VICEPRESIDENT,
		RankChoices.SECRETARY,
		RankChoices.WEBKEEPER,
	]
	
	webkeepers_to_add = forms.ModelMultipleChoiceField(
		queryset=Member.objects.all(),
	)
	
	def get_layout(self):
		return Layout(
			"webkeepers_to_add"
		)


class AddRemoveRanksForm(ControlPanelForm):
	form_name = "Selectively Add or Remove Ranks"
	form_short_description = (
		"Adds or Removes ranks for a single member. "
		"Useful for removing the Gatekeeper rank or adding the Excluded rank to a single member."
	)
	form_long_description = (
		"This form cannot be used for Committee Rank transferal. "
		"Use the Committee Transfer Form for that."
	)
	form_allowed_ranks = [
		RankChoices.PRESIDENT,
		RankChoices.VICEPRESIDENT,
		RankChoices.SECRETARY,
		RankChoices.WEBKEEPER,
	]
	
	def get_layout(self):
		return Layout()


class CommitteeTransferForm(ControlPanelForm):
	form_name = "Committee Transfer"
	form_short_description = "Freely transfer committee roles."
	form_allowed_ranks = [
		RankChoices.PRESIDENT,
		RankChoices.VICEPRESIDENT,
		RankChoices.WEBKEEPER,
	]
	
	def get_layout(self):
		return Layout()


class GetMembershipInfoForm(ControlPanelForm):
	form_name = "Get Membership CSV"
	form_short_description = "Get a CSV of membership data for a particular date. Useful for O-Day information."
	form_long_description = (
		"This will output a CSV containing the name, student number, and guild status "
		"of each membership purchased on the selected date."
	)
	form_allowed_ranks = [
		RankChoices.COMMITTEE,
		RankChoices.WEBKEEPER,
	]
	
	def get_layout(self):
		return Layout()
	
	

FORM_CLASSES = {}
for form_class in (
	GatekeeperWebkeeperPurgeForm,
	ExpireMembershipsForm,
	MakeGatekeepersForm,
	MakeWebkeepersForm,
	AddRemoveRanksForm,
	CommitteeTransferForm,
	GetMembershipInfoForm,
):
	FORM_CLASSES[slugify(form_class.form_name)] = form_class
