import json
from accounts.models import UnigamesUser, create_fresh_unigames_user
from library.models import Item, LibraryTag
from members.models import Member, Membership, Rank
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import validate_email
from collections import defaultdict

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
		self.import_members()
	
	def import_members(self):
		"""
		Continuing on from import_initial_library
		Steps:
			1) Import members
				a) Create e member object for them
				b) Create a blank user object for them.
				c) In the event that their email is not valid (ie. a student email) then we don't create a user for them.
				d) TODO: Implement logic in the stale member signup to create missing accounts.
			2) Import memberships
			3) Import rank assignments
			3) Import mailing lists / memberflags
		"""
		
		# Step 1: Import Members
		with open(BASE_PATH / "members.member.json", "r") as json_infile:
			json_objects = json.load(json_infile)
		for member in json_objects:
			self.import_member(pk=member["pk"], fields=member["fields"])
		
		# Step 2: Import Memberships
		with open(BASE_PATH / "members.member.json", "r") as json_infile:
			json_objects = json.load(json_infile)
		for member in json_objects:
			self.import_member(pk=member["pk"], fields=member["fields"])
	
	def import_initial_library(self):
		"""
		Steps:
			1) Import all taggit tags into LibraryTags
			2) Import the TagParents
			3) Add the Item Type tags (afterward, so the PKs don't conflict)
			4) Import the Items
			5) Add the appropriate tags onto Library Items (only base tags)
			6) Save all Items.
			At this point we will need to add Members, so that we can add BorrowRecords.
		"""
		
		# Step 1:  Import all taggit tags into LibraryTags
		with open(BASE_PATH / "taggit.tag.json", "r") as json_infile:
			json_objects = json.load(json_infile)
		for library_tag in json_objects:
			self.import_library_tag(pk=library_tag["pk"], fields=library_tag["fields"])
		
		# Step 2: Import the tag parents
		with open(BASE_PATH / "library.tagparent.json") as json_infile:
			json_objects = json.load(json_infile)
		for tag_parent in json_objects:
			child_tag = LibraryTag.objects.get(pk=tag_parent["fields"]["child_tag"])
			child_tag.parents.set(tag_parent["fields"]["parent_tag"])
			self.stdout.write(f"Setting parents for {child_tag.name}")
		
		# Step 3: Add the Item-type tags.
		self.item_types = {
			"BK": LibraryTag.objects.create(name="Item Type: Book", is_item_type=True),
			"BG": LibraryTag.objects.create(name="Item Type: Board Game", is_item_type=True),
			"CG": LibraryTag.objects.create(name="Item Type: Card Game", is_item_type=True),
			"??": LibraryTag.objects.create(name="Item Type: Other", is_item_type=True),
		}
		
		# Step 4: Import the Items
		with open(BASE_PATH / "library.item.json", "r") as json_infile:
			json_objects = json.load(json_infile)
		for library_item in json_objects:
			self.import_library_item(pk=library_item["pk"], fields=library_item["fields"])
		
		# Step 5: Apply base tags to Items.
		# Because of the previous implementation, we have to look
		# at two files simultaneously to figure out which tags should go where.
		with open(BASE_PATH / "library.itembasetags.json", "r") as json_infile:
			json_objects = json.load(json_infile)
		# Construct a dictionary, mapping the pk of the "item_base_tags" object to the Item itself.
		# (Yes, this system was stupid. In my defense, so was I.)
		item_lookup = {}
		for item_base_tags in json_objects:
			item_lookup[item_base_tags["pk"]] = item_base_tags["fields"]["item"]
		# Now we can continue.
		with open(BASE_PATH / "taggit.taggeditem.json", "r") as json_infile:
			json_objects = json.load(json_infile)
		invalid_content_types = defaultdict(list)
		for tagged_item in json_objects:
			tag_pk = tagged_item["fields"]["tag"]
			content_type = tagged_item["fields"]["content_type"]
			object_id = tagged_item["fields"]["object_id"]
			# The content_type is what matters here. We're looking for 12, and we ignore 13.
			# A tag shouldn't have been tagged to anything else.
			if content_type == 12:
				item = Item.objects.get(pk=item_lookup[object_id])
				tag = LibraryTag.objects.get(pk=tag_pk)
				item.base_tags.add(tag)
				self.stdout.write(f"Tagged {item.name} with {tag.name}")
			elif content_type == 13:
				pass
			else:
				invalid_content_types[content_type].append((tag_pk, content_type, object_id))
		if invalid_content_types:
			self.stdout.write(f"Warning: {invalid_content_types=}")
		
		# Step 6: Save all Items to regenerate all Tag data properly.
		for item in Item.objects.all():
			item.save()
			self.stdout.write(f"Re-saved {item.name}")
	
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
		}
		new_item = Item.objects.create(**item_data)
		new_item.base_tags.add(self.item_types[fields["type"]])
		self.stdout.write(f"Added library.item: {new_item.name}")
	
	def import_member(self, pk, fields):
		member_data = {
			"pk": pk,
			"short_name": fields["preferred_name"],
			"long_name": f'{fields["preferred_name"]} {fields["last_name"]}',
			"pronouns": fields["pronouns"],
			"student_number": fields["student_number"],
			"join_date": fields["join_date"],
			"notes": fields["notes"],
			"optional_emails": fields["receive_emails"]
		}
		email_address = fields["email_address"]
		make_user = True
		try:
			validate_email(email_address)
		except ValidationError:
			make_user = False
		if "@student" in email_address:
			make_user = False
		if UnigamesUser.objects.filter(email=email_address).exists():
			make_user = False
		
		if make_user:
			
			member_data["user"] = create_fresh_unigames_user(email_address)
		else:
			member_data["user"] = None
		
		new_member = Member.objects.create(**member_data)
		self.stdout.write(f"Added members.member: {new_member.long_name}{' - skipped creating user' if make_user is False else ''}")
		
