from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView, FormView
from django.utils import timezone
from datetime import timedelta
from library.models import Item, LibraryTag, BorrowerDetails
from library.forms import ExternalReservationRequestForm


class DashboardView(TemplateView):
	template_name = "library/dashboard_view.html"
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["unapproved"] = "UNSET"
		context["to_be_verified"] = "UNSET"
		context["pending"] = BorrowerDetails.objects.filter(completed=False)
		return context


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
	template_name = "library/item_list_view.html"
	context_object_name = "items_list"
	
	def get_queryset(self):
		self.tag = get_object_or_404(LibraryTag, slug=self.kwargs["slug"])
		qs = (
			Item.objects.filter(
				Q(base_tags__in=[self.tag]) | Q(computed_tags__in=[self.tag])
			).distinct()
		)
		return qs

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["page_title"] = f"All items tagged with '{self.tag}':"
		context["parent_tags"] = self.tag.parents.exclude(name__startswith="Item: ")
		context["child_tags"] = self.tag.children.exclude(name__startswith="Item: ")
		return context


class ExternalReservationRequestView(FormView):
	form_class = ExternalReservationRequestForm
	template_name = "library/reservation_form.html"
