from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Div
from crispy_forms.bootstrap import StrictButton

from blog.models import MailingList


class FresherMembershipForm(forms.Form):
	"""
	Base Membership Form, used when signing Freshers up to the club.
	The form's layout is handled by `crispy_forms`, and is configured in the __init__ method.
	"""
	short_name = forms.CharField(
		required=True,
		max_length=100,
		help_text=
		"The name you want to be called by others. <strong>Please don't dead-name yourself.</strong><br>"
		"This is usually your <mark>first name</mark>, but it doesn't have to be.<br>"
		"Examples: Alistair, Jackie, Winslade, Gozz"
	)
	long_name = forms.CharField(
		required=True,
		max_length=200,
		help_text=
		"A longer version of your name, to distinguish between people who may share your shortname.<br>"
		"This will usually be your <mark>full name</mark>, but it doesn't have to be. "
		"<strong>Please don't dead-name yourself.</strong><br>"
		"Examples: Alistair Langton, Jackie S, Matt Winslade, Andrew Gozzard"
	)
	pronouns = forms.CharField(
		required=True,
		max_length=50,
		label="Pronouns (type your own, or use one of the options below)",
		widget=forms.TextInput(
			attrs={"id": "pronounField", "placeholder": "Type your own here"}
		),
	)
	email_address = forms.EmailField(
		required=True,
		help_text="Please enter a non-student email address."
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
		label="Would you like to receive email from Unigames about news and events?",
		help_text=
		"(We will still send you transactional email regardless. "
		"For example, we will send you emails reminding you to return library items.)",
	)
	
	def __init__(self, *args, **kwargs):
		"""
		This initialises the form with two major changes:
		1) It uses `crispy_forms` to define the layout for the form.
		2) It dynamically adds fields to the form to allow the member to sign up for any active mailing lists.
		"""
		super().__init__(*args, **kwargs)
		self.extra_fields = []
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
						css_class="btn-group w-100 mb-3"
					),
					'email_address',
					'is_guild',
					'is_student',
					'student_number',
					'optional_emails',
					Div(css_class="ms-5"),
				),
			)
		)
		
		for mailing_list in MailingList.objects.filter(is_active=True):
			# Dynamically put each Mailing List group in the Membership Form.
			field_name = f"mailing_list_{mailing_list.pk}"
			self.extra_fields.append(mailing_list.pk)
			self.fields[field_name] = forms.BooleanField(
				label=mailing_list.verbose_description,
				required=False,
			)
			self.helper.layout[0][0][-1].append(field_name)
	
	def clean(self):
		"""
		This is the error-checking step.
		Currently, this is checking for:
			- any student emails (not allowed)
			- making sure a student number is required if they are a student, and
			- making sure the student number is blank if they aren't a student.
		"""
		cleaned_data = super().clean()
		email_address = cleaned_data.get("email_address")
		is_student = cleaned_data.get("is_student")
		student_number = cleaned_data.get("student_number")
		
		if email_address is not None and "@student." in email_address:
			self.add_error('email_address', 'Please enter a non-student email')
		if is_student and not student_number:
			self.add_error('student_number', 'If you are a current student, a student number is required.')
		if not is_student and student_number != "":
			self.add_error('is_student', '')
			self.add_error(
				'student_number', 'If you are not a student, then please leave the student number field blank.'
			)


class StaleMembershipForm(FresherMembershipForm):
	"""
	If a member already has data on our system, and they want to purchase a new membership,
	they would be using this form.
	We dynamically pre-fill data in the form, which they can update if they wish.
	Layout and fields are inherited from FresherMembershipForm
	"""
	pass


class LegacyMembershipForm(FresherMembershipForm):
	"""
	If a member was previously a Unigames member, but hasn't given us data digitally before,
	they would be using this form.
	It's identical to the Fresher Form except that:
		- The created member is not a fresher.
		- A field is added to allow the member to give their approximate join date.
	"""
	pass


class MembershipFormPreview(forms.Form):
	verified_correct = forms.BooleanField(
		required=True,
		label="I confirm that this information is correct to the best of my knowledge."
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.layout = Layout(
			HTML("{% include 'members/membership_form_gatekeeper_snippet.html' %}"),
			Div(
				'verified_correct',
			)
		)
