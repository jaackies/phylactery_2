from django.urls import path
from members.views import MembershipWizard

urlpatterns = [
	path("signup/", MembershipWizard.as_view())
]