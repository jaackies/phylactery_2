from django.urls import path
from members.views import FresherMembershipWizard

urlpatterns = [
	path("signup/fresher/", FresherMembershipWizard.as_view())
]