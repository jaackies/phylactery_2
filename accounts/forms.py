from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UnigamesUser
from allauth.account.forms import AddEmailForm
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


class UnigamesEmailChangeForm(AddEmailForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.layout = Layout(
			"email"
		)
