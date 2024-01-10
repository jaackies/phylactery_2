from django.views.generic import ListView
from .models import Member


class MemberListView(ListView):
	model = Member
	
	def get_queryset(self):
		qs = Member.objects.all()
		return qs