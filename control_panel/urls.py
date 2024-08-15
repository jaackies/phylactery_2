from django.urls import path
from control_panel.views import ControlPanelListView, ControlPanelFormView

app_name = "control_panel"
urlpatterns = [
	path("", ControlPanelListView.as_view(), name="list"),
	path("<slug:slug>/", ControlPanelFormView.as_view(), name="form")
]
