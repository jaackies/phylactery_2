from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import UnigamesUserCreationForm, UnigamesUserChangeForm
from .models import UnigamesUser


class UnigamesUserAdmin(UserAdmin):
	add_form = UnigamesUserCreationForm
	form = UnigamesUserChangeForm
	model = UnigamesUser
	list_display = ['email', 'username', ]


admin.site.register(UnigamesUser, UnigamesUserAdmin)
