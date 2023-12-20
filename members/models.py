from django.db import models
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
	
	@property
	def is_fresher(self):
		# Simple test - if they joined this year, they are a fresher.
		if self.join_date.year == timezone.now().year:
			return True
		else:
			return False
	
	
	