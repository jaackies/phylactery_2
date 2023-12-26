from django.contrib.auth.models import AbstractUser
from django.db import models


class UnigamesUser(AbstractUser):
	pass
	
	def __str__(self):
		if self.member is None:
			return self.email
		else:
			return self.member.long_name
