from django.views.generic import TemplateView


class HomePageView(TemplateView):
	template_name = "pages/home.html"


class AboutPageView(TemplateView):
	template_name = "pages/about.html"


class EventsPageView(TemplateView):
	template_name = "pages/events.html"


class RolePlayingPageView(TemplateView):
	template_name = "pages/role_playing.html"


class CommitteeView(TemplateView):
	template_name = "pages/committee.html"
