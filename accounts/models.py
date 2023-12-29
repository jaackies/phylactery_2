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
