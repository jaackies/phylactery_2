from django.urls import path
from library.autocompletes import ItemAutocomplete, LibraryTagAutocomplete
from library.wizards import InternalBorrowItemsWizard, ReservationBorrowItemsWizard
from library.views import (
	ItemDetailView,
	ItemListView,
	TagListView,
	TagDetailView,
	DashboardView,
	ExternalReservationRequestView,
	InternalReservationRequestView,
	ReservationApprovalView,
	VerifyReturnsView,
	ReservationBorrowView,
	ReturnItemsView,
	LibraryHomeView,
)


app_name = 'library'
urlpatterns = [
	path("dashboard/", DashboardView.as_view(), name="dashboard"),
	path("request/external/", ExternalReservationRequestView.as_view(), name="reservation-external"),
	path("request/internal/", InternalReservationRequestView.as_view(), name="reservation-internal"),
	path("approve/<int:pk>/", ReservationApprovalView.as_view(), name="approve-reservation"),
	path("verify/", VerifyReturnsView.as_view(), name="verify-returns"),
	path("item/<slug:slug>/", ItemDetailView.as_view(), name="item-detail"),
	path("tag/<slug:slug>/", TagDetailView.as_view(), name="tag-detail"),
	path("items/", ItemListView.as_view(), name="item-list"),
	path("tags/", TagListView.as_view(), name="tag-list"),
	path("borrow/", InternalBorrowItemsWizard.as_view(), name="borrow-wizard"),
	path("borrow/reservation/<int:pk>/", ReservationBorrowItemsWizard.as_view(), name="borrow-reservation"),
	path("return/<int:pk>/", ReturnItemsView.as_view(), name="return"),
	path("autocomplete-item", ItemAutocomplete.as_view(), name="autocomplete-item"),
	path("autocomplete-tag", LibraryTagAutocomplete.as_view(), name="autocomplete-tag"),
	path("", LibraryHomeView.as_view(), name="home"),
]