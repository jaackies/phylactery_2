from django.urls import path
from members.wizards import FresherMembershipWizard, StaleMembershipWizard, LegacyMembershipWizard
from members.views import MemberListView

urlpatterns = [
	path("signup/fresher/", FresherMembershipWizard.as_view()),
	path("signup/stale/<int:pk>/", StaleMembershipWizard.as_view()),
	path("signup/legacy/", LegacyMembershipWizard.as_view()),
	path("list/", MemberListView.as_view())
]