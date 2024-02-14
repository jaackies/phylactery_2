from dal import autocomplete
from library.models import Item, LibraryTag


class ItemAutocomplete(autocomplete.Select2QuerySetView):
	"""
	Simple view for handling the Item selection box autocompletes.
	See the django-autocomplete-light documentation for more info.
	"""
	def get_queryset(self):
		qs = Item.objects.all()
		if self.q:
			# TODO: Add the un-accent Postgres filter.
			qs = qs.filter(name__istartswith=self.q)
		return qs


class LibraryTagAutocomplete(autocomplete.Select2QuerySetView):
	"""
	Simple view for handling the Tag selection box autocompletes.
	See the django-autocomplete-light documentation for more info.
	"""
	def get_queryset(self):
		qs = LibraryTag.objects.all()
		if self.q:
			qs = qs.filter(name__istartswith=self.q)
		return qs
	
	# Weird things happen if you don't override this - you'll end up with a bunch of tags that begin with "Create"
	def get_create_option(self, context, q):
		return []
	