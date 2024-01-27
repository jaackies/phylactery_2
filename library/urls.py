from django.urls import path
from library.wizards import InternalBorrowItemsWizard
from library.views import ItemDetailView

urlpatterns = [
	path("item/<slug:slug>/", ItemDetailView.as_view()),
	path("borrow/", InternalBorrowItemsWizard.as_view(), name="borrow"),
]