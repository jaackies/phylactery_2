from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def gatekeeper_required(function=None):
	"""
	Decorator for views - requires a Gatekeeper to be logged in.
	If they are logged in, but not a Gatekeeper, then raise 403.
	Otherwise, redirect them to the login page.
	"""
	
	def gatekeeper_test(u):
		if u.is_authenticated:
			if u.get_member is not None and u.get_member.is_gatekeeper():
				return True
			else:
				raise PermissionDenied
		else:
			return False
		
	actual_decorator = user_passes_test(gatekeeper_test)
	
	if function:
		return actual_decorator(function)
	return actual_decorator


def committee_required(function=None):
	"""
	Decorator for views - requires a Committee Member to be logged in.
	If they are logged in, but not Committee, then raise 403.
	Otherwise, redirect them to the login page.
	"""
	
	def committee_test(u):
		if u.is_authenticated:
			if u.get_member is not None and u.get_member.is_committee():
				return True
			else:
				raise PermissionDenied
		else:
			return False
	
	actual_decorator = user_passes_test(committee_test)
	
	if function:
		return actual_decorator(function)
	return actual_decorator


def exec_required(function=None):
	"""
	Decorator for views - requires an Executive Committee Member to be logged in.
	(Being either President, VP, Treasurer, Secretary, or Librarian)
	If they are logged in, but not Exec, then raise 403.
	Otherwise, redirect them to the login page.
	"""
	
	def exec_test(u):
		if u.is_authenticated:
			if u.get_member is not None and u.get_member.is_exec():
				return True
			else:
				raise PermissionDenied
		else:
			return False
	
	actual_decorator = user_passes_test(exec_test)
	
	if function:
		return actual_decorator(function)
	return actual_decorator
