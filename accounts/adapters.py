from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomRegularAccountAdapter(DefaultAccountAdapter):
	"""
	Custom adapter for AllAuth accounts. This should disable signing up though the website.
	"""
	def is_open_for_signup(self, request):
		return False


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
	"""
	Custom adapter for AllAuth Social Accounts. This should disable signing up exclusively via Discord.
	"""
	def is_open_for_signup(self, request, sociallogin):
		return False
