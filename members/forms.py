from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Div, Submit
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, PrependedText


class MembershipForm1(forms.Form):
	short_name = forms.CharField(
		required=True,
		max_length=100,
		help_text=
		"The name you want to be called by others. Please don't dead-name yourself.<br>"
		"This is usually your first name, but it doesn't have to be.<br>"
		"Examples: Alistair, Jackie, Winslade, Gozz"
	)
	long_name = forms.CharField(
		required=True,
		max_length=200,
		help_text=
		"A longer version of your name, to distinguish between people who may share your shortname.<br>"
		"This will usually your full name, but it doesn't have to be. Please don't dead-name yourself.<br>"
		"Examples: Alistair Langton, Jackie S, Matthew Winslade, Andrew Gozzard"
	)
	pronouns = forms.CharField(
		required=True,
		max_length=50,
	)
	is_guild = forms.BooleanField(
		required=False,
		label="Are you a current UWA Student Guild member?"
	)
	is_student = forms.BooleanField(
		required=False,
		label="Are you a current UWA Student?"
	)
	student_number = forms.CharField(
		required=False,
		widget=forms.TextInput(attrs={"type": "tel"}),
		max_length=10,
		label="If so, please enter your student number."
	)
	optional_emails = forms.BooleanField(
		required=False,
		label="Would you like to receive email from Unigames about news and events?"
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		# noinspection PyTypeChecker
		self.helper.layout = Layout(
			Div(
				Fieldset(
					'Become a member of Unigames!',
					'short_name',
					'long_name',
					FieldWithButtons(
						'pronouns',
						StrictButton(
							"He / Him",
							css_class="btn-outline-secondary",
							onclick='$("#pronounField").val("He / Him")'
						),
						StrictButton(
							"She / Her",
							css_class="btn-outline-secondary",
							onclick='$("#pronounField").val("She / Her")'
						),
						StrictButton(
							"They / Them",
							css_class="btn-outline-secondary",
							onclick='$("#pronounField").val("They / Them")'
						),
					),
					'is_student',
					'student_number',
					'is_guild',
					'email',
					'receive_emails',
				),
			)
		)
