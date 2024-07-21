from members.models import Rank
from django.views.generic import TemplateView


class HomePageView(TemplateView):
	template_name = "pages/home.html"


class AboutPageView(TemplateView):
	template_name = "pages/about.html"


class EventsPageView(TemplateView):
	template_name = "pages/events.html"


class RolePlayingPageView(TemplateView):
	template_name = "pages/role_playing.html"


class LifeMemberView(TemplateView):
	template_name = "pages/life_members.html"
	

class ContactView(TemplateView):
	template_name = "pages/contact.html"


class CommitteeView(TemplateView):
	template_name = "pages/committee.html"
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["committee"] = Rank.objects.get_committee()
		return context
