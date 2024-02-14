import json
from library.models import Item, LibraryTag
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
		self.import_initial_library()
	
	def import_initial_library(self):
		"""
		Steps:
			1) Import all taggit tags into LibraryTags
			2) Import the TagParents
			3) Add the Item Type tags (afterward, so the PKs don't conflict)
			4) Import the Items
			5) Add the appropriate tags onto Library Items (only base tags)
			At this point we will need to add Members, so that we can add BorrowRecords.
		"""
		with open(BASE_PATH / "taggit.tag.json", "r") as json_infile:
			json_objects = json.load(json_infile)
		for library_tag in json_objects:
			self.import_library_tag(pk=library_tag["pk"], fields=library_tag["fields"])
		
		with open(BASE_PATH / "library.item.json", "r") as json_infile:
			json_objects = json.load(json_infile)
		for library_item in json_objects:
			self.import_library_item(pk=library_item["pk"], fields=library_item["fields"])
	
	def import_library_tag(self, pk, fields):
		tag_data = {
			"pk": pk,
			"name": fields["name"],
			"slug": fields["slug"],
		}
		new_tag = LibraryTag.objects.create(**tag_data)
		self.stdout.write(f"Added library.librarytag: {new_tag.name}")
	
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
