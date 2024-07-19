from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UnigamesUser
from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import filter_users_by_email
from allauth.account.forms import AddEmailForm, UserForm
from allauth.account.models import EmailAddress
from allauth.socialaccount.forms import DisconnectForm
from allauth.socialaccount.models import SocialAccount
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset


class UnigamesUserCreationForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = UnigamesUser
		fields = ('email', 'username',)


class UnigamesUserChangeForm(UserChangeForm):
	class Meta:
		model = UnigamesUser
		fields = ('email', 'username',)


class SocialAccountModelChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return f"{obj.get_provider_account().get_brand()['name']}: {obj.get_provider_account()}"


class UnigamesDisconnectForm(DisconnectForm):
	account = SocialAccountModelChoiceField(
		queryset=SocialAccount.objects.none(),
		widget=forms.RadioSelect,
		required=True,
		label="",
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.layout = Layout(
			"account",
		)


class PrototypeEmailChangeForm(UserForm):
	current_email = forms.EmailField(
		label="Current Email",
		required=False,
		disabled=True,
		widget=forms.TextInput(
			attrs={
				"type": "email"
			}
		)
	)
	new_email = forms.EmailField(
		label="New Email",
		required=True,
		widget=forms.TextInput(
			attrs={
				"type": "email",
				"placeholder": "New Email Address"
			}
		)
	)
	
	def clean_new_email(self):
		from allauth.account import signals
		
		value = self.cleaned_data["new_email"].lower()
		adapter = get_adapter()
		value = adapter.clean_email(value)
		users = filter_users_by_email(value)
		on_this_account = [u for u in users if u.pk == self.user.pk]
		on_diff_account = [u for u in users if u.pk != self.user.pk]
		
		if on_this_account:
			raise adapter.validation_error("duplicate_email")
		if on_diff_account:
			raise adapter.validation_error("email_taken")
		if not EmailAddress.objects.can_add_email(self.user):
			raise adapter.validation_error(
				"max_email_addresses", app_settings.MAX_EMAIL_ADDRESSES
			)
		
		signals._add_email.send(
			sender=self.user.__class__,
			email=value,
			user=self.user,
		)
		
		return value
		

class UnigamesEmailChangeForm(AddEmailForm):
	current_email_address = forms.EmailField(
		label="Current Email",
		required=False,
		disabled=True,
		widget=forms.TextInput(
			attrs={
				"type": "email"
			}
		)
	)
	
	email = forms.EmailField(
		label="New Email Address",
		required=True,
		widget=forms.TextInput(
			attrs={
				"type": "email",
				"placeholder": "New Email Address"
			}
		),
	)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.layout = Layout(
			"email"
		)
