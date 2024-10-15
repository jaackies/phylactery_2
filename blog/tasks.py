from celery import shared_task

from blog.models import EmailOrder


@shared_task(name="send_pending_email_orders_task")
def send_pending_email_orders_task():
	"""
	Scheduled task - every 15 minutes.
	Checks the list of EmailOrders, and sends any that:
		a) Haven't been sent, and
		b) Their BlogPost is published.
	"""
	pass
