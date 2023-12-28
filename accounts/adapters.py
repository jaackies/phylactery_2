from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
	"""
	Custom adapter for AllAuth Social Accounts. This should disable signing up exclusively via Discord.
	"""
	def is_open_for_signup(self, request, sociallogin):
		return False
