from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import css_inline

logger = get_task_logger(__name__)
inliner = css_inline.CSSInliner(
	load_remote_stylesheets=False
)


def compose_html_email(template_name, context, request=None):
	"""
		Renders an email template in both html and plaintext.
	"""
	context["protocol"] = "https://"
	context["domain"] = Site.objects.get_current().domain
	
	html_message = render_to_string(template_name, context, request=request)
	# For best HTML email results, CSS has to be put on elements inline.
	html_message = inliner.inline(html_message)
	
	# Process the plaintext version
	context["override_base"] = "phylactery/email_base.txt"
	plaintext_message = render_to_string(template_name, context, request=request)
	# Remove leftover HTML tags from the plaintext message
	plaintext_message = strip_tags(plaintext_message)
	return plaintext_message, html_message


@shared_task(name="send_single_mail_task", rate_limit="1/s")
def send_single_email_task(email_address, subject, message, html_message=None, connection=None, log=True):
	"""
		Sends a single email to a single email address asynchronously.
	"""
	logger.info(f"Sending email.\nTo: {email_address}\nSubject: {subject}\nMessage: {message}")