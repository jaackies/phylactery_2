from django.db.models import Count
from django.views.generic import DetailView, ListView
from django.utils import timezone
from datetime import timedelta
from .models import Item, LibraryTag


class ItemDetailView(DetailView):
	model = Item
	template_name = "library/item_detail_view.html"
	slug_field = "slug"
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["item_info"] = self.object.get_availability_info()
		if context["item_info"]["in_clubroom"] is False:
			today = timezone.now().date()
			tomorrow = today + timedelta(days=1)
			if context["item_info"]["expected_available_date"] not in [today, tomorrow]:
				context["available_str"] = ""
			elif context["item_info"]["expected_available_date"] == today:
				context["available_str"] = "today"
			elif context["item_info"]["expected_available_date"] == tomorrow:
				context["available_str"] = "tomorrow"
		context["item_types"] = self.object.base_tags.filter(is_item_type=True)
		return context


class ItemListView(ListView):
	model = Item
	template_name = "library/item_list_view.html"
	context_object_name = "items_list"
	paginate_by = 24
	

class TagListView(ListView):
	model = LibraryTag
	template_name = "library/tag_list_view.html"
	context_object_name = "tags_list"
	
	def get_queryset(self):
		qs = (
			LibraryTag.objects.exclude(name__startswith="Item: ")
			.annotate(num_items=Count('computed_items'))
			.filter(num_items__gt=0, is_item_type=False, is_tag_category=False)
			.order_by('-num_items', 'name')
		)
		return qs


class TagDetailView(ListView):
	model = Item
