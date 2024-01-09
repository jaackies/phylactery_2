from django.shortcuts import render
from django.utils.decorators import method_decorator
from formtools.wizard.views import SessionWizardView
from .decorators import gatekeeper_required
from .forms import FresherMembershipForm, StaleMembershipForm, LegacyMembershipForm, MembershipFormPreview
from blog.models import MailingList


@method_decorator(gatekeeper_required, name="dispatch")
class FresherMembershipWizard(SessionWizardView):
	form_list = [
		("0", FresherMembershipForm,),
		("preview", MembershipFormPreview,),
	]
	template_name = "members/membership_form.html"
	
	def render_goto_step(self, *args, **kwargs):
		"""
		This method overrides the WizardView Method.
		When going back a step, it allows the form to validate data that you may have already entered.
		If so, then it saves that data, so that when you return to that step, your data will be safe.
		"""
		form = self.get_form(data=self.request.POST, files=self.request.FILES)
		if form.is_valid():
			self.storage.set_step_data(self.steps.current, self.process_step(form))
			self.storage.set_step_files(self.steps.current, self.process_step_files(form))
		return super().render_goto_step(*args, **kwargs)
	
	def get_context_data(self, form, **kwargs):
		"""
		This method overrides the WizardView Method.
		For the "preview" step, we add the cleaned data from the previous steps
		into the context, so we can render the preview.
		"""
		context = super().get_context_data(form=form, **kwargs)
		if self.steps.current == "preview":
			context["preview_data"] = self.get_all_cleaned_data()
			context["preview_data"]["mailing_lists"] = []
			for mailing_list in MailingList.objects.filter(is_active=True):
				if context["preview_data"][f"mailing_list_{mailing_list.pk}"] is True:
					context["preview_data"]["mailing_lists"].append(mailing_list.name)
		return context
	
	def done(self, form_list, **kwargs):
		print("Did the thing!")


class StaleMembershipWizard(FresherMembershipWizard):
	form_list = [
		("0", StaleMembershipForm,),
		("preview", MembershipFormPreview,),
	]


class LegacyMembershipWizard(FresherMembershipWizard):
	form_list = [
		("0", LegacyMembershipForm,),
		("preview", MembershipFormPreview,),
	]
