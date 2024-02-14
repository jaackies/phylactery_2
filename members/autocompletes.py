from dal import autocomplete
from members.models import Member, RankChoices


class MemberAutocomplete(autocomplete.Select2QuerySetView):
	"""
	Simple view for handling the Member selection box autocompletes.
	See the django-autocomplete-light documentation for more info.
	"""
	def get_queryset(self):
		# Since our list of Members is private information,
		# make sure we are logged in as a Gatekeeper.
		if not (self.request.user.is_authenticated and self.request.user.member.is_gatekeeper()):
			return Member.objects.none()
			
		qs = Member.objects.all()
		if self.q:
			qs = qs.filter(long_name__icontains=self.q)
		return qs
