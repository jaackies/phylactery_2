from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from .forms import MembershipForm1, MembershipForm2


class MembershipWizard(SessionWizardView):
	form_list = [MembershipForm1, MembershipForm2]
	template_name = "members/membership_form.html"
	
	def done(self, form_list, **kwargs):
		print("Did the thing!")
