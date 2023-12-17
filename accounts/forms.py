from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UnigamesUser

class UnigamesUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = UnigamesUser
        fields = ('email', 'username',)

class UnigamesUserChangeForm(UserChangeForm):

    class Meta:
        model = UnigamesUser
        fields = ('email', 'username',)