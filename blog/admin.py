from django.contrib import admin
from .models import MailingList


class MailingListAdmin(admin.ModelAdmin):
	model = MailingList
	exclude = ["members"]


admin.site.register(MailingList, MailingListAdmin)
