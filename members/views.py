from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.decorators import method_decorator
from formtools.wizard.views import SessionWizardView
from .decorators import gatekeeper_required
from .forms import FresherMembershipForm, StaleMembershipForm, LegacyMembershipForm, MembershipFormPreview
from .models import Member, Membership
from accounts.models import UnigamesUser
from blog.models import MailingList


@method_decorator(gatekeeper_required, name="dispatch")
class FresherMembershipWizard(SessionWizardView):
	"""
	This view handles the Membership form in a "Wizard", which is multiple forms working together in one view.
	This view is used to handle Fresher Memberships - people that haven't signed up to the club before ever.
	"""
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
		"""
		When the form is submitted entirely, we can create the new Member and all relevant details.
		This involves:
			- Creating a new Member object for them.
			- Attaching them to the Mailing Lists they chose.
			- Creating a new Membership object for them.
			- Creating a new User object for them.
		Then, send them a Welcome email.
		"""
		cleaned_data = self.get_all_cleaned_data()
		
		new_user = UnigamesUser.objects.create(
			email=cleaned_data.get("email_address")
		)
		new_user.set_unusable_password()
		new_user.save()
		
		new_member = Member.objects.create(
			short_name=cleaned_data.get("short_name"),
			long_name=cleaned_data.get("long_name"),
			pronouns=cleaned_data.get("pronouns"),
			student_number=cleaned_data.get("student_number"),
			join_date=timezone.now(),
			optional_emails=cleaned_data.get("optional_emails"),
			user=new_user,
		)
		
		new_member.save()
		
		if cleaned_data.get("is_guild") is True:
			amount_paid = 5
		else:
			amount_paid = 7
		
		new_membership = Membership.objects.create(
			member=new_member,
			date_purchased=timezone.now(),
			guild_member=cleaned_data.get("is_guild"),
			amount_paid=amount_paid,
			expired=False,
			authorised_by=self.request.user.get_member
		)
		new_membership.save()
		
		# TODO: Email the new Member with a welcome email.
	
		messages.success(
			self.request,
			f"Membership for { cleaned_data.get('long_name')} was successfully created!"
		)
		
		return redirect("home")


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
