from redis import Redis

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger(__name__)

# Gatekeepers Role ID: 459262632113995776
# Committee Role ID: 459262627437346817
# Treasurer Role ID: 612900808580923393
# Secretary Role ID: 612901130438967296
# Librarian Role ID: 612901006203682817


@shared_task(name="send_to_discord")
def send_to_discord(redis_channel_name: str, message: str):
	"""
		The Discord bot is linked to the same Redis instance that
		this website is linked to, and is subscribed to various Redis-channels.
		Publishing a message to one of these Redis-channels will cause the
		Discord bot to relay that message to any linked Discord channels.
	"""
	r = Redis(host=settings.REDIS_HOST, port=6379, decode_responses=True)
	r.publish(redis_channel_name, message)
	r.close()


def send_to_minutes(message: str):
	send_to_discord.delay(redis_channel_name="discord:minutes:ping", message=message)


def send_to_news(message: str):
	send_to_discord.delay(redis_channel_name="discord:news:ping", message=message)


def send_to_operations(message: str):
	send_to_discord.delay(redis_channel_name="discord:operations:ping", message=message)


def send_to_door(message: str):
	send_to_discord.delay(redis_channel_name="discord:door:ping", message=message)
