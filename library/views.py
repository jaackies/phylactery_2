from django.views.generic import DetailView
from django.utils import timezone
from datetime import timedelta
from .models import Item


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
	
