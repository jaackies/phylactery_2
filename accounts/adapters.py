from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages

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
	
	def pre_social_login(self, request, sociallogin):
		"""
		By default, AllAuth allows for someone to connect as many accounts as they please.
		Since there wasn't an easy way to disable this, this is my workaround.
		Immediately before the connection is processed, check if they have a Discord account linked already.
		If they do, we disallow the connection by redirecting immediately to the profile view with an error message.
		"""
		if request.user.is_authenticated:
			if SocialAccount.objects.filter(
				user=request.user,
				provider="discord"
			).exists():
				# They have an account already
				messages.error(request, "You already have a Discord account linked.")
				raise ImmediateHttpResponse(redirect("members:my_profile"))
