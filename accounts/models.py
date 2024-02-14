from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractUser
from django.db import models


def create_fresh_unigames_user(email_address):
	"""
	Helper method - creates a new user with the specified email address, sets an unusable password on it, and saves it.
	"""
	new_user = UnigamesUser.objects.create(
		username=email_address,
		email=email_address
	)
	new_user.set_unusable_password()
	new_user.save()
	return new_user


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
	