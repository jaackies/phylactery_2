import datetime

from django.db import models
from django.db.models import Case, When, Value
from django.db.models.functions import Now
from django.utils import timezone

from accounts.models import UnigamesUser


class Member(models.Model):
	"""
	Stores all information about a single Unigames member.
	"""
	
	# Rather than a first name and last name, we track a short name and long name.
	# This is for too many reasons to list here. But it is intentional.
	short_name = models.CharField(max_length=100)
	long_name = models.CharField(max_length=200)
	
	# Members provide their own pronouns. The membership form provides common options, but members can type their own.
	pronouns = models.CharField(max_length=50)
	
	student_number = models.CharField(max_length=10, blank=True)
	email = models.EmailField(unique=True)
	join_date = models.DateField()
	
	# Unigames Committee can use this field to store notes on a particular member.
	notes = models.TextField(blank=True)
	
	# Members can create user accounts linked to their member information.
	user = models.OneToOneField(UnigamesUser, blank=True, null=True, on_delete=models.SET_NULL, related_name="member")
	
	# A simple checkbox that controls globally whether the member is sent optional emails.
	# (they will still receive transactional emails and reminder emails, regardless)
	optional_emails = models.BooleanField(default=True)
	
	# Methods
	def __str__(self):
		return self.short_name
	
	def is_fresher(self):
		# Simple test - if they joined this year, they are a fresher.
		if self.join_date.year == timezone.now().year:
			return True
		else:
			return False
	
	def has_rank(self, *rank_names):
		# Returns True if the member has a non-expired rank with any of the given types.
		# Returns False otherwise.
		return self.ranks.filter(expired=False, rank_name__in=rank_names).exists()
	
	def has_active_membership(self):
		# Returns True if the member has a valid membership.
		return self.memberships.filter(expired=False).exists()
	
	def is_valid_member(self):
		# Returns True if the member has a valid membership (or is a life member) and does not have the excluded rank.
		return (
			(self.has_active_membership() or self.has_rank(RankChoices.LIFEMEMBER))
			and not self.has_rank(RankChoices.EXCLUDED)
		)
	
	# The following are the preferred methods of testing for privileges.
	# Webkeepers get these privileges as well for debugging.
	def is_gatekeeper(self):
		return self.is_valid_member() and self.has_rank(RankChoices.GATEKEEPER, RankChoices.WEBKEEPER)
	
	def is_committee(self):
		return self.is_valid_member() and self.has_rank(RankChoices.COMMITTEE, RankChoices.WEBKEEPER)
	
	def is_exec(self):
		return (
			self.is_valid_member() and
			self.has_rank(
				RankChoices.PRESIDENT,
				RankChoices.VICEPRESIDENT,
				RankChoices.TREASURER,
				RankChoices.SECRETARY,
				RankChoices.LIBRARIAN,
				RankChoices.WEBKEEPER
			)
		)


class Membership(models.Model):
	"""
	Stores information about a single membership purchased for a single member.
	"""
	member = models.ForeignKey("Member", on_delete=models.SET_NULL, null=True, related_name="memberships")
	date_purchased = models.DateField(default=timezone.now)
	guild_member = models.BooleanField()
	amount_paid = models.IntegerField()
	expired = models.BooleanField(default=False)
	authorised_by = models.ForeignKey("Member", on_delete=models.SET_NULL, null=True, related_name="authorised")
	
	def __str__(self):
		return f"Membership: {self.member.long_name} ({self.date_purchased.year})"


class RankChoices(models.TextChoices):
	EXCLUDED = 'EXCLUDED', 'Excluded'
	GATEKEEPER = 'GATEKEEPER', 'Gatekeeper'
	WEBKEEPER = 'WEBKEEPER', 'Webkeeper'
	COMMITTEE = 'COMMITTEE', 'Committee'
	LIFEMEMBER = 'LIFEMEMBER', 'Life Member'
	PRESIDENT = 'PRESIDENT', 'President'
	VICEPRESIDENT = 'VICEPRESIDENT', 'Vice-President'
	TREASURER = 'TREASURER', 'Treasurer'
	SECRETARY = 'SECRETARY', 'Secretary'
	LIBRARIAN = 'LIBRARIAN', 'Librarian'
	FRESHERREP = 'FRESHERREP', 'Fresher-Rep'
	OCM = 'OCM', 'OCM'
	IPP = 'IPP', 'IPP (Immediate Past President)'


class RankManager(models.Manager):
	"""
	Custom manager for ranks - this will annotate all Ranks with an easy to use "expired" field.
	"""
	def get_queryset(self):
		# Annotates the default queryset.
		return super().get_queryset().annotate(expired=Case(
			When(expired_date__lte=Now(), then=Value(True)),
			default=Value(False),
			output_field=models.BooleanField()
		))
	
	# This lets you use Ranks.objects.all_active/all_expired as a shortcut.
	def all_active(self):
		return self.all().filter(expired=False)
	
	def all_expired(self):
		return self.all().filter(expired=True)


class Rank(models.Model):
	"""
	Stores a rank for a Member, for granting permission and such.
	There are currently 13 hard-coded ranks.
	Each rank has an assignment date and expiry date.
	A rank stops granting privileges when current_date >= expiry_date.
	"""
	
	member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="ranks")
	rank_name = models.TextField(max_length=20, choices=RankChoices.choices)
	assigned_date = models.DateField(default=timezone.now)
	expired_date = models.DateField(blank=True, null=True)
	
	# Custom manager to help with quality of life
	objects = RankManager()
	
	def __str__(self):
		return f"Rank: {RankChoices[self.rank_name].label} for {self.member.long_name} {'(EXPIRED)' if self.is_expired else ''}"
	
	@property
	def is_expired(self):
		# A rank is expired if the expiry date <= today
		if self.expired_date is None:
			return False
		elif datetime.date.today() >= self.expired_date:
			return True
		else:
			return False
	
	def set_expired(self):
		# Set the expiry date to today.
		self.expired_date = datetime.date.today()
		self.save()
