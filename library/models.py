from django.db import models
from django.db.models import Q
from taggit.managers import TaggableManager, _TaggableManager
from taggit.models import TagBase, TaggedItemBase


class ItemTaggableManager(_TaggableManager):
	"""
	A custom TaggableManager to help with Library tagging.
	"""
	pass


class LibraryTag(TagBase):
	"""
	A custom tag to implement Tag hierarchies.
	"""
	parents = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="children")
	
	class Meta:
		verbose_name = "Tag"
		verbose_name_plural = "Tags"
	
	def recompute_dependant_items(self):
		"""
		Called when a Tag object is saved.
		Find any Items that have this tag in their base_tags or computed_tags, and re-save them.
		"""
		for item in Item.objects.filter(
				Q(base_tags__in=[self]) | Q(computed_tags__in=[self])
		):
			item.compute_tags(recursion=False)
	
	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		self.recompute_dependant_items()


class BaseTaggedLibraryItem(TaggedItemBase):
	"""
	A custom model to store the Tags for the library system.
	"""
	tag = models.ForeignKey(
		LibraryTag,
		on_delete=models.CASCADE,
		related_name="%(app_label)s_%(class)s_items"
	)
	content_object = models.ForeignKey("Item", on_delete=models.CASCADE)


class ComputedTaggedLibraryItem(TaggedItemBase):
	"""
	A custom model to store the Tags for the library system.
	"""
	tag = models.ForeignKey(
		LibraryTag,
		on_delete=models.CASCADE,
		related_name="%(app_label)s_%(class)s_items"
	)
	content_object = models.ForeignKey("Item", on_delete=models.CASCADE)


class Item(models.Model):
	"""
	Stores all the data related to a single library item.
	"""
	
	# The name and slug of the Item
	name = models.CharField(max_length=100, unique=True)
	slug = models.SlugField(max_length=100)
	
	# These fields are for the description, condition, and other notes.
	description = models.TextField(blank=True)
	condition = models.TextField(blank=True)
	notes = models.TextField(blank=True)
	
	# The tags for the Item. Base tags are the tags manually applied to the item.
	# Computed tags are the ones automatically set due to tag hierarchy.
	# The item_tag field stores a link to the Item's own tag, written in the form of "Item: <self.name>"
	# That tag is automatically created upon saving.
	base_tags = TaggableManager(
		manager=ItemTaggableManager, through=BaseTaggedLibraryItem, blank=True, verbose_name="Base Tags",
		related_name="base_items"
	)
	computed_tags = TaggableManager(
		manager=ItemTaggableManager, through=ComputedTaggedLibraryItem, blank=True, verbose_name="Computed Tags",
		related_name="computed_items"
	)
	item_tag = models.OneToOneField(
		LibraryTag, on_delete=models.SET_NULL, null=True, editable=False, default=None, related_name="item"
	)
	
	# Data for display on the Item's page.
	min_players = models.PositiveIntegerField(blank=True, null=True)
	max_players = models.PositiveIntegerField(blank=True, null=True)
	
	min_play_time = models.PositiveIntegerField(blank=True, null=True, help_text="in minutes")
	max_play_time = models.PositiveIntegerField(blank=True, null=True, help_text="in minutes")
	average_play_time = models.PositiveIntegerField(blank=True, null=True, help_text="in minutes")
	
	# These govern the Item's borrowing behaviour
	is_borrowable = models.BooleanField(default=True)
	is_high_demand = models.BooleanField(default=False)
	
	def get_image_filename(self, filename: str) -> str:
		filename, _, extension = filename.rpartition('.')
		return f"library/item_images/{self.slug}.{extension}"
	
	image = models.ImageField(upload_to=get_image_filename, null=True)
	
	class Meta:
		ordering = ['name']
	
	# Properties
	def __str__(self):
		# The name for the object in the admin interface.
		return self.name
	
	@property
	def all_tags(self):
		# Helper method to return all the item's tags.
		return self.base_tags.all().union(self.computed_tags.all())
	
	@property
	def players_display(self):
		# Returns a string representation of the player count.
		if not (self.min_players or self.max_players):
			# No player count given.
			return ""
		if self.min_players == self.max_players:
			# Exactly N players.
			return f"{self.min_players} player{'s' if self.min_players > 1 else ''}"
		if not self.min_players:
			# There's a max but no minimum.
			return f"1 - {self.max_players} players"
		if not self.max_players:
			# There's a minimum but no max.
			return f"{self.min_players}+ players"
		# The base case
		return f"{self.min_players} - {self.max_players} players"
	
	# Methods
	def save(self, *args, **kwargs):
		# This method is called whenever the Item is saved.
		# Before saving, we calculate the playtime.
		# After saving, we compute the full tags for the Item.
		self.compute_play_time()
		super().save(*args, **kwargs)  # This actually does the saving.
		self.compute_tags()
	
	def compute_play_time(self):
		# Calculates and sets the average play time of the Item.
		# This method is called upon saving the Item.
		if self.average_play_time is None and (self.min_play_time is not None and self.max_play_time is not None):
			# If the average is already set, we don't change anything.
			self.average_play_time = (self.min_play_time + self.max_play_time) // 2
	
	def compute_tags(self, recursion=True):
		# This method is called upon saving the Item or Tag.
		
		# Calculate the items computed tags by finding all parents, until there's none left.
		tags_to_search = set(self.base_tags.all())
		already_searched = set()
		while True:
			tags_to_search -= already_searched
			if len(tags_to_search) == 0:
				break
			already_searched |= tags_to_search
			tags_to_search = set(LibraryTag.objects.filter(children__in=tags_to_search))
		self.computed_tags.set(already_searched, clear=True)
		
		# If the item doesn't have an associated "Item: <>" tag, create it.
		# Then, set its parents to be this item's base tags.
		if self.item_tag is None:
			self.item_tag = LibraryTag.objects.create(name=f"Item: {self.name}")
		else:
			# Make sure the name of the Tag is updated.
			if self.item_tag.name != f"Item: {self.name}":
				self.item_tag.name = f"Item: {self.name}"
		self.item_tag.parents.set(self.base_tags.all())
		
		# Finally, we re-save any items with Tags that depend on this one.
		if recursion:
			self.item_tag.recompute_dependant_items()
