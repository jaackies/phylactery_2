from django.views.generic import TemplateView, FormView


class ControlPanelListView(TemplateView):
	"""
	This view renders the list of control panel forms that
	the user has access to.
	"""
	template_name = "control_panel/control_panel_list.html"


class ControlPanelFormView(FormView):
	"""
	This view renders the requested form.
	"""
	template_name = "control_panel/control_panel_form.html"
