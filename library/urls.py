from django.urls import path
from library.wizards import InternalBorrowItemsWizard

urlpatterns = [
	path("borrow/", InternalBorrowItemsWizard.as_view(), name="borrow"),
]