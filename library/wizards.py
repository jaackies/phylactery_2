from django.contrib import messages
from django.forms import formset_factory
from django.utils.decorators import method_decorator
from formtools.wizard.views import SessionWizardView
from members.decorators import gatekeeper_required

from library.forms import SelectLibraryItemsForm, ItemDueDateForm, InternalBorrowerDetailsForm


ItemDueDateFormset = formset_factory(ItemDueDateForm, extra=0)


@method_decorator(gatekeeper_required, name="dispatch")
class InternalBorrowItemsWizard(SessionWizardView):
	"""
	This view handles the borrowing of Library Items in a "wizard", which is
	multiple forms working together in one view.
	"""
	form_list = [
		("select", SelectLibraryItemsForm),
		("due_dates", ItemDueDateFormset),
		("details", InternalBorrowerDetailsForm),
	]
	template_name = "library/library_borrow_wizard.html"
	
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
	
	def get_form_initial(self, step):
		"""
		This method overrides the WizardView method.
		Adds in the initial data to the formset in the second stop, allowing the gatekeeper to modify item due dates.
		"""
		if step == "due_dates":
			cleaned_data = self.get_cleaned_data_for_step("select")
			cleaned_items = cleaned_data["items"]
			initial_form_data = []
			for item in cleaned_items:
				initial_form_data.append({
					"item": item,
					"due_date": item.get_availability_info()["max_due_date"]
				})
			return initial_form_data
		return super().get_form_initial(step)
	
	def process_step(self, form):
		"""
		This method overrides the WizardView method.
		Used to trigger a warning if some (but not all) of the items selected in step 1 are not available.
		"""
		if self.steps.current == "select":
			# Check if there are any rejected items.
			if form.rejected_items:
				messages.error(
					self.request,
					f"The following items are not available at the moment: {', '.join(form.rejected_items)}. "
					"If you think this is incorrect, please contact the Librarian."
				)
			if form.different_due:
				messages.warning(
					self.request,
					"One or more of the below items has a shorter due-date than the default (2 weeks). "
					"They have been highlighted in Yellow. Please verify that this still suits the borrower."
				)
		return super().process_step(form)
	
	def done(self, form_list, **kwargs):
		"""
		When the form is submitted entirely, we create the BorrowingRecords and all related objects.
		This includes:
			- Creating a new BorrowerDetails object
			- Create a new BorrowRecord object for each Item being borrowed.
			- TODO: Email the borrower a receipt.
		"""
		pass
