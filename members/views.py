from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from .forms import MembershipForm, MembershipFormPreview
from blog.models import MailingList


class MembershipWizard(SessionWizardView):
	form_list = [
		("0", MembershipForm,),
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
				if context["preview_data"][f"group_{mailing_list.pk}"] is True:
					context["preview_data"]["mailing_groups"].append(mailing_list.name)
		return context
	
	def done(self, form_list, **kwargs):
		print("Did the thing!")
