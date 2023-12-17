from django.contrib import admin

from .models import Item, LibraryTag

admin.site.register(Item)
admin.site.register(LibraryTag)