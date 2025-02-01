import json
from redis import Redis

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger(__name__)


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


def send_operation_notification(roles: str | list[str], message: str, redis_channel_name: str = "discord:operations:ping"):
	"""
	Composes a JSON fragment to send through Redis to the discord bot.
	Roles should be either a string or list of strings containing the roles that should be allowed to be mentioned in the message.
	"""
	if type(roles) is str:
		roles = [roles]
	notification_message = {
		"roles": roles,
		"message": message,
	}
	send_to_discord.delay(
		redis_channel_name=redis_channel_name,
		message=json.dumps(notification_message)
	)


def send_to_minutes(message: str):
	send_to_discord.delay(redis_channel_name="discord:minutes:ping", message=message)


def send_to_news(message: str):
	send_to_discord.delay(redis_channel_name="discord:news:ping", message=message)


def send_to_library(message: str):
	send_to_discord.delay(redis_channel_name="discord:library:ping", message=message)


def send_to_door(message: str):
	send_to_discord.delay(redis_channel_name="discord:door:ping", message=message)


