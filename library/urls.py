from django.urls import path
from library.autocompletes import ItemAutocomplete, LibraryTagAutocomplete
from library.wizards import InternalBorrowItemsWizard
from library.views import (
	ItemDetailView,
	ItemListView,
	TagListView,
	TagDetailView,
	DashboardView,
	ExternalReservationRequestView,
	InternalReservationRequestView
)


app_name = 'library'
urlpatterns = [
	path("dashboard/", DashboardView.as_view(), name="dashboard"),
	path("request/ext/", ExternalReservationRequestView.as_view(), name="reservation-external"),
	path("request/int/", InternalReservationRequestView.as_view(), name="reservation-internal"),
	path("item/<slug:slug>/", ItemDetailView.as_view(), name="item-detail"),
	path("tag/<slug:slug>/", TagDetailView.as_view(), name="tag-detail"),
	path("items/", ItemListView.as_view(), name="item-list"),
	path("tags/", TagListView.as_view(), name="tag-list"),
	path("borrow/", InternalBorrowItemsWizard.as_view(), name="borrow-wizard"),
	path("autocomplete-item", ItemAutocomplete.as_view(), name="autocomplete-item"),
	path("autocomplete-tag", LibraryTagAutocomplete.as_view(), name="autocomplete-tag"),
]