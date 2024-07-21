from django.utils.text import slugify
from django.shortcuts import reverse
from django.views.generic import TemplateView, FormView
from control_panel.forms import FORM_CLASSES


class ControlPanelListView(TemplateView):
	"""
	This view renders the list of control panel forms that
	the user has access to.
	"""
	template_name = "control_panel/control_panel_list.html"
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		form_list = []
		for form_slug, form_class in FORM_CLASSES.items():
			form_list.append({
				"name": form_class.form_name,
				"description": form_class.form_short_description,
				"slug": form_slug
			})
		context["form_list"] = form_list
		return context
		


class ControlPanelFormView(FormView):
	"""
	This view renders the requested form.
	"""
	template_name = "control_panel/control_panel_form.html"
	
	def get_form_class(self):
		return FORM_CLASSES.get(self.kwargs["slug"])
	
	def form_valid(self, form):
		form.submit(self.request)
		return super().form_valid(form)
	
	def get_success_url(self):
		return reverse("control_panel:list")
