from django.urls import path
from members.views import FresherMembershipWizard, StaleMembershipWizard, LegacyMembershipWizard

urlpatterns = [
	path("signup/fresher/", FresherMembershipWizard.as_view()),
	path("signup/stale/<int:pk>/", StaleMembershipWizard.as_view()),
	path("signup/legacy/", LegacyMembershipWizard.as_view())
]