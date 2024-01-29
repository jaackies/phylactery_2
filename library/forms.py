from dal import autocomplete
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML

from .models import Item
from members.models import Member


class SelectLibraryItemsForm(forms.Form):
	"""
	Form to select library items, for the first step of the borrowing process.
	"""
	items = forms.ModelMultipleChoiceField(
		queryset=Item.objects.all(),
		widget=autocomplete.ModelSelect2Multiple(
			url="autocomplete-item",
			attrs={
				"data-theme": "bootstrap-5"
			}
		)
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.include_media = False
		# noinspection PyTypeChecker
		self.helper.layout = Layout(
			Fieldset(
				"Borrow Items",
				HTML("<p>Select items for the member to borrow. Member details will be filled out in the next step.</p>"),
				"items",
			)
		)


class ItemDueDateForm(forms.Form):
	"""
	Form to show and potentially change a due date when borrowing an item.
	One of these forms are displayed for each item selected in the preview step.
	"""
	item = forms.ModelChoiceField(
		widget=forms.HiddenInput,
		required=True,
		queryset=Item.objects.all(),
	)
	due_date = forms.DateField(
		required=True,
		widget=forms.DateInput(
			attrs={
				"type": "date"
			}
		)
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.layout = Layout(
			"item",
			"due_date",
		)
	
	def clean(self):
		cleaned_data = super().clean()
		item = cleaned_data["item"]
		due_date = cleaned_data["due_date"]
		item_availability = item.get_availability_info()
		if not item_availability["available_to_borrow"]:
			raise ValidationError(f"{item} is not available to borrow at the moment.")
		if due_date > item_availability["max_due_date"]:
			self.add_error(
				field="due_date",
				error=f"The due date can't be set beyond the maximum due date for this item. "
				f"({item_availability['max_due_date']}"
			)
		if due_date < timezone.now().date():
			self.add_error(
				field="due_date",
				error="Due date cannot be in the past."
			)


class InternalBorrowerDetailsForm(forms.Form):
	member = forms.ModelChoiceField(
		queryset=Member.objects.all(),
	)
	address = forms.CharField(
		widget=forms.Textarea(
			attrs={
				"rows": 3
			}
		),
		required=True,
	)
	phone_number = forms.CharField(
		widget=forms.TextInput(
			attrs={
				"type": "tel"
			},
		),
		required=True,
		max_length=20,
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.layout = Layout(
			Fieldset(
				"Enter the Member details below:",
				"member",
				"address",
				"phone_number",
			)
		)
	
	def clean_member(self):
		member = self.cleaned_data["member"]
		if not member.is_valid_member():
			raise ValidationError("This member cannot borrow items.")
