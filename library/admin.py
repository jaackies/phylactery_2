from django.contrib import admin
from django import forms
from dal.forms import FutureModelForm
from dal_select2_taggit.widgets import TaggitSelect2

from .models import Item, LibraryTag


class ItemModelForm(FutureModelForm):
	class Meta:
		model = Item
		fields = [
			"name", "slug",
			"image",
			"description", "condition", "notes",
			"base_tags", "computed_tags",
			"min_players", "max_players",
			"min_play_time", "max_play_time", "average_play_time",
			"is_borrowable", "is_high_demand"
		]
		widgets = {
			"description": forms.Textarea(
				attrs={
					"style": "font-family: monospace; width: 100%;",
					
				}
			),
			"notes": forms.Textarea(
				attrs={
					"style": "font-family: monospace; width: 100%;",
					
				}
			),
			"condition": forms.Textarea(
				attrs={
					"style": "font-family: monospace; width: 100%;",
					
				}
			),
			"base_tags": TaggitSelect2(
				url="autocomplete-tag",
				attrs={
					"style": "width: 100%;",
				}
			),
		}
		help_texts = {
			"computed_tags": ""
		}


class ItemAdmin(admin.ModelAdmin):
	form = ItemModelForm
	prepopulated_fields = {"slug": ("name",)}
	readonly_fields = ["computed_tags"]


admin.site.register(Item, ItemAdmin)
admin.site.register(LibraryTag)
