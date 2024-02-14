import json
from library.models import Item
from django.conf import settings
from django.core.management.base import BaseCommand

"""
This program will be used to import data from the old website into the new one.

We will skip:
	- admin logentries (possible, but not worth it)
	- auth as a whole (people will need to reset passwords anyway)
	- contenttypes
	- celery stuff as a whole (can be easily re-added afterwards)
	- sessions
	- blog email orders
	
"""

BASE_PATH = settings.BASE_DIR / "pretty_models"


class Command(BaseCommand):
	def handle(self, *args, **options):
		with open(BASE_PATH / "library.item.json", "r") as json_infile:
			library_items = json.load(json_infile)
		for library_item in library_items:
			self.import_library_item(pk=library_item["pk"], fields=library_item["fields"])
	
	def import_library_item(self, pk, fields):
		item_data = {
			"pk": pk,
			"name": fields["name"],
			"slug": fields["slug"],
			"description": fields["description"],
			"condition": fields["condition"],
			"notes": fields["notes"],
			"is_borrowable": fields["is_borrowable"],
			"is_high_demand": fields["high_demand"],
			"min_play_time": fields["min_play_time"],
			"max_play_time": fields["max_play_time"],
			"average_play_time": fields["average_play_time"],
			"image": fields["image"],
			# TODO: Item Type Tag
		}
		new_item = Item.objects.create(**item_data)
		self.stdout.write(f"Added library.item: {new_item.name}")
