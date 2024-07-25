

class UserToMemberMiddleware(object):
	"""
	This middleware filters every request, and updates the request to include
	the Unigames member object, if there is one.
	"""

	def __init__(self, get_response):
		self.get_response = get_response
	
	def __call__(self, request):
		if request.user.is_authenticated:
			unigames_member = request.user.get_member
			if unigames_member is not None:
				request.is_unigames_member = True
				request.unigames_member = unigames_member
			else:
				request.is_unigames_member = False
				request.unigames_member = None
		else:
			request.is_unigames_member = False
			request.unigames_member = None
