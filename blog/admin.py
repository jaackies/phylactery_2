from django.contrib import admin
from .models import MailingList, BlogPost


class BlogPostAdmin(admin.ModelAdmin):
	model = BlogPost


class MailingListAdmin(admin.ModelAdmin):
	model = MailingList
	exclude = ["members"]


admin.site.register(MailingList, MailingListAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
