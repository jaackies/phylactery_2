from datetime import date, datetime, timedelta
from typing import Any
from django.db import models
from django.db.models import Q, Case, When, Value
from django.db.models.functions import Now
from django.utils import timezone
from taggit.managers import TaggableManager, _TaggableManager
from taggit.models import TagBase, TaggedItemBase


# Misc functions to help with date-related functions
def default_due_date() -> datetime:
	# Returns the default due date. Currently, two weeks from now.
	return timezone.now() + timedelta(weeks=2)


def next_weekday() -> datetime:
	# Returns the next weekday. i.e. If this is called on a Fri, Sat, or Sun, returns the Monday.
	new_date = timezone.now() + timedelta(days=1)
	while new_date.weekday() in {5, 6}:
		new_date += timedelta(days=1)
	return new_date


def tomorrow() -> date:
	# Returns tomorrow's date.
	return (timezone.now() + timedelta(days=1)).date()


def dates_between(from_date: date, to_date: date) -> set[date]:
	# Returns all dates between from_date and to_date, inclusive.
	difference = (to_date - from_date).days + 1
	return {(from_date + timedelta(days=i)) for i in range(difference)}


def get_invalid_dates(borrow_records, reservations) -> set[date]:
	# Given the active borrow_records and active reservations for an item, return all invalid dates.
	invalid_dates = set()
	for record in borrow_records:
		invalid_dates |= dates_between(record.borrowed_datetime.date, record.due_date)
	for reservation in reservations:
		invalid_dates |= dates_between(
			reservation.requested_date_to_borrow - timedelta(days=1),
			reservation.requested_date_to_return
		)
	return invalid_dates


class ReservationStatus(models.TextChoices):
	PENDING = "?", "Pending"
	APPROVED = "A", "Approved"
	DENIED = "X", "Denied"
	COMPLETED = "!", "Completed"


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
	
	def get_availability_info(self) -> dict[str, Any]:
		"""
		All in one method for getting availability information about the item.
		Returns a dict with the following keys:
			max_due_date
				A date object representing the maximum due date for the item (i.e. how long it can be borrowed for.)
			available_to_borrow
				A bool that represents if the item is currently available to long-term borrow, overnight.
			in_clubroom
				An item may not be borrowable, but it might be in the clubroom for you to look at. This bool shows that.
			expected_available_date
				This shows the next date that an item should be available_to_borrow. Returns None if it is already.
		"""
		item_availability_info: dict[str, None | date | bool] = {
			"max_due_date": None,
			"available_to_borrow": None,
			"in_clubroom": None,
			"expected_available_date": None,
		}
		item_active_reservations = self.reservations.filter(active=True).order_by('-requested_date_to_borrow')
		item_active_borrow_records = self.borrow_records.filter(returned=False)
		
		# max_due_date is None if self.is_borrowable is False
		# Otherwise max_due_date is the minimum of:
		# 	- the date (minus 1) of the next active reservation
		# 	- the date of the next week day if self.is_high_demand
		# 	- the result of the default_due_date function
		
		if self.is_borrowable is False:
			item_availability_info["max_due_date"] = None
		else:
			date_candidates = {default_due_date()}
			if self.is_high_demand is True:
				date_candidates.add(next_weekday())
			if item_active_reservations.exists():
				date_candidates.add(item_active_reservations.first().requested_date_to_borrow)
			item_availability_info["max_due_date"] = min(date_candidates).date()
		
		# available_to_borrow is True if ALL of the following are True:
		# - self.is_borrowable is True
		# - No current/active borrow records (that are unreturned) exist for the item.
		# - The max_due_date is at least tomorrow.
		
		borrow_conditions = [
			self.is_borrowable,
			item_active_borrow_records.exists() is False,
			(item_availability_info["max_due_date"] is not None),
			(item_availability_info["max_due_date"] >= tomorrow()),
		]
		item_availability_info["available_to_borrow"] = all(borrow_conditions)
		
		# in_clubroom is True if any of the following are True:
		# - available_to_borrow is True
		# - is_borrowable is False
		# - No current/active borrow records (that are unreturned) exist for the item.
		
		clubroom_conditions = [
			item_availability_info["available_to_borrow"],
			self.is_borrowable is False,
			item_active_borrow_records.exists() is False
		]
		item_availability_info["in_clubroom"] = any(clubroom_conditions)
		
		# expected_available_date is None if the item is already available.
		# Otherwise, we calculate the next date (starting from today) that fits all the following criteria:
		# - It doesn't fall within (inclusive) the borrow_date and due_date of an active borrow record.
		# - It isn't the date before an active reservation of that item.
		# - It doesn't fall within (inclusive) the borrow_date and return_date of an active Reservation.
		
		if item_availability_info["available_to_borrow"] is True:
			item_availability_info["expected_available_date"] = None
		else:
			invalid_dates = get_invalid_dates(item_active_borrow_records, item_active_reservations)
			available_date = timezone.now().date()
			while available_date in invalid_dates:
				available_date += timedelta(days=1)
			item_availability_info["expected_available_date"] = available_date
		
		return item_availability_info


class BorrowerDetails(models.Model):
	"""
	Stores all the borrowers details for one borrowing transaction.
	The same member borrowing again will create a new record here.
	BorrowRecords link to this.
	"""
	
	# Who are the items being borrowed by.
	is_external = models.BooleanField(default=False)
	internal_member = models.ForeignKey("members.Member", blank=True, null=True, on_delete=models.SET_NULL)
	borrower_name = models.CharField(max_length=200, blank=True)
	
	borrower_address = models.TextField()
	borrower_phone = models.CharField(max_length=20)
	
	def save(self, *args, **kwargs):
		if self.is_external is False and self.internal_member is not None:
			self.borrower_name = self.internal_member.long_name
		super().save(*args, **kwargs)
	

class BorrowRecordManager(models.Manager):
	"""
	Custom Manager for Borrow Records. This will annotate all BorrowRecords with an easy to use "returned" field.
	"""
	def get_queryset(self):
		# Annotates the default queryset.
		return super().get_queryset().annotate(
			returned=Case(
				When(returned_datetime__lte=Now(), then=Value(True)),
				default=Value(False),
				output_field=models.BooleanField()
			)
		)
	
	# This lets you use BorrowRecords.objects.all_active/all_returned as a shortcut.
	def all_active(self):
		return self.all().filter(returned=False)
	
	def all_returned(self):
		return self.all().filter(returned=True)


class BorrowRecord(models.Model):
	"""
	Stores all information regarding one particular item being borrowed.
	"""
	# Which item, and who borrowed it?
	item = models.ForeignKey("Item", on_delete=models.CASCADE, related_name="borrow_records")
	borrower = models.ForeignKey("BorrowerDetails", on_delete=models.CASCADE, related_name="borrow_records")
	
	# When was it borrowed?
	borrowed_datetime = models.DateTimeField(default=timezone.now)
	# Who authorised it being borrowed?
	borrow_authorised_by = models.CharField(max_length=200)
	
	# The latest day the item can be returned on before being considered overdue.
	due_date = models.DateField(default=default_due_date)
	
	# When was it returned, and who authorised its return?
	returned_datetime = models.DateTimeField(blank=True, null=True, default=None)
	return_authorised_by = models.CharField(max_length=200)
	
	# Any comments about anything (e.g. Damage) noticed on borrow or return can be documented here.
	comments = models.TextField(blank=True)
	
	# Finally, the Librarian verifies that it is returned.
	verified_returned = models.BooleanField(default=False)
	
	# This is the above custom manager to help with Quality of Life.
	objects = BorrowRecordManager()
	

class Reservation(models.Model):
	"""
	Allows both internal and external entities to request to reserve items, for a later pickup.
	"""
	
	# Details for the requestor
	is_external = models.BooleanField(default=False)
	internal_member = models.ForeignKey("members.Member", blank=True, null=True, on_delete=models.SET_NULL)
	requestor_name = models.CharField(max_length=200, blank=True)
	requestor_email = models.EmailField()
	requestor_phone = models.CharField(max_length=20)
	
	# Which items they've asked for.
	reserved_items = models.ManyToManyField("Item", related_name="reservations")
	
	# When they want to reserve them.
	requested_date_to_borrow = models.DateField()
	requested_date_to_return = models.DateField()
	
	# Any extra details from the requestor can be put in here.
	additional_details = models.TextField(blank=True)
	
	# Automatically set when the reservation is created.
	submitted_datetime = models.DateTimeField(auto_now_add=True)
	
	# All requests are started as Pending
	approval_status = models.CharField(
		max_length=1, choices=ReservationStatus.choices, default=ReservationStatus.PENDING
	)
	
	# The timestamp of the last time the status of the reservation was updated.
	status_update_datetime = models.DateTimeField(auto_now_add=True)
	
	# The librarian can put comments here.
	librarian_comments = models.TextField(blank=True)
	
	# This control whether the reservation is 'active'. Defaults to False. Approval sets this to true.
	# Reservations that are active are taken into account when determining whether an item is borrowable, etc.
	is_active = models.BooleanField(default=False)
	
	# Once the items are borrowed, this links to the borrower details, which in turn links to the items borrowed.
	borrower = models.ForeignKey("BorrowerDetails", on_delete=models.SET_NULL, blank=True, null=True)


class LibraryStrike(models.Model):
	"""
	If a Library-related offense occurs, the Librarian can issue a Library strike to the offending member.
	Accumulating enough strikes prohibits a member from borrowing until the strikes expire.
	"""
	member = models.ForeignKey("members.Member", on_delete=models.CASCADE, related_name="strikes")
	reason = models.TextField()
	is_expired = models.BooleanField(default=False)
