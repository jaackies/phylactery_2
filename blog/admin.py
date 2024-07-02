from django.contrib import admin
from .models import MailingList, BlogPost


class BlogPostAdmin(admin.ModelAdmin):
	model = BlogPost
	prepopulated_fields = {"slug_title": ("title",)}


class MailingListAdmin(admin.ModelAdmin):
	model = MailingList
	exclude = ["members"]


admin.site.register(MailingList, MailingListAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
