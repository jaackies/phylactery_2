from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractUser
from django.db import models


class UnigamesUser(AbstractUser):
	pass
	
	def __str__(self):
		try:
			return self.member.long_name
		except ObjectDoesNotExist:
			return self.email
	
	@property
	def get_member(self):
		# Convenience method - returns the Member if there is one.
		# Otherwise, returns None.
		try:
			return self.member
		except ObjectDoesNotExist:
			return None
	