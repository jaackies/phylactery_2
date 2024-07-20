from django.urls import path

from .views import HomePageView, AboutPageView, EventsPageView

urlpatterns = [
	path("", HomePageView.as_view(), name="home"),
	path("about/", AboutPageView.as_view(), name="about"),
	path("events/", EventsPageView.as_view(), name="events")
]
