from django.forms import formset_factory
from django.utils.decorators import method_decorator
from formtools.wizard.views import SessionWizardView
from members.decorators import gatekeeper_required

from .forms import SelectLibraryItemsForm, ItemDueDateForm, InternalBorrowerDetailsForm


ItemDueDateFormset = formset_factory(ItemDueDateForm, extra=0)


@method_decorator(gatekeeper_required, name="dispatch")
class InternalBorrowItemsWizard(SessionWizardView):
	"""
	This view handles the borrowing of Library Items in a "wizard", which is
	multiple forms working together in one view.
	"""
	form_list = [
		("0", SelectLibraryItemsForm),
		("1", ItemDueDateFormset),
		("2", InternalBorrowerDetailsForm),
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
	
	def done(self, form_list, **kwargs):
		"""
		When the form is submitted entirely, we create the BorrowingRecords and all related objects.
		This includes:
			- Creating a new BorrowerDetails object
			- Create a new BorrowRecord object for each Item being borrowed.
			- TODO: Email the borrower a receipt.
		"""
		pass
