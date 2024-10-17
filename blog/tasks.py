from celery import shared_task

from blog.models import EmailOrder
from phylactery.tasks import render_html_email, send_single_email_task

@shared_task(name="send_pending_email_orders_task")
def send_pending_email_orders_task():
	"""
	Scheduled task - every 15 minutes.
	Checks the list of EmailOrders, and sends any that:
		a) Haven't been sent, and
		b) Their BlogPost is published.
	TODO: Send via Discord as well.
	"""
	
	email_orders = EmailOrder.objects.filter(email_sent=False)
	if email_orders.count() == 0:
		# Nothing to do - stop now
		return False
	
	for order in email_orders:
		if order.is_ready:
			subject = f"{order.blog_post.title} - Unigames News"
			members_to_email_to = order.get_members_to_send_to()
			context = {
				"blogpost": order.post,
			}
			plaintext_message, html_message = render_html_email(
				template_name="blog/email/blog_post.html",
				context=context,
			)
			for member in members_to_email_to:
				send_single_email_task.delay(
					email_address=member.email,
					subject=subject,
					message=plaintext_message,
					html_message=html_message
				)
			order.email_sent = True
			order.save()
