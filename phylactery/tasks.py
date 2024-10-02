from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(name="send_single_mail_task", rate_limit="1/s")
def send_single_email_task(email_address, subject, message, html_message=None, connection=None, log=True):
	"""
		Sends a single email to a single email address asynchronously.
	"""
	logger.info(f"Sending email.\nTo: {email_address}\nSubject: {subject}\nMessage: {message}")