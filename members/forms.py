from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Div, Submit
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, PrependedText


class MembershipForm1(forms.Form):
	short_name = forms.CharField(
		required=True,
		max_length=100,
		help_text=
		"The name you want to be called by others. <b>Please don't dead-name yourself.</b><br>"
		"This is usually your first name, but it doesn't have to be.<br>"
		"Examples: Alistair, Jackie, Winslade, Gozz"
	)
	long_name = forms.CharField(
		required=True,
		max_length=200,
		help_text=
		"A longer version of your name, to distinguish between people who may share your shortname.<br>"
		"This will usually your full name, but it doesn't have to be. <b>Please don't dead-name yourself.</b><br>"
		"Examples: Alistair Langton, Jackie S, Matthew Winslade, Andrew Gozzard"
	)
	pronouns = forms.CharField(
		required=True,
		max_length=50,
		widget=forms.TextInput(
			attrs={"id": "pronounField", "placeholder": "Type your own here"}
		)
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
					'pronouns',
					Div(
						StrictButton(
							"He / Him",
							css_class="btn-outline-secondary",
							onclick='document.querySelector("#pronounField").setAttribute("value", "He / Him");'
						),
						StrictButton(
							"She / Her",
							css_class="btn-outline-secondary",
							onclick='document.querySelector("#pronounField").setAttribute("value", "She / Her");'
						),
						StrictButton(
							"They / Them",
							css_class="btn-outline-secondary",
							onclick='document.querySelector("#pronounField").setAttribute("value", "They / Them");'
						),
						StrictButton(
							"It / Its",
							css_class="btn-outline-secondary",
							onclick='document.querySelector("#pronounField").setAttribute("value", "It / Its");'
						),
						StrictButton(
							"Any",
							css_class="btn-outline-secondary",
							onclick='document.querySelector("#pronounField").setAttribute("value", "Any");'
						),
						css_class="btn-group"
					),
					'is_student',
					'student_number',
					'is_guild',
					'email',
					'receive_emails',
				),
			)
		)
