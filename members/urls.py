from django.urls import path
from members.wizards import FresherMembershipWizard, StaleMembershipWizard, LegacyMembershipWizard
from members.views import MemberListView, SignupHubView

urlpatterns = [
	path("signup/fresher/", FresherMembershipWizard.as_view(), name="signup-fresher"),
	path("signup/stale/<int:pk>/", StaleMembershipWizard.as_view(), name="signup-stale"),
	path("signup/legacy/", LegacyMembershipWizard.as_view(), name="signup-legacy"),
	path("signup/", SignupHubView.as_view(), name="signup-hub"),
	path("list/", MemberListView.as_view(), name="list")
]