from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UnigamesUser
from allauth.account.forms import AddEmailForm
from allauth.account.models import EmailAddress
from allauth.socialaccount.forms import DisconnectForm
from allauth.socialaccount.models import SocialAccount
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML
from crispy_forms.bootstrap import StrictButton


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
	display_verified_email_address = forms.EmailField(
		label="Current Email",
		required=False,
		disabled=True,
		widget=forms.TextInput(
			attrs={
				"type": "email"
			}
		)
	)
	
	display_pending_email_address = forms.EmailField(
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
		
		pending_email_address = EmailAddress.objects.get_new(self.user)  # An email attached to the user, but not verified
		verified_email_address = EmailAddress.objects.get_verified(self.user)  # A currently verified email
		
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.layout = Layout()
		
		if verified_email_address:
			self.initial.update({"display_verified_email_address": verified_email_address.email})
			self.fields["display_pending_email_address"].label = "Changing to"
			self.helper.layout.append(Field("display_verified_email_address"))
		if pending_email_address:
			self.initial.update({"display_pending_email_address": pending_email_address.email})
			self.helper.layout.append(Field("display_pending_email_address"))
			button_holder = Div(
				HTML("This email address is still pending verification. <hr>"),
				css_class="alert alert-warning"
			)
			button_holder.append(
				StrictButton(
					name="action_send",
					content="Resend Verification",
					type="submit",
					form="pending-email",
					css_class="btn-secondary"
				)
			)
			if verified_email_address:
				button_holder.append(
					StrictButton(
						name="action_remove",
						content="Cancel Change",
						type="submit",
						form="pending-email",
						css_class="btn-danger"
					)
				)
			self.helper.layout.append(button_holder)
		self.helper.layout.append(Field("email"))
