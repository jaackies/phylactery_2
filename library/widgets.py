from dal_select2_taggit.widgets import TaggitSelect2


class TaggitSelect2NoCreation(TaggitSelect2):
	"""
	Custom widget, which will eventually be used for searching.
	This one prevents the creation of objects.
	"""
	def build_attrs(self, *args, **kwargs):
		attrs = super().build_attrs(*args, **kwargs)
		attrs["data-tags"] = False
		return attrs
